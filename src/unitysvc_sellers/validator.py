"""Seller-catalog validator.

Wraps ``unitysvc_core.validator.DataValidator`` with seller-specific
catalog-layout checks: provider status warnings, service-directory
invariants (each service dir has exactly one offering file), and the
``usvc_seller data validate`` CLI command.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from unitysvc_core.validator import DataValidationError
from unitysvc_core.validator import DataValidator as CoreDataValidator

# S3 bucket name rules per https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
# - 3-63 characters, lowercase letters/digits/hyphens only, start and end with letter or digit
_S3_BUCKET_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$")
_S3_GATEWAY_PREFIX = "${S3_GATEWAY_BASE_URL}/"


class DataValidator(CoreDataValidator):
    """Seller-catalog validator.

    Extends the core per-file validator with checks that understand the
    seller catalog directory layout (``<provider>/services/<service>/``).
    """

    def validate_provider_status(self) -> tuple[bool, list[str]]:
        """
        Validate provider status and warn about services under disabled/draft providers.

        Returns tuple of (is_valid, warnings) where warnings indicate services
        that will be affected by provider status.
        """
        from unitysvc_core.models.base import ProviderStatusEnum
        from unitysvc_core.models.provider_v1 import ProviderV1

        warnings: list[str] = []

        provider_files = [
            f for f in self.data_dir.glob("*/provider.*") if not any(part.startswith(".") for part in f.parts)
        ]

        for provider_file in provider_files:
            try:
                data, load_errors = self.load_data_file(provider_file)
                if load_errors or data is None:
                    warnings.append(f"Failed to load provider file {provider_file}: {load_errors}")
                    continue

                provider = ProviderV1.model_validate(data)
                provider_dir = provider_file.parent
                provider_name = provider.name

                if provider.status != ProviderStatusEnum.ready:
                    services_dir = provider_dir / "services"
                    if services_dir.exists():
                        service_count = len(list(services_dir.iterdir()))
                        if service_count > 0:
                            warnings.append(
                                f"Provider '{provider_name}' has status '{provider.status}' but has {service_count} "
                                f"service(s). All services under this provider will be affected."
                            )

            except Exception as e:
                warnings.append(f"Error checking provider status in {provider_file}: {e}")

        return True, warnings

    def validate_s3_base_urls(self, data: dict[str, Any], schema_name: str) -> list[str]:
        """Validate S3 gateway aliases in listing_v1 user_access_interfaces.

        For any interface whose base_url starts with ${S3_GATEWAY_BASE_URL}/,
        the suffix must be a valid S3 bucket name.  Jinja2 template aliases
        (containing {{ }}) are skipped — they are validated at render time.
        """
        if schema_name != "listing_v1":
            return []

        errors: list[str] = []
        interfaces = data.get("user_access_interfaces") or {}
        if not isinstance(interfaces, dict):
            return errors

        for iface_name, iface in interfaces.items():
            if not isinstance(iface, dict):
                continue
            base_url = iface.get("base_url", "")
            if not isinstance(base_url, str) or not base_url.startswith(_S3_GATEWAY_PREFIX):
                continue

            alias = base_url[len(_S3_GATEWAY_PREFIX):]

            # Jinja2 template — cannot validate statically
            if "{{" in alias or "{%" in alias:
                continue

            field = f"user_access_interfaces.{iface_name}.base_url"

            if not alias:
                errors.append(f"{field}: S3 gateway alias is empty (must be a valid S3 bucket name)")
                continue

            if not _S3_BUCKET_RE.match(alias):
                errors.append(
                    f"{field}: S3 gateway alias '{alias}' is not a valid S3 bucket name — "
                    f"must be 3-63 characters, lowercase letters/digits/hyphens only, "
                    f"and must start and end with a letter or digit "
                    f"(see https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html)"
                )
                continue

            if alias.startswith("xn--"):
                errors.append(f"{field}: S3 gateway alias '{alias}' cannot start with 'xn--' (reserved prefix)")
            elif alias.endswith("-s3alias") or alias.endswith("--ol-s3"):
                errors.append(f"{field}: S3 gateway alias '{alias}' uses a reserved suffix")

        return errors

    def validate_data_file(self, file_path: Path) -> tuple[bool, list[str]]:
        """Validate a data file, adding S3 base_url checks for listing_v1."""
        is_valid, errors = super().validate_data_file(file_path)
        data, load_errors = self.load_data_file(file_path)
        if data and not load_errors:
            s3_errors = self.validate_s3_base_urls(data, data.get("schema", ""))
            if s3_errors:
                errors.extend(s3_errors)
                is_valid = False
        return is_valid, errors

    def validate_all(self) -> dict[str, tuple[bool, list[str]]]:
        """Validate all files in the data directory, including provider status."""
        results = super().validate_all()

        _provider_ok, provider_warnings = self.validate_provider_status()
        if provider_warnings:
            # Prepend provider status warnings while preserving insertion order
            results = {"_provider_status": (True, provider_warnings), **results}

        return results

    def validate_directory_data(self, directory: Path) -> None:
        """Validate data files in a directory for consistency.

        Validation rules:
        1. Each service directory must have exactly one offering_v1 file
        2. Listings in the directory automatically belong to that single offering

        Raises:
            DataValidationError: If validation fails
        """
        data_files: list[Path] = []
        for pattern in ["*.json", "*.toml"]:
            data_files.extend(directory.glob(pattern))

        offerings: list[tuple[Path, dict[str, Any]]] = []
        listings: list[Path] = []

        for file_path in data_files:
            try:
                data, load_errors = self.load_data_file(file_path)
                if load_errors or data is None:
                    continue

                schema = data.get("schema")

                if schema == "offering_v1":
                    offerings.append((file_path, data))
                elif schema == "listing_v1":
                    listings.append(file_path)

            except Exception as e:
                if isinstance(e, DataValidationError):
                    raise
                continue

        if len(offerings) > 1:
            offering_files = [str(f) for f, _ in offerings]
            raise DataValidationError(
                f"Multiple offering_v1 files found in directory {directory}:\n"
                f"  - " + "\n  - ".join(offering_files) + "\n"
                "Each service directory must have exactly one offering file."
            )

        if listings and len(offerings) == 0:
            raise DataValidationError(
                f"Listing files found in {directory} but no offering_v1 file exists. "
                f"Each service directory must have exactly one offering file."
            )

    def validate_all_service_directories(self, data_dir: Path) -> list[str]:
        """
        Validate all service directories in a directory tree.

        Returns a list of validation error messages (empty if all valid).
        """
        errors: list[str] = []

        directories_to_validate: set[Path] = set()

        for pattern in ["*.json", "*.toml"]:
            for file_path in data_dir.rglob(pattern):
                if any(part.startswith(".") for part in file_path.parts):
                    continue

                try:
                    data, load_errors = self.load_data_file(file_path)
                    if load_errors or data is None:
                        continue

                    schema = data.get("schema")
                    if schema in ["offering_v1", "listing_v1"]:
                        directories_to_validate.add(file_path.parent)
                except Exception:
                    continue

        for directory in sorted(directories_to_validate):
            try:
                self.validate_directory_data(directory)
            except DataValidationError as e:
                errors.append(str(e))

        return errors


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------

app = typer.Typer(help="Validate data files")
console = Console()


@app.command()
def validate(
    data_dir: Path | None = typer.Argument(
        None,
        help="Directory containing data files to validate (default: current directory)",
    ),
    has_service_id: bool = typer.Option(
        False,
        "--has-service-id",
        help="Require service_id field in listing files (from override or data file)",
    ),
) -> None:
    """
    Validate data consistency in service and listing files.

    Checks:
    1. Each service directory has exactly one offering_v1 file
    2. Listing files exist in directories with a valid offering file
    """
    import unitysvc_core

    if data_dir is None:
        data_dir = Path.cwd()

    if not data_dir.exists():
        console.print(f"[red]✗[/red] Data directory not found: {data_dir}")
        raise typer.Exit(1)

    console.print(f"[cyan]Validating data files in:[/cyan] {data_dir}")
    console.print()

    # Schemas live in unitysvc_core
    schema_dir = Path(unitysvc_core.__file__).parent / "schema"

    validator = DataValidator(data_dir, schema_dir)

    all_results = validator.validate_all()
    validation_errors: list[str] = []

    for file_path, (is_valid, errors) in all_results.items():
        if not is_valid and errors:
            for error in errors:
                validation_errors.append(f"{file_path}: {error}")

    directory_errors = validator.validate_all_service_directories(data_dir)
    validation_errors.extend(directory_errors)

    if has_service_id:
        from .utils import find_files_by_schema

        listing_files = find_files_by_schema(data_dir, "listing_v1")
        for listing_path, _fmt, data in listing_files:
            if not data.get("service_id"):
                validation_errors.append(
                    f"{listing_path}: Missing service_id "
                    f"(run 'usvc_seller data upload' first to generate override file)"
                )

    if validation_errors:
        console.print(f"[red]✗ Validation failed with {len(validation_errors)} error(s):[/red]")
        console.print()
        for i, error in enumerate(validation_errors, 1):
            console.print(f"[red]{i}.[/red] {error}")
            console.print()
        raise typer.Exit(1)
    else:
        console.print("[green]✓ All data files are valid![/green]")
