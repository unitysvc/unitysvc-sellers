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

from ..exceptions import APIError
from ..utils import convert_convenience_fields_to_documents

if TYPE_CHECKING:
    from ..client import Client


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
) -> UploadResult:
    """Upload all services, promotions, and service groups under ``data_dir``.

    Args:
        client: A configured :class:`unitysvc_sellers.Client`.
        data_dir: Root of the seller catalog tree.
        dryrun: If True, calls each operation with ``dryrun=True``
            (where supported) and never writes override files.
        upload_services: Walk and upload service bundles.
        upload_promotions: Walk and upsert promotion files.
        upload_groups: Walk and upsert service-group files.
        on_progress: Optional callable invoked with
            ``(kind, status, name, detail)`` after each item is
            processed. ``kind`` is one of ``"service"``,
            ``"promotion"``, ``"group"``; ``status`` is ``"ok"``,
            ``"error"``, or ``"dryrun"``.

    Returns:
        :class:`UploadResult` with per-resource tallies and any errors.
    """
    result = UploadResult()

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

            result.services.success += 1
            _emit(
                "service",
                "dryrun" if dryrun else "ok",
                listing_data.get("name", listing_file.name),
                f"task_id={getattr(response, 'task_id', '?')}",
            )

            # Persist the resulting service_id back to an override file so
            # subsequent uploads target the same service. The backend
            # accepts upload responses in two shapes — a fully-resolved
            # service record (with id/name) or a TaskQueuedResponse (just
            # task_id). We only write the override when we have an id.
            if not dryrun:
                service_id = getattr(response, "service_id", None) or getattr(response, "id", None)
                if service_id:
                    write_override_file(listing_file, {"service_id": str(service_id)})

    # ----- Promotions -------------------------------------------------
    if upload_promotions:
        promo_files = find_files_by_schema(data_dir, "promotion_v1")
        result.promotions.total = len(promo_files)

        for promo_path, _fmt, promo_data in promo_files:
            try:
                payload = _strip_schema(promo_data)
                if dryrun:
                    _emit("promotion", "dryrun", payload.get("name", "?"))
                    result.promotions.success += 1
                    continue
                client.promotions.upsert(payload)
                result.promotions.success += 1
                _emit("promotion", "ok", payload.get("name", "?"))
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
                if dryrun:
                    _emit("group", "dryrun", payload.get("name", "?"))
                    result.groups.success += 1
                    continue
                client.groups.upsert(payload)
                result.groups.success += 1
                _emit("group", "ok", payload.get("name", "?"))
            except APIError as exc:
                result.groups.failed += 1
                result.groups.errors.append({"file": str(group_path), "error": f"{exc.status_code}: {exc}"})
                _emit("group", "error", group_data.get("name", "?"), str(exc))
            except Exception as exc:
                result.groups.failed += 1
                result.groups.errors.append({"file": str(group_path), "error": str(exc)})
                _emit("group", "error", group_data.get("name", "?"), str(exc))

    return result
