"""
Template-based service population utilities.

This module provides utilities for populating services using Jinja2 templates
instead of the DataBuilder APIs. This approach separates data from structure.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader

if TYPE_CHECKING:
    pass


def populate_from_iterator(
    iterator: Iterator[dict],
    templates_dir: str | Path,
    output_dir: str | Path,
    offering_template: str = "offering.json.j2",
    listing_template: str = "listing.json.j2",
    name_field: str = "name",
    filter_func: Callable[[dict], bool] | None = None,
    dry_run: bool = False,
    deprecate_missing: bool = True,
    provider_template: str = "provider.json",
) -> dict:
    """
    Populate services from an iterator of model dictionaries.

    Renders Jinja2 templates with each dictionary from the iterator and writes
    the resulting ``offering.json`` + ``listing.json`` into a self-contained
    service folder under the flat ``specs/`` layout (#1263). When the templates
    directory holds a static ``provider.json`` it is copied into every folder
    too, so each service folder is independently valid.

    The folder path is the service name verbatim — ``/`` is preserved, so a
    name like ``deepseek/some-model`` nests as ``output_dir/deepseek/some-model``
    and matches the service's ``listing.name``. Only filesystem-hostile
    characters (``:``) are sanitised.

    Args:
        iterator: Yields dicts with template variables. Must include `name_field`.
        templates_dir: Directory containing .j2 templates (and optional provider.json).
        output_dir: Directory to write services (creates {name}/ subdirs, nested).
        offering_template: Filename of offering template (default: offering.json.j2).
        listing_template: Filename of listing template (default: listing.json.j2).
        name_field: Dict key to use for the folder path (default: "name").
        filter_func: Optional function that takes a model dict and returns True to
            include it, False to skip. Useful for filtering without modifying iterator.
        dry_run: If True, don't write files, just report what would happen.
        deprecate_missing: If True (default), mark services that exist locally but
            are no longer in the iterator as deprecated (sets status="deprecated").
        provider_template: Filename of the static provider definition copied into
            each service folder (default: provider.json). Skipped if absent.

    Returns:
        Stats dict: {"total": N, "written": N, "skipped": N, "filtered": N, "errors": N, "deprecated": N}

    Example:
        >>> def iter_models():
        ...     yield {"name": "acme/model-1", "service_type": "llm", ...}
        ...     yield {"name": "acme/model-2", "service_type": "llm", ...}
        >>> populate_from_iterator(iter_models(), "templates", "specs")
    """
    templates_dir = Path(templates_dir)
    output_dir = Path(output_dir)

    # Load the static provider definition once (copied into every folder so each
    # service folder is self-contained). Absent -> skip provider writes.
    provider_data: dict | None = None
    provider_path = templates_dir / provider_template
    if provider_path.exists():
        try:
            provider_data = json.loads(provider_path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"  Warning: could not read {provider_path.name}: {e}")

    # Track existing services before iteration (for deprecation). Folders nest
    # arbitrarily deep, so key each by its path relative to output_dir.
    existing_services: set[str] = set()
    if deprecate_missing and output_dir.exists():
        existing_services = {
            offering.parent.relative_to(output_dir).as_posix() for offering in output_dir.rglob("offering.json")
        }

    updated_services: set[str] = set()

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )

    # Load templates
    offering_tpl = env.get_template(offering_template)
    listing_tpl = env.get_template(listing_template)

    stats = {"total": 0, "written": 0, "skipped": 0, "filtered": 0, "errors": 0, "deprecated": 0}

    for model_data in iterator:
        stats["total"] += 1

        # Get service name for directory
        service_name = model_data.get(name_field)
        if not service_name:
            print(f"  Warning: Missing '{name_field}' field, skipping")
            stats["errors"] += 1
            continue

        # Apply filter if provided
        if filter_func is not None and not filter_func(model_data):
            stats["filtered"] += 1
            continue

        # Folder path = sanitised service name (nesting preserved)
        dir_name = _sanitize_dirname(service_name)
        service_dir = output_dir / dir_name

        # Track this service as updated (for deprecation logic)
        updated_services.add(dir_name)

        try:
            # Render templates
            offering_json = offering_tpl.render(**model_data)
            listing_json = listing_tpl.render(**model_data)

            # Parse to validate JSON and normalize formatting
            offering_data = json.loads(offering_json)
            listing_data = json.loads(listing_json)

            if dry_run:
                print(f"  Would write: {dir_name}/")
                stats["written"] += 1
                continue

            # Create directory
            service_dir.mkdir(parents=True, exist_ok=True)

            # Smart write (skip if unchanged, preserve time_created)
            offering_written = _smart_write_json(
                service_dir / "offering.json",
                offering_data,
            )
            listing_written = _smart_write_json(
                service_dir / "listing.json",
                listing_data,
            )
            # Copy the static provider definition in (own time_created preserved).
            if provider_data is not None:
                _smart_write_json(service_dir / "provider.json", dict(provider_data))

            if offering_written or listing_written:
                stats["written"] += 1
            else:
                stats["skipped"] += 1

        except json.JSONDecodeError as e:
            print(f"  Error: Invalid JSON for {service_name}: {e}")
            stats["errors"] += 1
        except Exception as e:
            print(f"  Error processing {service_name}: {e}")
            stats["errors"] += 1

    # Deprecate services no longer in upstream
    if deprecate_missing and not dry_run:
        missing_services = existing_services - updated_services
        for service_name in sorted(missing_services):
            service_dir = output_dir / service_name
            if _deprecate_service(service_dir):
                stats["deprecated"] += 1
                print(f"  Deprecated: {service_name}")

    print(
        f"\nDone! Total: {stats['total']}, Written: {stats['written']}, "
        f"Skipped: {stats['skipped']}, Filtered: {stats['filtered']}, "
        f"Errors: {stats['errors']}, Deprecated: {stats['deprecated']}"
    )

    return stats


def _sanitize_dirname(name: str) -> str:
    """Convert a service name to a folder path, preserving ``/`` nesting.

    Only filesystem-hostile characters are replaced; ``/`` is kept so
    ``org/model`` names nest naturally and the folder path equals the
    service's ``listing.name``.
    """
    return name.strip("/").replace(":", "_")


def _smart_write_json(path: Path, data: dict) -> bool:
    """
    Write JSON file only if content changed (ignoring time_created).

    Preserves original time_created if file exists and content is different.
    Adds time_created if not present.

    Returns:
        True if file was written, False if skipped (unchanged).
    """
    path = Path(path)

    # Check existing file
    if path.exists():
        try:
            existing = json.loads(path.read_text())

            # Compare without time_created
            existing_cmp = {k: v for k, v in existing.items() if k != "time_created"}
            new_cmp = {k: v for k, v in data.items() if k != "time_created"}

            if existing_cmp == new_cmp:
                return False  # No changes

            # Preserve original time_created
            if "time_created" in existing:
                data["time_created"] = existing["time_created"]

        except (json.JSONDecodeError, OSError):
            pass

    # Add time_created if not present
    if "time_created" not in data:
        data["time_created"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    # Write file with consistent formatting (sorted keys for deterministic output)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return True


def _deprecate_service(service_dir: Path) -> bool:
    """
    Mark a service as deprecated by setting ``status="deprecated"`` on both its
    ``offering.json`` and ``listing.json`` (whichever exist).

    Args:
        service_dir: Path to the service directory.

    Returns:
        True if any file was newly deprecated, False if already deprecated or error.
    """
    changed = False
    for fname in ("offering.json", "listing.json"):
        path = service_dir / fname
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("status") == "deprecated":
            continue
        data["status"] = "deprecated"
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        changed = True

    return changed
