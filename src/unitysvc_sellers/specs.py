"""``specs`` command group — local operations on the flat ``specs/`` layout.

The flat layout (unitysvc#1263) replaces the nested
``data/<provider>/services/<svc>/`` tree with one self-contained folder per
Service, named by the (namespaced) service name::

    specs/<provider>/<name...>/
        provider.json      # the provider that owns this service
        offering.json      # (or offering.toml) — the offering
        listing.json       # (or listing.toml)  — the single listing
        service.json       # optional: service_id + upload provenance

Key differences from the legacy ``data/`` layout, all enforced here:

- **No ``schema`` field.** The *filename* is the type discriminator, so spec
  files must not carry a ``schema`` key.
- **No directory traversal for information.** Every folder is self-contained;
  the provider lives beside the offering and listing rather than two levels up.
- **The folder path is the service name.** ``listing.name`` must equal the
  folder's path relative to ``specs/`` (e.g. ``parasail/deepseek-ai/DeepSeek``).
- **Three required files** per folder: ``provider``, ``offering``, ``listing``
  (``.json`` or ``.toml``). ``service.json`` is optional provenance written by
  ``upload``.
"""

from __future__ import annotations

from pathlib import Path

import typer
import unitysvc_core
from rich.console import Console
from unitysvc_core.validator import DataValidator

app = typer.Typer(help="Local operations on the flat specs/ layout")
console = Console()

# Filename stem → core schema name. The filename is the discriminator now.
FILENAME_TO_SCHEMA: dict[str, str] = {
    "provider": "provider_v1",
    "offering": "offering_v1",
    "listing": "listing_v1",
}

# Spec files that must exist in every service folder (service.json is optional).
REQUIRED_KINDS: tuple[str, ...] = ("provider", "offering", "listing")

_DATA_SUFFIXES = (".json", ".toml")


def resolve_specs_root(start: Path) -> Path:
    """Resolve the ``specs/`` root from a user-supplied path.

    Accepts the repo root (with a ``specs/`` subdir), the ``specs/`` dir
    itself, or any subtree of it.
    """
    candidate = start / "specs"
    if candidate.is_dir():
        return candidate
    return start


def _find_kind_file(folder: Path, kind: str) -> tuple[Path | None, list[Path]]:
    """Return ``(the single <kind>.{json,toml}, all_matches)`` in *folder*."""
    matches = [folder / f"{kind}{suffix}" for suffix in _DATA_SUFFIXES]
    present = [p for p in matches if p.is_file()]
    return (present[0] if len(present) == 1 else None), present


def find_service_folders(root: Path) -> list[Path]:
    """Every folder under *root* that contains a ``listing.{json,toml}``."""
    folders: set[Path] = set()
    for suffix in _DATA_SUFFIXES:
        for listing in root.rglob(f"listing{suffix}"):
            if any(part.startswith(".") for part in listing.parts):
                continue
            folders.add(listing.parent)
    return sorted(folders)


