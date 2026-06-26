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
``terms_of_service``) into ``DocumentData``, and POSTs the bundle to
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

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .exceptions import APIError
from .utils import (
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
    errors: list[dict[str, str]] = field(default_factory=list)


@dataclass
class UploadResult:
    services: UploadCounts = field(default_factory=UploadCounts)

    @property
    def total_failed(self) -> int:
        return self.services.failed


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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

            if is_backend_rendered and is_template:
                try:
                    content = full_path.read_text(encoding="utf-8")
                except Exception as exc:
                    raise ValueError(f"Failed to read template '{value}': {exc}") from exc

                result["file_content"] = content
                # Preserve the ``.j2`` suffix so the backend can recognise
                # the document as a renderable template.
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
                from .storage import upload_file as _upload_file

                try:
                    object_key = _upload_file(client._client, full_path)
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
def upload_directory(
    client: Client,
    data_dir: Path,
    *,
    on_progress: Any = None,
    task_wait_timeout: float = 600.0,
    task_poll_interval: float = 2.0,
    name: str | None = None,
    auto_submit: bool = False,
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

    Returns:
        :class:`UploadResult` with per-service tallies and any errors.
    """
    result = UploadResult()

    # Map task_id -> (listing_file, listing_data) so we can populate
    # per-service results after polling the batch-status endpoint and
    # write service.json back into the right service folder.
    pending_tasks: dict[str, tuple[Path, dict[str, Any]]] = {}

    # ----- Services ---------------------------------------------------
    all_listings = find_files_by_pattern(data_dir, "listing_v1")
    if name is not None:
        # --name uploads every service whose service_name (= listing.name,
        # #1138) matches the fnmatch pattern: a literal name uploads one
        # service, ``cohere/*`` uploads the set.
        matched = [p for p, _, d in all_listings if service_name_matches(d.get("name"), name)]
        if not matched:
            raise ValueError(
                f"No service with service_name (listing.name) matching '{name}' found under {data_dir}."
            )
        listing_files = sorted(matched)
    else:
        listing_files = sorted(p for p, _, _ in all_listings)
    result.services.total = len(listing_files)

    for listing_file in listing_files:
        try:
            provider_data, offering_data, listing_data, service_data = _build_service_payload(
                listing_file, client=client
            )
        except Exception as exc:
            result.services.failed += 1
            result.services.errors.append({"file": str(listing_file), "error": str(exc)})
            if on_progress is not None:
                on_progress("service", "error", listing_file.name, str(exc))
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
            continue

        pending_tasks[str(task_id)] = (listing_file, listing_data)
        if on_progress is not None:
            on_progress("service", "queued", service_name, f"task_id={task_id}")

    # ----- Drain pending service tasks --------------------------------
    if pending_tasks:

        def _poll_progress(done: int, total: int, last_ids: list[str]) -> None:
            _ = (done, total, last_ids)

        try:
            terminal_states = client.tasks.wait(
                *pending_tasks.keys(),
                timeout=task_wait_timeout,
                poll_interval=task_poll_interval,
                on_update=_poll_progress,
            )
        except APIError as exc:
            diagnostic = _format_polling_error(exc)
            for task_id, (listing_file, listing_data) in pending_tasks.items():
                result.services.failed += 1
                result.services.errors.append(
                    {"file": str(listing_file), "task_id": task_id, "error": diagnostic}
                )
                if on_progress is not None:
                    on_progress("service", "error", listing_data.get("name", listing_file.name), diagnostic)
            pending_tasks.clear()
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
                    if revision_of:
                        detail = f"revision_created, service_id={revision_of} (revision={service_id})"
                        if on_progress is not None:
                            on_progress("service", "ok", name_val, detail)
                    else:
                        detail = f"service_id={service_id}" if service_id else f"task_id={task_id}"
                        if on_progress is not None:
                            on_progress("service", "ok", name_val, detail)
                        if service_record:
                            write_service_data(listing_file.parent, service_record)
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

            pending_tasks.clear()

    return result


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
