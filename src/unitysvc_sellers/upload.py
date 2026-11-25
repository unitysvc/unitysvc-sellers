"""High-level catalog uploader.

Walks a seller's local catalog directory and ships the contents to the
backend by composing the lower-level resource methods exposed on
:class:`unitysvc_sellers.Client`. The directory layout it expects is the
flat ``specs/`` layout (unitysvc#1263) — one self-contained folder per
service, named by the (namespaced) service name::

    <specs_dir>/
    └── <provider>/<service-name...>/
        ├── provider.{json,toml}
        ├── offering.{json,toml}
        ├── listing.{json,toml}
        └── service.json              (optional: backend service_id)
    promotions/       ← all *.json/*.toml files here are promotions
    groups/           ← all *.json/*.toml files here are service groups

For each listing file the uploader pairs it with the offering and provider
in the *same folder*, optionally expands convenience fields (``logo``,
``terms_of_service``, an offering's ``instance_spec``) into ``DocumentData``, and POSTs the bundle to
``/v1/seller/services``. The backend's returned ``service_id`` is written
to that folder's ``service.json`` so subsequent uploads update the same
service in place.

Promotions and service groups are uploaded via PUT (idempotent upsert
keyed on the ``name`` field).  They are discovered by scanning the
``promotions/`` and ``groups/`` top-level directories directly — every
``*.json`` / ``*.toml`` file under those directories is assumed to be a
promotion or service group, respectively.

This module deliberately ships a minimal subset of the original
``unitysvc-services`` upload pipeline:

* No attachment-bytes upload — all file references must be reachable as
  public URLs (``external_url``) or rendered into the document body
  before upload. The standalone ``/upload-attachment`` endpoint that the
  old CLI used has been removed in the seller-api hygiene branch.
* No draft-status skipping — the backend now applies its own
  publish-readiness checks.
* No concurrency / retry — calls are sequential. Add a wrapper if you
  need parallelism.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .exceptions import APIError, SellerSDKError
from .params_render import (
    discover_system_param_files,
    load_param_data,
    read_service_id_for_param,
    service_name_for_param,
    write_service_id_for_param,
)
from .platform_services import (
    build_platform_service_payload,
    find_platform_service_folders,
    write_member_template_id,
    write_platform_service_id,
)
from .state import (
    KIND_PLATFORM,
    KIND_SERVICE,
    KIND_SYSTEM,
    TEST_PASSED,
    TEST_SKIPPED,
    UploadState,
    canonical_digest,
)
from .utils import (
    MEMBER_SERVICES_DIRNAMES,
    convert_convenience_fields_to_documents,
    find_files_by_pattern,
    load_data_file,
    read_service_data,
    service_name_matches,
    write_service_data,
)

if TYPE_CHECKING:
    from .client import Client


@dataclass
class UploadCounts:
    """Per-resource upload tally."""

    total: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0
    errors: list[dict[str, str]] = field(default_factory=list)


@dataclass
class TestOutcome:
    """The platform's decision on one submitted service, read with ``wait_for_test``.

    ``status`` is ``passed`` (the service became ``active`` or ``review``, or the check run on it again passed),
    ``rejected`` (the tests ran and the platform turned the service down), ``failed`` (the check run on an
    already accepted service failed), ``error`` (the test task failed or could not run) or ``timeout`` (no
    decision in time) or ``skipped`` (not tested on purpose: the service is deprecated or suspended). ``detail``
    is the platform's message for a failure: the failed documents and their errors. It never holds a run's
    environment or script.
    """

    __test__ = False  # not a pytest class

    name: str
    status: str
    detail: str = ""

    @property
    def passed(self) -> bool:
        return self.status == TEST_PASSED

    @property
    def failed(self) -> bool:
        """Not accepted and not left untested on purpose."""
        return self.status not in (TEST_PASSED, TEST_SKIPPED)


@dataclass
class UploadResult:
    services: UploadCounts = field(default_factory=UploadCounts)
    # With ``wait_for_test``: one outcome per service whose submission queued activation tests.
    tests: list[TestOutcome] = field(default_factory=list)
    # Things the run did that are not a per-service outcome (an unusable state file ignored, the target's
    # services not being listed), for the caller to show.
    notes: list[str] = field(default_factory=list)

    @property
    def total_failed(self) -> int:
        return self.services.failed

    @property
    def tests_failed(self) -> int:
        return sum(1 for t in self.tests if t.failed)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sync_sidecar(service_dir: Path, service_record: dict[str, Any]) -> None:
    """Write the canonical service_id into ``<service_dir>/service.json`` after a
    completed ingest.

    For a REVISION the canonical id is ``revision_of`` (the original active
    service), NOT the revision's own ``service_id`` — so the next upload targets
    the same service. When the local sidecar had diverged (a different/stale id),
    the backend resolves by ``(seller, name)`` and returns that ``revision_of``,
    so writing it here self-heals the sidecar. For a non-revision ingest the full
    returned record is persisted as before. An empty record is a no-op.
    """
    if not service_record:
        return
    # ``test_task_id`` is output only (the task of the tests this upload queued); a sidecar is identity.
    service_record = {k: v for k, v in service_record.items() if k != "test_task_id"}
    revision_of = service_record.get("revision_of")
    if revision_of:
        write_service_data(service_dir, {"service_id": str(revision_of)})
    else:
        write_service_data(service_dir, service_record)


def _format_polling_error(exc: APIError) -> str:
    """Translate an APIError raised during task polling into a user-friendly hint.

    The most common failure mode is a 404 / 405 on ``/tasks/`` when the
    seller points ``UNITYSVC_SELLER_API_URL`` at a composite deployment
    (``.../v1/seller``) that predates the commit exposing
    ``/seller/tasks/*``. Generic "404 Not Found" tells them nothing
    useful; an explicit hint saves them a trip to the backend logs.
    """
    status_code = getattr(exc, "status_code", 0)
    if status_code in (404, 405):
        return (
            "task polling endpoint is missing on the backend. This usually "
            "means your backend is on a composite layout (base URL ends in "
            "/v1/seller) that does not yet expose /seller/tasks/*. Either "
            "update the backend to include unitysvc/unitysvc@39da6b97 or "
            "later ('Mount tasks router under /seller'), or switch the SDK "
            "to the dedicated seller subdomain layout by setting "
            "UNITYSVC_SELLER_API_URL to something like "
            "'http://localhost:8000/v1' and running the backend with "
            f"DEPLOYMENT_TYPE=seller. Raw error: {exc}"
        )
    if status_code in (401, 403):
        return (
            "task polling was rejected by the backend with an auth error. "
            "The /tasks/* endpoint uses the same API-key auth as "
            "/services, so this usually indicates a key rotation or a "
            f"misconfigured role context. Raw error: {exc}"
        )
    if status_code >= 500:
        return f"task polling hit a backend error ({status_code}): {exc}"
    return f"task polling failed: {exc}"


def _as_dict(value: Any) -> dict[str, Any]:
    """Coerce generated SDK models and dict responses into plain dicts."""
    if isinstance(value, dict):
        return value
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "additional_properties"):
        return dict(value.additional_properties)
    return {}


def _template_items(response: Any) -> list[dict[str, Any]]:
    payload = _as_dict(response)
    items = payload.get("data") if payload else getattr(response, "data", [])
    return [_as_dict(item) for item in (items or [])]


def _resolve_system_template_id(client: Client, template_ref: str) -> str:
    """Resolve a system template by exact name or unambiguous id/prefix."""
    templates = _template_items(client.templates.list(limit=500))
    exact_name = [item for item in templates if item.get("name") == template_ref]
    if len(exact_name) == 1:
        return str(exact_name[0]["id"])
    if len(exact_name) > 1:
        raise ValueError(f"System template name {template_ref!r} is ambiguous; use the template id.")

    id_matches = [item for item in templates if str(item.get("id", "")).startswith(template_ref)]
    if len(id_matches) == 1:
        return str(id_matches[0]["id"])
    if len(id_matches) > 1:
        raise ValueError(f"System template id prefix {template_ref!r} is ambiguous; use the full template id.")
    raise ValueError(f"System template {template_ref!r} was not found. Run `usvc seller templates list`.")


def _extract_service_id(status_dict: dict[str, Any]) -> str | None:
    task_result = status_dict.get("result") or {}
    if not isinstance(task_result, dict):
        return None
    return task_result.get("revision_of") or task_result.get("service_id")


def _normalize_service_selector(name: str) -> str:
    """Accept service-name selectors and common local ``services/specs`` paths."""
    normalized = name.removeprefix("./")
    specs_marker = "/services/specs/"
    member_prefixes = tuple(f"{d}/" for d in MEMBER_SERVICES_DIRNAMES)
    member_markers = tuple(f"/{d}/" for d in MEMBER_SERVICES_DIRNAMES)
    if normalized.startswith("services/specs/"):
        normalized = normalized[len("services/specs/") :]
    elif normalized.startswith(member_prefixes):
        normalized = normalized.split("/", 1)[1]
    elif normalized.startswith("specs/"):
        normalized = normalized[len("specs/") :]
    elif specs_marker in normalized:
        normalized = normalized.split(specs_marker, 1)[1]
    elif any(marker in normalized for marker in member_markers):
        marker = next(m for m in member_markers if m in normalized)
        normalized = normalized.split(marker, 1)[1]
    if normalized.endswith(".json") and not normalized.endswith(".service.json"):
        normalized = normalized[: -len(".json")]
    return normalized


def _instantiate_system_param_file(
    client: Client,
    param_file: Path,
    *,
    auto_submit: bool,
) -> tuple[str | None, str]:
    data = load_param_data(param_file)
    template_ref = data.get("template")
    if not template_ref:
        raise ValueError(f"{param_file}: system-template param file must include a template name or id.")
    parameters = data.get("parameters") or {}
    if not isinstance(parameters, dict):
        raise ValueError(f"{param_file}: parameters must be a JSON object.")
    service_name = service_name_for_param(param_file)
    template_id = _resolve_system_template_id(client, str(template_ref))
    resp = client.services.create_from_template(
        template_id,
        parameters=parameters,
        name=service_name,
        auto_submit=auto_submit,
        service_id=read_service_id_for_param(param_file),
    )
    return getattr(resp, "task_id", None), service_name


# Content-hash -> object_key for files already uploaded during this process.
# A seller catalog generated from one template ships the SAME code examples and
# connectivity probe for every service: measured on a 100-service catalog, 1646
# document instances collapse to 25 distinct blobs (98.5% duplicates). Object
# keys are content-addressed, so re-uploading identical bytes is a no-op that
# still costs a full round-trip -- and a failed one fails the whole publish.
# Cache positives only: a miss is uploaded, which then makes it a positive.
#
# Markdown is deliberately excluded. ``storage.upload_file`` rewrites local
# image/link references before uploading, and those resolve relative to the
# file's own directory, so two byte-identical .md files in different service
# folders can legitimately upload to different content.
_UPLOADED_OBJECT_KEYS: dict[str, str] = {}


def _upload_file_deduped(client: Any, full_path: Path) -> str:
    """Upload ``full_path`` via ``POST /seller/upload``, once per distinct content."""
    from .storage import ContentHasher
    from .storage import upload_file as _upload_file

    if full_path.suffix.lower() == ".md":
        return str(_upload_file(client, full_path))
    if isinstance(client, ContentHasher):
        # Fingerprinting only: the hash is the key, and the process-wide cache holds real object keys.
        return str(_upload_file(client, full_path))

    digest = hashlib.sha256(full_path.read_bytes()).hexdigest()
    cached = _UPLOADED_OBJECT_KEYS.get(digest)
    if cached is not None:
        return cached
    object_key = str(_upload_file(client, full_path))
    _UPLOADED_OBJECT_KEYS[digest] = object_key
    return object_key


def _resolve_file_references(
    data: dict[str, Any],
    base_path: Path,
    *,
    client: Any | None = None,
    listing: dict[str, Any] | None = None,
    offering: dict[str, Any] | None = None,
    provider: dict[str, Any] | None = None,
    interface: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Walk ``data`` and resolve every ``file_path`` reference.

    Seller catalog files use ``file_path`` to point at on-disk assets —
    code examples, connectivity scripts, README chunks, Jinja2
    templates. The backend's ingest worker expects either
    ``file_content`` (inline text) or ``external_url`` (a pre-uploaded
    S3 URL) on each document.

    Behaviour per file type:

    - **Code-example / connectivity-test templates** (``.j2`` suffix and
      ``category`` is ``code_example`` or ``connectivity_test``): the raw
      template source is inlined as ``file_content`` and the ``.j2``
      suffix is preserved on ``file_path``. The backend renders these
      at consumption time so it can produce different views per render
      context (gateway vs. local probe, customer-inline vs. env-var
      portable, etc.). See unitysvc/unitysvc#877 / #878 for the
      backend-side render plan.
    - **Other Jinja2 templates** (``.j2`` suffix on documents that are
      not code-example / connectivity-test, e.g. README snippets):
      rendered with the surrounding catalog context and inlined as
      ``file_content``. These are static documents with no
      consumption-time render contexts, so client-side expansion stays.
    - **All other files** (when ``client`` is provided): uploaded to S3 via
      ``POST /seller/upload`` and referenced as
      ``external_url: "${UNITYSVC_S3_BASE_URL}/{object_key}"``.  This
      keeps large or binary files out of the ingest payload. For Markdown
      files the uploader also rewrites embedded local image / link
      references before uploading.
    - **All other files** (when ``client`` is ``None``): read from disk and
      inlined as ``file_content`` (legacy / dryrun fallback).
    """
    # Detect AccessInterface-shaped dicts so nested documents pick up
    # the right interface context for template rendering.
    current_interface = interface
    if "base_url" in data or "interface_type" in data:
        current_interface = data

    result: dict[str, Any] = {}

    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = _resolve_file_references(
                value,
                base_path,
                client=client,
                listing=listing,
                offering=offering,
                provider=provider,
                interface=current_interface,
            )
        elif isinstance(value, list):
            processed: list[Any] = []
            for item in value:
                if isinstance(item, dict):
                    processed.append(
                        _resolve_file_references(
                            item,
                            base_path,
                            client=client,
                            listing=listing,
                            offering=offering,
                            provider=provider,
                            interface=current_interface,
                        )
                    )
                else:
                    processed.append(item)
            result[key] = processed
        elif key == "file_path" and isinstance(value, str):
            full_path = base_path / value if not Path(value).is_absolute() else Path(value)
            if not full_path.exists():
                raise ValueError(f"File not found: {value}")

            is_template = full_path.name.endswith(".j2")
            # Code-example and connectivity-test documents are templates
            # that the backend renders at consumption time so that a single
            # source can produce gateway-mode and local-mode views (see
            # unitysvc/unitysvc#877 / #878). Send the raw template instead
            # of expanding it client-side.
            is_backend_rendered = data.get("category") in (
                "code_example",
                "connectivity_test",
            )

            if is_backend_rendered and is_template and client is not None:
                # Still the RAW template -- the backend renders it at
                # consumption time (unitysvc/unitysvc#877 / #878). It just
                # travels by content-addressed S3 key instead of inline, so
                # the identical probe shared by every service in a catalog is
                # uploaded once rather than once per service. The stored
                # Document is byte-identical either way: ``file_content`` is
                # transport only, and ingest hashes it to the same object_key.
                try:
                    object_key = _upload_file_deduped(client._client, full_path)
                except Exception as exc:
                    raise ValueError(f"Failed to upload template '{value}' to S3: {exc}") from exc

                result["external_url"] = f"${{UNITYSVC_S3_BASE_URL}}/{object_key}"
                # Preserve the ``.j2`` suffix so the backend can recognise
                # the document as a renderable template.
                result[key] = full_path.name if Path(value).is_absolute() else value
            elif is_backend_rendered and is_template:
                # No client (dryrun / offline): inline as before.
                try:
                    content = full_path.read_text(encoding="utf-8")
                except Exception as exc:
                    raise ValueError(f"Failed to read template '{value}': {exc}") from exc

                result["file_content"] = content
                result[key] = full_path.name if Path(value).is_absolute() else value
            elif is_template or client is None:
                # Jinja2 template (or no client): render and inline as file_content.
                from .utils import render_template_file

                try:
                    content, actual_filename = render_template_file(
                        full_path,
                        listing=listing,
                        offering=offering,
                        provider=provider,
                        interface=current_interface,
                    )
                except Exception as exc:
                    raise ValueError(f"Failed to load/render file content from '{value}': {exc}") from exc

                result["file_content"] = content
                if Path(value).is_absolute():
                    result[key] = actual_filename
                elif is_template:
                    result[key] = value[:-3]
                else:
                    result[key] = value
            else:
                # Non-template file with an active client: upload to S3.
                try:
                    object_key = _upload_file_deduped(client._client, full_path)
                except Exception as exc:
                    raise ValueError(f"Failed to upload '{value}' to S3: {exc}") from exc

                result["external_url"] = f"${{UNITYSVC_S3_BASE_URL}}/{object_key}"
                result[key] = full_path.name if Path(value).is_absolute() else value
        else:
            result[key] = value

    return result


def _build_service_payload(
    listing_file: Path, *, client: Any | None = None
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    """Locate the offering and provider files for a listing and load all three.

    Returns ``(provider_data, offering_data, listing_data, service_data)``. The
    first three are the authored content that drops into ``ServiceDataInput``;
    ``service_data`` is the backend-assigned identity record (from
    ``service.json``), not listing content, so it is returned separately and
    travels as the upload body's standalone ``service_status`` field — never
    embedded in ``listing_data`` or ``ServiceDataInput``.
    """
    from .utils import load_data_file

    listing_data, _ = load_data_file(listing_file)

    # Flat specs/ layout: provider.json, offering.json and listing.json are all
    # siblings in the one self-contained service folder.
    service_dir = listing_file.parent

    offering_files = find_files_by_pattern(service_dir, "offering_v1")
    if not offering_files:
        raise ValueError(
            f"No offering file found in {service_dir}. "
            f"Each service folder must contain exactly one offering.{{json,toml}}."
        )
    if len(offering_files) > 1:
        names = [str(p) for p, _, _ in offering_files]
        raise ValueError(f"Multiple offering files in {service_dir}: {', '.join(names)}. Keep exactly one.")
    offering_path, _, offering_data = offering_files[0]

    if not listing_data.get("name"):
        listing_data["name"] = offering_data.get("name")

    provider_files = find_files_by_pattern(service_dir, "provider_v1")
    if not provider_files:
        raise ValueError(f"No provider file found in {service_dir}. Each service folder must contain a provider file.")
    provider_path, _, provider_data = provider_files[0]

    # Backend-assigned identity record (service.json) — returned as a separate
    # value so the caller can send it as the upload body's standalone
    # service_status field, which tells the backend to treat the upload as an
    # update/revision rather than a new service. It is identity, not listing
    # content, so it is never merged into listing_data or ServiceDataInput.
    service_data = read_service_data(service_dir)

    # Convenience-field expansion (logo: "./foo.png" -> DocumentData entry).
    provider_data = convert_convenience_fields_to_documents(
        provider_data,
        provider_path.parent,
        logo_field="logo",
        terms_field="terms_of_service",
    )
    offering_data = convert_convenience_fields_to_documents(
        offering_data,
        offering_path.parent,
        logo_field="logo",
        terms_field="terms_of_service",
        # A path flows through file_path resolution below; a URL stays an
        # external_url for the backend to snapshot (it is never downloaded here).
        instance_spec_field="instance_spec",
    )
    listing_data = convert_convenience_fields_to_documents(
        listing_data,
        listing_file.parent,
        logo_field="logo",
        terms_field="terms_of_service",
    )

    # Resolve file_path references: Jinja2 templates are rendered and
    # inlined as file_content; plain files are uploaded to S3 (when
    # client is provided) and referenced via external_url.
    provider_data = _resolve_file_references(
        provider_data,
        provider_path.parent,
        client=client,
        provider=provider_data,
    )
    offering_data = _resolve_file_references(
        offering_data,
        offering_path.parent,
        client=client,
        offering=offering_data,
        provider=provider_data,
    )
    listing_data = _resolve_file_references(
        listing_data,
        listing_file.parent,
        client=client,
        listing=listing_data,
        offering=offering_data,
        provider=provider_data,
    )

    return provider_data, offering_data, listing_data, service_data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def _remote_service_names(client: Client) -> set[str] | None:
    """The names of the services the target holds for this seller, or None when they cannot be listed.

    One paginated listing (about a second for a thousand services). It is how a state file learns that a
    service it remembers is gone from the target (a reset, a deletion): that one is sent again.
    """
    try:
        names: set[str] = set()
        for service in client.services.iter_all(limit=200):
            name = service.get("name") if isinstance(service, dict) else getattr(service, "name", None)
            if name:
                names.add(str(name))
        return names
    except Exception:
        return None


def _service_digest(listing_file: Path) -> tuple[str, str]:
    """``(service name, fingerprint)`` of what ``listing_file``'s service would send, with no request.

    The payload is built exactly as for an upload, with a :class:`~unitysvc_sellers.storage.ContentHasher`
    in place of the client, so every referenced file contributes the hash of its content and nothing is
    uploaded. The fingerprint is over the EXPANDED provider, offering and listing (presets, templates and
    convenience fields resolved); the sidecar (``service.json``) is identity, not content, and is not in it.

    ``time_created`` is left out of the three documents. Rendering a param file fills it in with the current
    time when the template sets none, so it differs on every render while nothing else has changed; the
    repo's own change check (``template_populate._smart_write_json``) ignores it for the same reason. Counting
    it would make every such service look changed on every run.
    """
    from .storage import ContentHasher

    provider_data, offering_data, listing_data, _ = _build_service_payload(listing_file, client=ContentHasher())
    name = str(listing_data.get("name") or listing_file.name)

    def _content(data: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in data.items() if key != "time_created"}

    return name, canonical_digest(
        {
            "provider": _content(provider_data),
            "offering": _content(offering_data),
            "listing": _content(listing_data),
        }
    )


def _ingest_outcome(status_dict: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    """``(outcome, service_id, revision_of)`` from a completed ingest task's result."""
    result = status_dict.get("result")
    record = result if isinstance(result, dict) else {}
    revision_of = record.get("revision_of")
    canonical = revision_of or record.get("service_id")
    outcome = record.get("status")
    return (
        str(outcome) if outcome else None,
        str(canonical) if canonical else None,
        str(revision_of) if revision_of else None,
    )


def _test_outcome(name: str, status_dict: dict[str, Any], timeout: float) -> TestOutcome:
    """The platform's decision from a finished (or unfinished) ``run_service_tests`` task."""
    status = status_dict.get("status")
    if status == "completed":
        record = status_dict.get("result")
        record = record if isinstance(record, dict) else {}
        verdict = str(record.get("status") or "")
        if verdict in ("active", "review"):
            return TestOutcome(name, TEST_PASSED, verdict)
        detail = str(record.get("error") or "") or f"the platform answered {verdict!r}"
        return TestOutcome(name, "rejected" if verdict == "rejected" else "error", detail)
    if status == "failed":
        message = status_dict.get("error") or status_dict.get("message") or "the test task failed"
        return TestOutcome(name, "error", str(message))
    return TestOutcome(name, "timeout", f"no decision from the platform within {int(timeout)} seconds")


def _wait_for_tests(
    client: Client,
    waits: dict[str, str],
    *,
    timeout: float,
    poll_interval: float,
    result: UploadResult,
    state: UploadState | None,
    on_progress: Any,
) -> None:
    """Wait for the activation tests each upload queued (``test_task_id``) and record the verdicts.

    ``waits`` maps a test task id to its service's name. A verdict that is not a pass is kept in the
    state record, so the next run sends that service again instead of skipping it as unchanged.
    """
    try:
        states = client.tasks.wait(*waits.keys(), timeout=timeout, poll_interval=poll_interval)
    except APIError as exc:
        diagnostic = _format_polling_error(exc)
        states = {tid: {"status": "failed", "error": diagnostic} for tid in waits}
    for task_id, name in waits.items():
        outcome = _test_outcome(name, states.get(task_id) or {}, timeout)
        result.tests.append(outcome)
        if state is not None:
            state.record_test(name, status=outcome.status, detail=outcome.detail)
        if on_progress is not None:
            on_progress("test", "ok" if outcome.passed else "error", name, outcome.detail or outcome.status)


def _describe_check(run: Any) -> str:
    """What a failed diagnostic says, from its error messages only (never a run's stdout, stderr or environment)."""
    parts: list[str] = []
    if getattr(run, "reason", None):
        parts.append(str(run.reason))
    elif getattr(run, "outcome", None):
        parts.append(str(run.outcome))
    for row in getattr(run, "results", []) or []:
        if row.status not in ("success", "skipped") and (row.error or row.status):
            title = row.document_title or row.category or "a document"
            parts.append(f"{title}: {row.status}" + (f" ({row.error})" if row.error else ""))
    for link in getattr(run, "links", []) or []:
        if not link.ok:
            parts.append(f"link {getattr(link, 'url', '?')} unreachable")
    return "; ".join(parts) or f"the platform's check answered {getattr(run, 'status', '?')!r}"


# Lifecycle states of a service that is retired on purpose: its check is not run.
_RETIRED = frozenset({"deprecated", "suspended"})


def _lifecycle_status(client: Client, service_id: str) -> str:
    """The platform's status of a service (``active``, ``review``, ``deprecated``, ...)."""
    status = getattr(client.services.get(service_id), "status", None)
    return str(getattr(status, "value", status) or "")


def _retest_one(client: Client, name: str, service_id: str, *, remaining: float, poll_interval: float) -> TestOutcome:
    """The platform's check on one service whose upload queued no tests, or why it was not run."""
    # The upload result does not say what became of the service: deprecating one answers "updated" or
    # "unchanged" like any other change. Only the platform knows, so ask before starting anything.
    try:
        lifecycle = _lifecycle_status(client, service_id)
    except (APIError, SellerSDKError) as exc:
        return TestOutcome(name, "error", f"could not read the service: {exc}")
    if lifecycle in _RETIRED:
        return TestOutcome(name, TEST_SKIPPED, f"the service is {lifecycle}; it was not tested")
    if lifecycle == "rejected":
        return TestOutcome(name, "rejected", "the service is rejected by the platform")
    if lifecycle not in ("active", "review"):
        return TestOutcome(name, "error", f"the service is {lifecycle or 'in an unknown state'}, not accepted")
    if remaining <= 0:
        return TestOutcome(name, "timeout", "no time left to run the platform's check")
    try:
        run = client.services.run_tests(service_id, force=True, timeout=remaining, poll_interval=poll_interval)
    except APIError as exc:
        return TestOutcome(name, "error", f"{exc.status_code}: {exc}")
    if run.passed:
        return TestOutcome(name, TEST_PASSED, "checked again; the service is unchanged")
    # ``run_tests`` returns the last state it saw when its own time runs out, which parses as an unknown result:
    # a diagnostic that never finished is a timeout, not an unexpected answer from the platform.
    if (getattr(run, "raw", None) or {}).get("status") not in ("completed", "failed"):
        return TestOutcome(name, "timeout", f"no decision from the platform within {int(remaining)} seconds")
    if run.status not in ("success", "failure"):
        return TestOutcome(name, "error", _describe_check(run))
    return TestOutcome(name, "failed", _describe_check(run))


def _retest_services(
    client: Client,
    retests: dict[str, str],
    *,
    deadline: float,
    poll_interval: float,
    result: UploadResult,
    state: UploadState | None,
    on_progress: Any,
) -> None:
    """Run the platform's check again on services whose upload queued no tests, and record the verdicts.

    An upload that changes nothing (the service is already accepted with this content) queues no activation
    tests, so there would be nothing to wait for and a service that no longer starts would pass. The check
    that ``services run-tests`` runs (the container is started, its entries fetched, then stopped) is run
    here instead, one service at a time, until ``deadline`` (a ``time.monotonic`` value).
    """
    import time

    for name, service_id in retests.items():
        outcome = _retest_one(
            client, name, service_id, remaining=deadline - time.monotonic(), poll_interval=poll_interval
        )
        result.tests.append(outcome)
        # A retired service has no verdict to remember; one that failed is sent again by the next run.
        if state is not None and outcome.status != TEST_SKIPPED:
            state.record_test(name, status=outcome.status, detail=outcome.detail)
        if on_progress is not None:
            on_progress("test", "error" if outcome.failed else "ok", name, outcome.detail or outcome.status)


def upload_directory(
    client: Client,
    data_dir: Path,
    *,
    on_progress: Any = None,
    task_wait_timeout: float = 600.0,
    task_poll_interval: float = 2.0,
    name: str | None = None,
    auto_submit: bool = False,
    state_path: Path | None = None,
    force: bool = False,
    verify_remote: bool = True,
    wait_for_test: float | None = None,
) -> UploadResult:
    """Upload service bundles under ``data_dir``.

    Services go through an **asynchronous** ingest pipeline: the
    backend ``POST /services`` returns ``202 Accepted`` with a Celery
    task id, and the actual provider/offering/listing writes happen in
    a worker. This helper collects every task id returned from the
    per-service uploads, polls ``POST /tasks/batch-status`` until
    every task reaches a terminal state, and populates the per-service
    pass/fail result based on the real worker outcome — not the
    optimistic 202 response.

    Args:
        client: A configured :class:`unitysvc_sellers.Client`.
        data_dir: Root of the seller catalog tree.
        on_progress: Optional callable invoked as
            ``on_progress(kind, status, name, detail)``. ``kind`` is
            ``"service"``; ``status`` transitions through ``"queued"``,
            ``"ok"``, ``"error"`` as the upload progresses.
        task_wait_timeout: Seconds to wait for all service tasks to
            reach a terminal state before giving up and marking the
            leftover tasks as failed. Default 10 minutes.
        task_poll_interval: Seconds between ``batch-status`` polls.
            Default 2.
        auto_submit: When True, each freshly published service draft is
            also submitted for review (validate → pending → run tests)
            in the same ingest task. When False (default), services are
            left as reviewable drafts to submit later.
        state_path: A state file (:mod:`unitysvc_sellers.state`). When given, a service whose expanded
            content has not changed since its ingest last completed is skipped, its record untouched, and
            the file is rewritten at the end with what this run sent. A missing file is a first run.
        force: With ``state_path``, ignore the records and send everything (the file is still rewritten).
        verify_remote: With ``state_path``, list the target's services once and send again any the state
            remembers but the target no longer has. When the listing fails nothing is skipped.
        wait_for_test: With ``auto_submit``, seconds to wait, after the ingests finish, for the platform's
            decision on each service, put in ``UploadResult.tests``. ``None`` (the default) does not wait. A
            submission queues activation tests, and those are waited for. A service whose upload queued none (the
            content did not change, or a revision was merged without tests) gets the platform's check
            (``services.run_tests``, which starts the container, fetches its entries and stops it) run on it, so
            every service that was sent has a decision.

    Returns:
        :class:`UploadResult` with per-service tallies and any errors.
    """
    result = UploadResult()
    if wait_for_test is not None and not auto_submit:
        raise ValueError("wait_for_test needs auto_submit: only a submitted service has tests to wait for.")
    # test task id -> service name, for the services whose ingest queued activation tests.
    test_waits: dict[str, str] = {}
    # service name -> service id, for the services whose ingest queued none (the content did not change): they
    # get the platform's check run on them again, so a pass is never vacuous.
    retests: dict[str, str] = {}

    state: UploadState | None = None
    remote_names: set[str] | None = None
    # task_id -> (service name, kind, fingerprint): what to record when its ingest task ends.
    pending_state: dict[str, tuple[str, str, str]] = {}
    local_names: set[str] = set()
    names_known = True
    if state_path is not None:
        state, ignored = UploadState.load(state_path, client._base_url)
        if ignored:
            result.notes.append(f"Ignoring the state file {state_path}: {ignored}. Every service is sent.")
        if not force and verify_remote and state.services:
            remote_names = _remote_service_names(client)
            if remote_names is None:
                result.notes.append(
                    "Could not list the target's services to check the state file against; every service is sent."
                )

    def _unchanged(svc_name: str, kind: str, digest: str, sidecar_id: str | None) -> bool:
        """Whether the state says ``svc_name`` need not be sent (and, if so, count and report the skip)."""
        if state is None or force:
            return False
        if verify_remote and state.services and remote_names is None:
            return False
        if remote_names is not None and svc_name not in remote_names:
            return False
        if not state.is_current(svc_name, kind=kind, digest=digest, sidecar_id=sidecar_id, submit=auto_submit):
            return False
        result.services.skipped += 1
        if on_progress is not None:
            on_progress("service", "skipped", svc_name, "unchanged since the last upload")
        return True

    # Map task_id -> (listing_file, listing_data) so we can populate
    # per-service results after polling the batch-status endpoint and
    # write service.json back into the right service folder.
    pending_tasks: dict[str, tuple[Path, dict[str, Any]]] = {}
    pending_system_tasks: dict[str, tuple[Path, str]] = {}
    pending_platform_tasks: dict[str, tuple[Path, str]] = {}

    # ----- Services ---------------------------------------------------
    all_listings = find_files_by_pattern(data_dir, "listing_v1")
    all_system_params = discover_system_param_files(data_dir)
    all_platform_folders = {
        folder: _platform_service_name(folder) for folder in find_platform_service_folders(data_dir)
    }
    if name is not None:
        name = _normalize_service_selector(name)
        # --name uploads every service whose service_name (= listing.name,
        # #1138) matches the fnmatch pattern: a literal name uploads one
        # service, ``cohere/*`` uploads the set.
        matched = [p for p, _, d in all_listings if service_name_matches(d.get("name"), name)]
        matched_system = [p for p in all_system_params if service_name_matches(service_name_for_param(p), name)]
        matched_platform = [f for f, n in all_platform_folders.items() if service_name_matches(n, name)]
        if not matched and not matched_system and not matched_platform:
            raise ValueError(f"No service with service_name (listing.name) matching '{name}' found under {data_dir}.")
        listing_files = sorted(matched)
        system_param_files = sorted(matched_system)
        platform_folders = sorted(matched_platform)
    else:
        listing_files = sorted(p for p, _, _ in all_listings)
        system_param_files = sorted(all_system_params)
        platform_folders = sorted(all_platform_folders)
    result.services.total = len(listing_files) + len(system_param_files) + len(platform_folders)

    # Platform services (#2569): each folder is published with its member
    # template through its own endpoint, never as an ordinary service.
    for folder in platform_folders:
        service_name = all_platform_folders[folder]
        digest: str | None = None
        if state is not None:
            local_names.add(service_name)
            try:
                from .storage import ContentHasher

                digest = canonical_digest(build_platform_service_payload(folder, client=ContentHasher()))
            except Exception:
                digest = None  # the real build below reports why
            if digest is not None and _unchanged(service_name, KIND_PLATFORM, digest, None):
                continue
        try:
            platform_payload = build_platform_service_payload(folder, client=client)
            resp = client.services.upload_platform_service(platform_payload)
        except APIError as exc:
            result.services.failed += 1
            result.services.errors.append({"file": str(folder), "error": f"{exc.status_code}: {exc}"})
            if on_progress is not None:
                on_progress("service", "error", service_name, str(exc))
            if state is not None and digest is not None:
                state.record_failed(
                    service_name, kind=KIND_PLATFORM, digest=digest, submitted=auto_submit, error=str(exc)
                )
            continue
        except Exception as exc:
            result.services.failed += 1
            result.services.errors.append({"file": str(folder), "error": str(exc)})
            if on_progress is not None:
                on_progress("service", "error", service_name, str(exc))
            if state is not None and digest is not None:
                state.record_failed(
                    service_name, kind=KIND_PLATFORM, digest=digest, submitted=auto_submit, error=str(exc)
                )
            continue
        task_id = getattr(resp, "task_id", None)
        if not task_id:
            result.services.failed += 1
            result.services.errors.append({"file": str(folder), "error": "no task id returned"})
            if on_progress is not None:
                on_progress("service", "error", service_name, "no task id returned")
            continue
        pending_platform_tasks[str(task_id)] = (folder, service_name)
        if state is not None and digest is not None:
            pending_state[str(task_id)] = (service_name, KIND_PLATFORM, digest)
        if on_progress is not None:
            on_progress("service", "queued", service_name, f"task_id={task_id}")

    for param_file in system_param_files:
        service_name = service_name_for_param(param_file)
        digest = None
        if state is not None:
            local_names.add(service_name)
            try:
                param_data = load_param_data(param_file)
                digest = canonical_digest(
                    {"template": param_data.get("template"), "parameters": param_data.get("parameters") or {}}
                )
            except Exception:
                digest = None  # the real call below reports why
            if digest is not None and _unchanged(
                service_name, KIND_SYSTEM, digest, read_service_id_for_param(param_file)
            ):
                continue
        try:
            task_id, service_name = _instantiate_system_param_file(
                client,
                param_file,
                auto_submit=auto_submit,
            )
        except APIError as exc:
            result.services.failed += 1
            result.services.errors.append({"file": str(param_file), "error": f"{exc.status_code}: {exc}"})
            if on_progress is not None:
                on_progress("service", "error", service_name, str(exc))
            if state is not None and digest is not None:
                state.record_failed(
                    service_name, kind=KIND_SYSTEM, digest=digest, submitted=auto_submit, error=str(exc)
                )
            continue
        except Exception as exc:
            result.services.failed += 1
            result.services.errors.append({"file": str(param_file), "error": str(exc)})
            if on_progress is not None:
                on_progress("service", "error", service_name, str(exc))
            if state is not None and digest is not None:
                state.record_failed(
                    service_name, kind=KIND_SYSTEM, digest=digest, submitted=auto_submit, error=str(exc)
                )
            continue

        if not task_id:
            result.services.success += 1
            if on_progress is not None:
                on_progress("service", "ok", service_name)
            if state is not None and digest is not None:
                state.record_completed(
                    service_name, kind=KIND_SYSTEM, digest=digest, submitted=auto_submit, outcome=None, service_id=None
                )
            continue

        pending_system_tasks[str(task_id)] = (param_file, service_name)
        if state is not None and digest is not None:
            pending_state[str(task_id)] = (service_name, KIND_SYSTEM, digest)
        if on_progress is not None:
            on_progress("service", "queued", service_name, f"task_id={task_id}")

    for listing_file in listing_files:
        # Upload is NOT gated on the local connectivity probe. The authoritative
        # check is the platform's — ``check_service_tests_passed`` runs on the
        # gateway-side results and blocks review -> active, so a service that
        # cannot serve never reaches customers. Gating here instead deadlocked
        # that check: the gateway-side test needs the service to exist on the
        # platform, so refusing the upload meant a transient local failure (a
        # 429 while probing a catalog back-to-back) permanently prevented the
        # one test that would have proven the service fine.
        digest = None
        state_name: str | None = None
        if state is not None:
            try:
                state_name, digest = _service_digest(listing_file)
                local_names.add(state_name)
            except Exception:
                # The real build below reports why; the catalog's names are not all known, so the
                # records of services that disappeared are kept this run.
                names_known = False
            if digest is not None and state_name is not None:
                sidecar = read_service_data(listing_file.parent) or {}
                sidecar_id = sidecar.get("service_id")
                if _unchanged(state_name, KIND_SERVICE, digest, str(sidecar_id) if sidecar_id else None):
                    continue
        try:
            provider_data, offering_data, listing_data, service_data = _build_service_payload(
                listing_file, client=client
            )
        except Exception as exc:
            result.services.failed += 1
            result.services.errors.append({"file": str(listing_file), "error": str(exc)})
            if on_progress is not None:
                on_progress("service", "error", listing_file.name, str(exc))
            if state is not None and digest is not None and state_name is not None:
                state.record_failed(state_name, kind=KIND_SERVICE, digest=digest, submitted=auto_submit, error=str(exc))
            continue

        payload: dict[str, Any] = {
            "data": {
                "provider_data": provider_data,
                "offering_data": offering_data,
                "listing_data": listing_data,
            }
        }
        if service_data:
            payload["service_status"] = service_data

        try:
            resp = client.services.upload(payload, auto_submit=auto_submit)
        except APIError as exc:
            result.services.failed += 1
            result.services.errors.append({"file": str(listing_file), "error": f"{exc.status_code}: {exc}"})
            if on_progress is not None:
                on_progress("service", "error", listing_data.get("name", listing_file.name), str(exc))
            if state is not None and digest is not None and state_name is not None:
                state.record_failed(state_name, kind=KIND_SERVICE, digest=digest, submitted=auto_submit, error=str(exc))
            continue

        service_name = listing_data.get("name", listing_file.name)
        task_id = getattr(resp, "task_id", None)

        if not task_id:
            # Defensive: if the backend somehow returned 200 with a
            # fully-resolved service (old shape), count it as done
            # and write service.json immediately.
            result.services.success += 1
            if on_progress is not None:
                on_progress("service", "ok", service_name)
            service_id = getattr(resp, "service_id", None) or getattr(resp, "id", None)
            if service_id:
                write_service_data(listing_file.parent, {"service_id": str(service_id)})
            if state is not None and digest is not None and state_name is not None:
                state.record_completed(
                    state_name,
                    kind=KIND_SERVICE,
                    digest=digest,
                    submitted=auto_submit,
                    outcome=None,
                    service_id=str(service_id) if service_id else None,
                )
            continue

        pending_tasks[str(task_id)] = (listing_file, listing_data)
        if state is not None and digest is not None and state_name is not None:
            pending_state[str(task_id)] = (state_name, KIND_SERVICE, digest)
        if on_progress is not None:
            on_progress("service", "queued", service_name, f"task_id={task_id}")

    # ----- Drain pending service tasks --------------------------------
    if pending_tasks or pending_system_tasks or pending_platform_tasks:

        def _poll_progress(done: int, total: int, last_ids: list[str]) -> None:
            _ = (done, total, last_ids)

        try:
            terminal_states = client.tasks.wait(
                *pending_tasks.keys(),
                *pending_system_tasks.keys(),
                *pending_platform_tasks.keys(),
                timeout=task_wait_timeout,
                poll_interval=task_poll_interval,
                on_update=_poll_progress,
            )
        except APIError as exc:
            diagnostic = _format_polling_error(exc)
            for task_id, (listing_file, listing_data) in pending_tasks.items():
                result.services.failed += 1
                result.services.errors.append({"file": str(listing_file), "task_id": task_id, "error": diagnostic})
                if on_progress is not None:
                    on_progress("service", "error", listing_data.get("name", listing_file.name), diagnostic)
            for task_id, (param_file, service_name) in [
                *pending_system_tasks.items(),
                *pending_platform_tasks.items(),
            ]:
                result.services.failed += 1
                result.services.errors.append({"file": str(param_file), "task_id": task_id, "error": diagnostic})
                if on_progress is not None:
                    on_progress("service", "error", service_name, diagnostic)
            if state is not None:
                # Whether the backend ingested them is unknown, so none is remembered as sent.
                for svc_name, kind, digest_ in pending_state.values():
                    state.record_failed(svc_name, kind=kind, digest=digest_, submitted=auto_submit, error=diagnostic)
            pending_tasks.clear()
            pending_system_tasks.clear()
            pending_platform_tasks.clear()
        else:
            for task_id, (listing_file, listing_data) in pending_tasks.items():
                status_dict = terminal_states.get(task_id) or {
                    "status": "unknown",
                    "message": "task status not returned",
                }
                name_val = listing_data.get("name", listing_file.name)
                status_value = status_dict.get("status")

                if status_value == "completed":
                    result.services.success += 1
                    task_result = status_dict.get("result") or {}
                    service_record: dict[str, Any] = task_result if isinstance(task_result, dict) else {}
                    service_id = service_record.get("service_id")
                    revision_of = service_record.get("revision_of")
                    if wait_for_test is not None:
                        if service_record.get("test_task_id"):
                            test_waits[str(service_record["test_task_id"])] = str(name_val)
                        elif service_record.get("status") not in ("deleted", "skipped"):
                            canonical = revision_of or service_id
                            if canonical:
                                retests[str(name_val)] = str(canonical)
                    if revision_of:
                        detail = f"revision_created, service_id={revision_of} (revision={service_id})"
                    else:
                        detail = f"service_id={service_id}" if service_id else f"task_id={task_id}"
                    if on_progress is not None:
                        on_progress("service", "ok", name_val, detail)
                    _sync_sidecar(listing_file.parent, service_record)
                else:
                    result.services.failed += 1
                    error_msg = (
                        status_dict.get("error")
                        or status_dict.get("message")
                        or f"task ended in state {status_value!r}"
                    )
                    result.services.errors.append(
                        {"file": str(listing_file), "task_id": task_id, "error": str(error_msg)}
                    )
                    if on_progress is not None:
                        on_progress("service", "error", name_val, str(error_msg))

            for task_id, (param_file, service_name) in pending_system_tasks.items():
                status_dict = terminal_states.get(task_id) or {
                    "status": "unknown",
                    "message": "task status not returned",
                }
                status_value = status_dict.get("status")
                if status_value == "completed":
                    result.services.success += 1
                    service_id = _extract_service_id(status_dict)
                    system_record = status_dict.get("result")
                    if wait_for_test is not None and isinstance(system_record, dict):
                        if system_record.get("test_task_id"):
                            test_waits[str(system_record["test_task_id"])] = service_name
                        elif service_id:
                            retests[service_name] = str(service_id)
                    if service_id:
                        write_service_id_for_param(param_file, service_id)
                    detail = f"service_id={service_id}" if service_id else f"task_id={task_id}"
                    if on_progress is not None:
                        on_progress("service", "ok", service_name, detail)
                else:
                    result.services.failed += 1
                    error_msg = (
                        status_dict.get("error")
                        or status_dict.get("message")
                        or f"task ended in state {status_value!r}"
                    )
                    result.services.errors.append(
                        {"file": str(param_file), "task_id": task_id, "error": str(error_msg)}
                    )
                    if on_progress is not None:
                        on_progress("service", "error", service_name, str(error_msg))

            for task_id, (folder, service_name) in pending_platform_tasks.items():
                status_dict = terminal_states.get(task_id) or {
                    "status": "unknown",
                    "message": "task status not returned",
                }
                status_value = status_dict.get("status")
                if status_value == "completed":
                    result.services.success += 1
                    record = status_dict.get("result") or {}
                    record = record if isinstance(record, dict) else {}
                    service_id = record.get("service_id")
                    template_id = record.get("member_template_id")
                    if service_id:
                        write_platform_service_id(folder, str(service_id))
                    if template_id:
                        write_member_template_id(folder, str(template_id))
                    detail = (
                        f"{record.get('status', 'done')}, service_id={service_id}, "
                        f"member template {record.get('member_template', 'done')}"
                    )
                    if on_progress is not None:
                        on_progress("service", "ok", service_name, detail)
                else:
                    result.services.failed += 1
                    error_msg = (
                        status_dict.get("error")
                        or status_dict.get("message")
                        or f"task ended in state {status_value!r}"
                    )
                    result.services.errors.append({"file": str(folder), "task_id": task_id, "error": str(error_msg)})
                    if on_progress is not None:
                        on_progress("service", "error", service_name, str(error_msg))

            if state is not None:
                for task_id, (svc_name, kind, digest_) in pending_state.items():
                    status_dict = terminal_states.get(task_id) or {}
                    if status_dict.get("status") == "completed":
                        outcome, canonical_id, revision_of = _ingest_outcome(status_dict)
                        state.record_completed(
                            svc_name,
                            kind=kind,
                            digest=digest_,
                            submitted=auto_submit,
                            outcome=outcome,
                            service_id=canonical_id,
                            revision_of=revision_of,
                        )
                    else:
                        error_msg = (
                            status_dict.get("error")
                            or status_dict.get("message")
                            or f"task ended in state {status_dict.get('status')!r}"
                        )
                        state.record_failed(
                            svc_name, kind=kind, digest=digest_, submitted=auto_submit, error=str(error_msg)
                        )

            pending_tasks.clear()
            pending_system_tasks.clear()
            pending_platform_tasks.clear()

    if wait_for_test is not None and (test_waits or retests):
        import time

        deadline = time.monotonic() + wait_for_test
        if test_waits:
            _wait_for_tests(
                client,
                test_waits,
                timeout=wait_for_test,
                poll_interval=task_poll_interval,
                result=result,
                state=state,
                on_progress=on_progress,
            )
        if retests:
            _retest_services(
                client,
                retests,
                deadline=deadline,
                poll_interval=task_poll_interval,
                result=result,
                state=state,
                on_progress=on_progress,
            )

    if state is not None and state_path is not None:
        # A selector uploads a subset: the records of the rest stay. A full run also forgets services that
        # left the catalog (unless some spec could not be read, so not every name is known).
        if name is None and names_known:
            state.prune(local_names)
        counts = result.services
        state.summary = {
            "total": counts.total,
            "sent": counts.success + counts.failed,
            "skipped": counts.skipped,
            "failed": counts.failed,
        }
        state.save(state_path)

    return result


def _platform_service_name(folder: Path) -> str:
    """The platform service's name: its listing's ``name``, else ``<provider>/<name>``."""
    for suffix in (".json", ".toml"):
        listing = folder / f"listing{suffix}"
        if listing.is_file():
            try:
                data, _ = load_data_file(listing)
            except Exception:
                break
            if isinstance(data, dict) and data.get("name"):
                return str(data["name"])
            break
    return f"{folder.parent.name}/{folder.name}"


def upload_promotions(
    client: Client,
    data_dir: Path,
    *,
    on_progress: Any = None,
) -> UploadCounts:
    """Upload all promotion files from ``data_dir/promotions/``.

    Every ``*.json`` / ``*.toml`` under ``promotions/`` is upserted
    via ``client.promotions.upsert`` (synchronous PUT, idempotent on
    the ``name`` field).
    """
    result = UploadCounts()
    promo_dir = data_dir / "promotions"
    promo_files: list[tuple[Path, dict[str, Any]]] = []
    if promo_dir.is_dir():
        for f in sorted(promo_dir.glob("*.json")):
            promo_files.append((f, load_data_file(f)[0]))
        for f in sorted(promo_dir.glob("*.toml")):
            promo_files.append((f, load_data_file(f)[0]))
    result.total = len(promo_files)

    for promo_path, promo_data in promo_files:
        try:
            payload = promo_data
            name = str(payload.get("name", "?"))
            client.promotions.upsert(payload)
            result.success += 1
            if on_progress is not None:
                on_progress("promotion", "ok", name)
        except APIError as exc:
            result.failed += 1
            result.errors.append({"file": str(promo_path), "error": f"{exc.status_code}: {exc}"})
            if on_progress is not None:
                on_progress("promotion", "error", promo_data.get("name", "?"), str(exc))
        except Exception as exc:
            result.failed += 1
            result.errors.append({"file": str(promo_path), "error": str(exc)})
            if on_progress is not None:
                on_progress("promotion", "error", promo_data.get("name", "?"), str(exc))

    return result


def upload_groups(
    client: Client,
    data_dir: Path,
    *,
    on_progress: Any = None,
) -> UploadCounts:
    """Upload all service-group files from ``data_dir/groups/``.

    Every ``*.json`` / ``*.toml`` under ``groups/`` is upserted via
    ``client.groups.upsert`` (synchronous PUT, idempotent on the
    ``name`` field).
    """
    result = UploadCounts()
    group_dir = data_dir / "groups"
    group_files: list[tuple[Path, dict[str, Any]]] = []
    if group_dir.is_dir():
        for f in sorted(group_dir.glob("*.json")):
            group_files.append((f, load_data_file(f)[0]))
        for f in sorted(group_dir.glob("*.toml")):
            group_files.append((f, load_data_file(f)[0]))
    result.total = len(group_files)

    for group_path, group_data in group_files:
        try:
            payload = group_data
            name = str(payload.get("name", "?"))
            client.groups.upsert(payload)
            result.success += 1
            if on_progress is not None:
                on_progress("group", "ok", name)
        except APIError as exc:
            result.failed += 1
            result.errors.append({"file": str(group_path), "error": f"{exc.status_code}: {exc}"})
            if on_progress is not None:
                on_progress("group", "error", group_data.get("name", "?"), str(exc))
        except Exception as exc:
            result.failed += 1
            result.errors.append({"file": str(group_path), "error": str(exc)})
            if on_progress is not None:
                on_progress("group", "error", group_data.get("name", "?"), str(exc))

    return result