def validate_service_folder(validator: DataValidator, root: Path, folder: Path) -> list[str]:
    """Validate a single ``specs/`` service folder; return error strings."""
    errors: list[str] = []
    rel_folder = folder.relative_to(root).as_posix()

    # Stale override files were folded into service.json by the migration.
    for override in sorted(folder.glob("*.override.*")):
        errors.append(
            f"{override.relative_to(root)}: legacy override file — fold it into "
            f"service.json (the flat layout stores service_id there)"
        )

    # Required spec files present, exactly one format each.
    kind_files: dict[str, Path] = {}
    for kind in REQUIRED_KINDS:
        single, present = _find_kind_file(folder, kind)
        if not present:
            errors.append(f"{rel_folder}: missing required {kind} file ({kind}.json or {kind}.toml)")
        elif len(present) > 1:
            names = ", ".join(p.name for p in present)
            errors.append(f"{rel_folder}: multiple {kind} files ({names}) — keep exactly one")
        else:
            kind_files[kind] = single  # type: ignore[assignment]

    # Per-file validation, keyed by filename rather than a ``schema`` field.
    for kind, path in kind_files.items():
        data, load_errors = validator.load_data_file(path)
        if load_errors or data is None:
            errors.extend(f"{path.relative_to(root)}: {e}" for e in (load_errors or ["failed to load"]))
            continue
        if "schema" in data:
            errors.append(
                f"{path.relative_to(root)}: remove the 'schema' field — the filename is the "
                f"discriminator in the specs/ layout"
            )
        try:
            ok, file_errors = validator.validate_data_file(
                path, schema_name=FILENAME_TO_SCHEMA[kind], check_name_consistency=False
            )
        except Exception as exc:  # noqa: BLE001 — surface, don't crash the run
            ok, file_errors = False, [f"validation raised {type(exc).__name__}: {exc}"]
        if not ok:
            errors.extend(f"{path.relative_to(root)}: {e}" for e in file_errors)

    # The folder path under specs/ must equal the listing (service) name.
    if "listing" in kind_files:
        data, load_errors = validator.load_data_file(kind_files["listing"])
        if not load_errors and isinstance(data, dict):
            listing_name = data.get("name")
            if listing_name != rel_folder:
                errors.append(
                    f"{rel_folder}: listing name {listing_name!r} does not match the folder path "
                    f"{rel_folder!r} — the folder under specs/ must be the service name"
                )

    # Optional service.json: if present, must be a JSON object.
    service_file = folder / "service.json"
    if service_file.is_file():
        data, load_errors = validator.load_data_file(service_file)
        if load_errors or not isinstance(data, dict):
            errors.append(f"{service_file.relative_to(root)}: not a valid JSON object")
        elif "schema" in data:
            errors.append(f"{service_file.relative_to(root)}: remove the 'schema' field")

    return errors


@app.command()
def validate(
    specs_dir: Path | None = typer.Argument(
        None,
        help="Repo root or specs/ directory to validate (default: current directory)",
    ),
    has_service_id: bool = typer.Option(
        False,
        "--has-service-id",
        help="Also require each service folder to have a service.json with a service_id",
    ),
) -> None:
    """Validate a repository in the flat ``specs/`` layout.

    For every service folder (one containing a ``listing.{json,toml}``):

    1. the three spec files (provider, offering, listing) are present, one
       format each, and carry no ``schema`` field;
    2. each validates against its core schema (routed by filename);
    3. ``listing.name`` equals the folder's path relative to ``specs/``.
    """
    start = (specs_dir or Path.cwd()).resolve()
    if not start.exists():
        console.print(f"[red]✗[/red] Path not found: {start}")
        raise typer.Exit(1)

    root = resolve_specs_root(start)
    console.print(f"[cyan]Validating specs in:[/cyan] {root}")
    console.print()

    schema_dir = Path(unitysvc_core.__file__).parent / "schema"
    validator = DataValidator(root, schema_dir)

    folders = find_service_folders(root)
    if not folders:
        console.print(f"[red]✗[/red] No service folders (containing a listing.json) found under {root}")
        raise typer.Exit(1)

    validation_errors: list[str] = []
    for folder in folders:
        validation_errors.extend(validate_service_folder(validator, root, folder))

        if has_service_id:
            service_file = folder / "service.json"
            data, _ = validator.load_data_file(service_file) if service_file.is_file() else (None, [])
            if not isinstance(data, dict) or not data.get("service_id"):
                rel = folder.relative_to(root).as_posix()
                validation_errors.append(
                    f"{rel}: missing service_id in service.json (run 'usvc_seller specs upload' first)"
                )

    if validation_errors:
        console.print(f"[red]✗ Validation failed with {len(validation_errors)} error(s):[/red]")
        console.print()
        for i, error in enumerate(validation_errors, 1):
            console.print(f"[red]{i}.[/red] {error}")
        raise typer.Exit(1)

    console.print(f"[green]✓ All {len(folders)} service folder(s) are valid![/green]")
