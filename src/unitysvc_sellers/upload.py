"""High-level catalog uploader.

Walks a seller's local catalog directory and ships the contents to the
backend by composing the lower-level resource methods exposed on
:class:`unitysvc_sellers.Client`. The directory layout it expects is the
seller convention from ``unitysvc-services-*`` data repositories::

    <data_dir>/
    ├── <provider-name>/
    │   ├── provider.{json,toml}        (provider_v1 schema)
    │   └── services/
    │       └── <service-name>/
    │           ├── offering.{json,toml}    (offering_v1 schema)
    │           └── listing.{json,toml}     (listing_v1 schema)
    ├── promotion-*.{json,toml}              (promotion_v1 schema)
    └── service-group-*.{json,toml}          (service_group_v1 schema)

For each listing file the uploader pairs it with the offering in the
same directory and the provider in the parent ``services/..``,
optionally expands convenience fields (``logo``, ``terms_of_service``)
into ``DocumentData``, and POSTs the bundle to
``/v1/seller/services``. The backend's returned ``service_id`` is
written back to a ``listing.override.{json,toml}`` file so subsequent
uploads update the same service in place.

Promotions and service groups are uploaded via PUT (idempotent upsert
keyed on the ``name`` field).

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

from unitysvc_core.utils import find_files_by_schema, write_override_file

from .exceptions import APIError
from .utils import convert_convenience_fields_to_documents

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
    """Aggregate result of :func:`upload_directory`."""

    services: UploadCounts = field(default_factory=UploadCounts)
    promotions: UploadCounts = field(default_factory=UploadCounts)
    groups: UploadCounts = field(default_factory=UploadCounts)

    @property
    def total_failed(self) -> int:
        return self.services.failed + self.promotions.failed + self.groups.failed


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _strip_schema(payload: dict[str, Any]) -> dict[str, Any]:
    """Drop the ``schema`` discriminator field from a v1 file payload.

    The seller file schemas (``provider_v1``, ``offering_v1``, ...) carry a
    ``schema`` field for local validation, but the API models don't accept
    it. We pop it before sending.
    """
    return {k: v for k, v in payload.items() if k != "schema"}


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
    listing: dict[str, Any] | None = None,
    offering: dict[str, Any] | None = None,
    provider: dict[str, Any] | None = None,
    interface: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Walk ``data`` and inline the content of every ``file_path`` reference.

    Seller catalog files use ``file_path`` to point at on-disk assets —
    code examples, connectivity scripts, README chunks, Jinja2
    templates. The backend's ingest worker expects either
    ``file_content`` (inline bytes) or ``external_url`` (a pre-uploaded
    URL) on each document; it does **not** open arbitrary paths from
    its own filesystem, because the seller's catalog repo isn't
    mounted in the backend container.

    This resolver recursively walks the payload. For every dict entry
    keyed ``file_path``, it:

    1. Resolves the path relative to ``base_path``.
    2. Reads the file (rendering Jinja2 templates with the listing /
       offering / provider / interface context when the name ends in
       ``.j2``).
    3. Sets a sibling ``file_content`` field with the loaded content.
    4. Strips the ``.j2`` suffix from ``file_path`` so the stored
       filename matches what a customer would see.

    This is a port of ``resolve_file_references`` from the legacy
    ``unitysvc-services`` SDK, minus the markdown-attachment extraction
    (which depended on a separate ``/seller/documents/upload-attachment``
    backend endpoint that was removed in the seller-api-codegen-hygiene
    cleanup). Catalogs that embed images or linked files in markdown
    documents via the legacy attachment flow are not supported yet —
    add ``external_url`` on those documents to point at pre-hosted
    assets as a workaround.
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
            # Resolve the path relative to the source file's directory.
            from .utils import render_template_file

            full_path = base_path / value if not Path(value).is_absolute() else Path(value)
            if not full_path.exists():
                raise ValueError(f"File not found: {value}")

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

            # Strip .j2 suffix so the stored filename matches the
            # rendered output (e.g. ``test.py.j2`` -> ``test.py``).
            if full_path.name.endswith(".j2"):
                result[key] = value[:-3]
            else:
                result[key] = value
        else:
            result[key] = value

    return result


def _build_service_payload(listing_file: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Locate the offering and provider files for a listing and load all three.

    Returns ``(provider_data, offering_data, listing_data)`` as plain
    dicts ready to drop into ``ServiceDataInput``.
    """
    from unitysvc_core.utils import load_data_file

    listing_data, _ = load_data_file(listing_file)

    parts = listing_file.parts
    try:
        services_idx = parts.index("services")
        provider_dir = Path(*parts[:services_idx])
    except (ValueError, IndexError) as exc:
        raise ValueError(
            f"Cannot extract provider directory from path: {listing_file}. "
            f"Expected the path to contain '.../<provider>/services/<service>/'."
        ) from exc

    # Find the offering file in the same directory as the listing.
    offering_files = find_files_by_schema(listing_file.parent, "offering_v1")
    if not offering_files:
        raise ValueError(
            f"No offering_v1 file found in {listing_file.parent}. "
            f"Each service directory must contain exactly one offering file."
        )
    if len(offering_files) > 1:
        names = [d.get("name", "?") for _, _, d in offering_files]
        raise ValueError(
            f"Multiple offering_v1 files in {listing_file.parent}: {', '.join(names)}. "
            f"Each service directory must contain exactly one offering file."
        )
    offering_path, _, offering_data = offering_files[0]

    # Default offering name to the directory name (per seller convention).
    if not offering_data.get("name"):
        offering_data["name"] = parts[services_idx + 1]
    if not listing_data.get("name"):
        listing_data["name"] = offering_data["name"]

    # Find the provider file in the parent directory.
    provider_files = find_files_by_schema(provider_dir, "provider_v1")
    if not provider_files:
        raise ValueError(
            f"No provider_v1 file found in {provider_dir}. A provider file must exist in the parent of services/."
        )
    provider_path, _, provider_data = provider_files[0]

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

    # Resolve file_path references — read each referenced file, render
    # Jinja2 templates with the surrounding catalog as context, and
    # inline the content into the payload as ``file_content`` so the
    # backend's ingest worker can store it without touching the
    # seller's filesystem.
    provider_data = _resolve_file_references(
        provider_data,
        provider_path.parent,
        provider=provider_data,
    )
    offering_data = _resolve_file_references(
        offering_data,
        offering_path.parent,
        offering=offering_data,
        provider=provider_data,
    )
    listing_data = _resolve_file_references(
        listing_data,
        listing_file.parent,
        listing=listing_data,
        offering=offering_data,
        provider=provider_data,
    )

    return _strip_schema(provider_data), _strip_schema(offering_data), _strip_schema(listing_data)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def upload_directory(
    client: Client,
    data_dir: Path,
    *,
    dryrun: bool = False,
    upload_services: bool = True,
    upload_promotions: bool = True,
    upload_groups: bool = True,
    on_progress: Any = None,
    task_wait_timeout: float = 600.0,
    task_poll_interval: float = 2.0,
) -> UploadResult:
    """Upload all services, promotions, and service groups under ``data_dir``.

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
        dryrun: If True, calls each operation with ``dryrun=True``
            (where supported) and skips the task-polling step entirely,
            since dryrun runs synchronously on the backend.
        upload_services: Walk and upload service bundles.
        upload_promotions: Walk and upsert promotion files.
        upload_groups: Walk and upsert service-group files.
        on_progress: Optional callable invoked as
            ``on_progress(kind, status, name, detail)``. ``kind`` is
            one of ``"service"``, ``"promotion"``, ``"group"``;
            ``status`` transitions through ``"queued"``, ``"ok"``,
            ``"error"``, ``"dryrun"`` as the upload progresses.
            Services emit ``"queued"`` right after the 202 and then
            either ``"ok"`` or ``"error"`` once the Celery task
            finishes. Promotions and groups emit ``"ok"`` / ``"error"``
            directly since they're synchronous PUTs.
        task_wait_timeout: Seconds to wait for all service tasks to
            reach a terminal state before giving up and marking the
            leftover tasks as failed. Default 10 minutes.
        task_poll_interval: Seconds between ``batch-status`` polls.
            Default 2.

    Returns:
        :class:`UploadResult` with per-resource tallies and any errors.
    """
    result = UploadResult()

    # Map task_id -> (listing_file, listing_data) so we can populate
    # per-service results after polling the batch-status endpoint and
    # so we can still write override files with the right listing path.
    pending_tasks: dict[str, tuple[Path, dict[str, Any]]] = {}

    def _emit(kind: str, status: str, name: str, detail: str = "") -> None:
        if on_progress is not None:
            on_progress(kind, status, name, detail)

    # ----- Services ---------------------------------------------------
    if upload_services:
        listing_files = sorted(p for p, _, _ in find_files_by_schema(data_dir, "listing_v1"))
        result.services.total = len(listing_files)

        for listing_file in listing_files:
            try:
                provider_data, offering_data, listing_data = _build_service_payload(listing_file)
            except Exception as exc:
                result.services.failed += 1
                result.services.errors.append({"file": str(listing_file), "error": str(exc)})
                _emit("service", "error", listing_file.name, str(exc))
                continue

            payload = {
                "provider_data": provider_data,
                "offering_data": offering_data,
                "listing_data": listing_data,
            }

            try:
                response = client.services.upload(payload, dryrun=dryrun)
            except APIError as exc:
                result.services.failed += 1
                result.services.errors.append({"file": str(listing_file), "error": f"{exc.status_code}: {exc}"})
                _emit("service", "error", listing_data.get("name", listing_file.name), str(exc))
                continue

            name = listing_data.get("name", listing_file.name)
            task_id = getattr(response, "task_id", None)

            if dryrun:
                # Dryrun runs synchronously on the backend. Nothing to poll.
                result.services.success += 1
                _emit("service", "dryrun", name)
                continue

            if not task_id:
                # Defensive: if the backend somehow returned 200 with a
                # fully-resolved service (old shape), count it as done
                # and write the override immediately.
                result.services.success += 1
                _emit("service", "ok", name)
                service_id = getattr(response, "service_id", None) or getattr(response, "id", None)
                if service_id:
                    write_override_file(listing_file, {"service_id": str(service_id)})
                continue

            pending_tasks[str(task_id)] = (listing_file, listing_data)
            _emit("service", "queued", name, f"task_id={task_id}")

    # ----- Drain pending service tasks --------------------------------
    if pending_tasks:

        def _poll_progress(done: int, total: int, last_ids: list[str]) -> None:
            # The caller's on_progress is the per-item hook, not a
            # "batch poll tick" hook. We use it to emit terminal
            # outcomes below, not intermediate poll ticks.
            _ = (done, total, last_ids)

        try:
            terminal_states = client.tasks.wait(
                *pending_tasks.keys(),
                timeout=task_wait_timeout,
                poll_interval=task_poll_interval,
                on_update=_poll_progress,
            )
        except APIError as exc:
            # Polling itself blew up — mark every pending task as failed
            # and surface an actionable hint for the common failure modes:
            #
            #   * 404 / 405 → the backend doesn't expose /tasks/
            #     under this base URL. Most likely the seller is pointing
            #     the SDK at a composite deployment (base_url ends in
            #     /seller) that predates the ``Mount tasks router under
            #     /seller`` change (unitysvc PR #702). Tell them to either
            #     update the backend or switch to the dedicated subdomain.
            #   * 401 / 403 → API key is invalid for tasks specifically,
            #     which is unusual — the tasks endpoint uses the same auth
            #     as /services. Probably a key rotation mid-upload.
            #   * 5xx → backend instability; just report the raw error and
            #     let the seller retry.
            diagnostic = _format_polling_error(exc)

            for task_id, (listing_file, listing_data) in pending_tasks.items():
                result.services.failed += 1
                result.services.errors.append(
                    {
                        "file": str(listing_file),
                        "task_id": task_id,
                        "error": diagnostic,
                    }
                )
                _emit(
                    "service",
                    "error",
                    listing_data.get("name", listing_file.name),
                    diagnostic,
                )
            pending_tasks.clear()
        else:
            for task_id, (listing_file, listing_data) in pending_tasks.items():
                status_dict = terminal_states.get(task_id) or {
                    "status": "unknown",
                    "message": "task status not returned",
                }
                name = listing_data.get("name", listing_file.name)
                status_value = status_dict.get("status")

                if status_value == "completed":
                    result.services.success += 1
                    _emit("service", "ok", name, f"task_id={task_id}")
                    # Write override file with service_id from the task result.
                    # The ingest task returns {"service": {"id": "..."}, ...}.
                    task_result = status_dict.get("result") or {}
                    service_id = None
                    if isinstance(task_result, dict):
                        service_data = task_result.get("service") or {}
                        if isinstance(service_data, dict):
                            service_id = service_data.get("id")
                    if service_id:
                        write_override_file(listing_file, {"service_id": str(service_id)})
                else:
                    result.services.failed += 1
                    error_msg = (
                        status_dict.get("error")
                        or status_dict.get("message")
                        or f"task ended in state {status_value!r}"
                    )
                    result.services.errors.append(
                        {
                            "file": str(listing_file),
                            "task_id": task_id,
                            "error": str(error_msg),
                        }
                    )
                    _emit("service", "error", name, str(error_msg))

            pending_tasks.clear()

    # ----- Promotions -------------------------------------------------
    if upload_promotions:
        promo_files = find_files_by_schema(data_dir, "promotion_v1")
        result.promotions.total = len(promo_files)

        for promo_path, _fmt, promo_data in promo_files:
            try:
                payload = _strip_schema(promo_data)
                name = str(payload.get("name", "?"))
                if dryrun:
                    _emit("promotion", "dryrun", name)
                    result.promotions.success += 1
                    continue
                client.promotions.upsert(payload)
                result.promotions.success += 1
                _emit("promotion", "ok", name)
            except APIError as exc:
                result.promotions.failed += 1
                result.promotions.errors.append({"file": str(promo_path), "error": f"{exc.status_code}: {exc}"})
                _emit("promotion", "error", promo_data.get("name", "?"), str(exc))
            except Exception as exc:
                result.promotions.failed += 1
                result.promotions.errors.append({"file": str(promo_path), "error": str(exc)})
                _emit("promotion", "error", promo_data.get("name", "?"), str(exc))

    # ----- Service groups --------------------------------------------
    if upload_groups:
        group_files = find_files_by_schema(data_dir, "service_group_v1")
        result.groups.total = len(group_files)

        for group_path, _fmt, group_data in group_files:
            try:
                payload = _strip_schema(group_data)
                name = str(payload.get("name", "?"))
                if dryrun:
                    _emit("group", "dryrun", name)
                    result.groups.success += 1
                    continue
                client.groups.upsert(payload)
                result.groups.success += 1
                _emit("group", "ok", name)
            except APIError as exc:
                result.groups.failed += 1
                result.groups.errors.append({"file": str(group_path), "error": f"{exc.status_code}: {exc}"})
                _emit("group", "error", group_data.get("name", "?"), str(exc))
            except Exception as exc:
                result.groups.failed += 1
                result.groups.errors.append({"file": str(group_path), "error": str(exc)})
                _emit("group", "error", group_data.get("name", "?"), str(exc))

    return result
