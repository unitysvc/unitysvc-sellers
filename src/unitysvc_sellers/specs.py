"""specs command group - local operations on the flat specs/ layout."""

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from . import _cli_upload as upload_cmd
from . import example, format_data, populate, specs_layout
from . import list as list_cmd
from .params_render import ParamRenderError, expand_param_file, is_param_file, materialized_param_specs
from .utils import find_files_by_schema, load_data_file, read_service_id

app = typer.Typer(help="Local operations on the flat specs/ layout (validate, format, populate, upload, test, etc.)")
console = Console()


@app.callback()
def _expand_params(ctx: typer.Context) -> None:
    """Reading service files is the same whether they're written directly or
    expanded from a template.

    Before any *read* command runs, render the repo's local param files
    (``specs/<name>.json`` → ``{ template, parameters }``) into ephemeral service
    folders so the rest of the pipeline treats them exactly like hand-authored
    folders. The folders are removed — and any backend-assigned ``service_id``
    synced to the committed ``<name>.service.json`` sidecar — when the command
    finishes. ``format`` and ``populate`` are skipped: they operate on the
    committed files themselves, not the expanded view.
    """
    sub = ctx.invoked_subcommand
    # ``format``/``populate`` operate on the committed files themselves; ``expand``
    # writes the informal expanded/ tree from the param file directly — none of
    # them want the ephemeral whole-repo render.
    if not sub or sub in {"format", "populate", "expand"}:
        return
    try:
        ctx.with_resource(materialized_param_specs(Path.cwd()))
    except ParamRenderError as exc:
        console.print(f"[red]✗[/red] Param render error: {exc}")
        raise typer.Exit(1) from exc


# ---------------------------------------------------------------------------
# show — locate the three files belonging to a service and print their
# fully-expanded payload (provider + offering + listing). ``service_name``
# matches the first column of ``data list`` output; see ``_list_services_impl``
# below for the resolution algorithm it mirrors. Data is loaded through the
# seller's ``load_data_file`` wrapper so $preset sentinels are replaced with
# their expanded records before display — the CLI shows the same shape the
# upload / validate pipeline sees.
# ---------------------------------------------------------------------------


def _resolve_service_paths(data_dir: Path, service_name: str) -> tuple[Path | None, Path | None, Path | None]:
    """Return ``(provider_file, offering_file, listing_file)`` for *service_name*.

    Mirrors ``_list_services_impl``'s resolution order:
    listing.name → offering.name → provider at <listing_dir>/../../.
    Any slot may be ``None`` if the corresponding file is missing.
    """
    for listing_file, _fmt, listing_data in find_files_by_schema(data_dir, "listing_v1"):
        offering_file: Path | None = None
        offering_name = ""
        offering_results = find_files_by_schema(listing_file.parent, "offering_v1")
        if offering_results:
            offering_file, _, offering_data = offering_results[0]
            offering_name = offering_data.get("name", "")

        resolved = listing_data.get("name") or offering_name
        if resolved != service_name:
            continue

        # In the flat specs/ layout the provider lives beside the listing.
        provider_file: Path | None = None
        provider_results = find_files_by_schema(listing_file.parent, "provider_v1")
        if provider_results:
            provider_file = provider_results[0][0]

        return provider_file, offering_file, listing_file
    return None, None, None


def _render_output(payload: Any, output_format: str) -> None:
    """Emit *payload* on stdout. ``json`` gets rich syntax highlighting;
    ``text`` prints plain JSON without colour (better for piping).
    """
    text = json.dumps(payload, indent=2, default=str, ensure_ascii=False)
    if output_format == "json":
        console.print(Syntax(text, "json", theme="monokai", line_numbers=False))
    elif output_format == "text":
        print(text)
    else:
        console.print(f"[red]Unknown format: {output_format!r}. Use 'json' or 'text'.[/red]")
        raise typer.Exit(code=1)


@app.command("show")
def show_service(
    service_name: str = typer.Argument(
        ...,
        help="Service name (first column of 'usvc_seller specs list services' output).",
    ),
    only_provider: bool = typer.Option(False, "--provider", help="Show only provider data."),
    only_offering: bool = typer.Option(False, "--offering", help="Show only offering data."),
    only_listing: bool = typer.Option(False, "--listing", help="Show only listing data."),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Directory containing data files (default: current directory).",
    ),
    output_format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format: json (syntax-highlighted) or text (plain).",
    ),
) -> None:
    """Show expanded data for a service.

    By default prints provider + offering + listing as a single JSON
    object keyed by section. Pass one or more of ``--provider``,
    ``--offering``, ``--listing`` to restrict the output — with exactly
    one flag set, the selected section is emitted unwrapped for easy
    piping into ``jq``.

    Data is loaded through the seller's preset-aware loader, so any
    ``$doc_preset`` / ``$file_preset`` sentinels have already been
    replaced with the expanded records from ``unitysvc-data``.
    """
    if data_dir is None:
        data_dir = Path.cwd()
    if not data_dir.is_absolute():
        data_dir = Path.cwd() / data_dir
    if not data_dir.exists():
        console.print(f"[red]Data directory not found: {data_dir}[/red]")
        raise typer.Exit(code=1)

    provider_file, offering_file, listing_file = _resolve_service_paths(data_dir, service_name)
    if listing_file is None:
        console.print(
            f"[red]Service not found: {service_name!r}. "
            f"Run 'usvc_seller specs list services' to see available service names.[/red]"
        )
        raise typer.Exit(code=1)

    def _load(path: Path | None) -> dict[str, Any]:
        if path is None:
            return {}
        data, _ = load_data_file(path)
        return data

    provider_data = _load(provider_file)
    offering_data = _load(offering_file)
    listing_data = _load(listing_file)

    flags = {
        "provider": only_provider,
        "offering": only_offering,
        "listing": only_listing,
    }
    selected = [name for name, on in flags.items() if on]
    sections = {
        "provider": provider_data,
        "offering": offering_data,
        "listing": listing_data,
    }

    if not selected:
        _render_output(sections, output_format)
    elif len(selected) == 1:
        # Unwrapped for single-section — more jq-friendly.
        _render_output(sections[selected[0]], output_format)
    else:
        _render_output({k: sections[k] for k in selected}, output_format)


@app.command("expand")
def expand_service(
    name: str = typer.Argument(
        ...,
        help="Service name = the param file's path under specs/ without .json (e.g. 'parasail/foo').",
    ),
    presets: bool = typer.Option(
        False,
        "--presets",
        help="Also resolve $doc_preset / $file_preset references and copy their files into the folder.",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help=(
            "Directory to expand into (default: <repo>/expanded — the one tree discovery ignores). "
            "The full <service_name> path is created beneath it, so several services never collide."
        ),
    ),
    flat: bool = typer.Option(
        False,
        "--flat",
        help=(
            "Write the spec files directly into the directory, without the <service_name>/ subfolder "
            "(predictable paths). Holds one service at a time; best paired with --output-dir."
        ),
    ),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Repo root or specs/ directory (default: current directory).",
    ),
) -> None:
    """Expand a param file into the informal ``expanded/`` tree for inspection.

    Renders ``specs/<NAME>.json`` to ``expanded/<NAME>/`` (provider + offering +
    listing + bundled files) at the repo root. The folder is yours to read,
    diff, or delete — it is **never** validated or uploaded, and discovery
    ignores it, so it may go stale after a template change until you re-run
    ``expand``. Pass ``--presets`` to also inline preset documents so the folder
    has no references outside itself, or ``--output-dir`` to expand elsewhere.
    """
    start = (data_dir or Path.cwd()).resolve()
    specs_root = specs_layout.resolve_specs_root(start)
    param_file = specs_root / f"{name}.json"
    if not param_file.is_file():
        console.print(f"[red]✗[/red] No param file for {name!r} at {param_file}")
        raise typer.Exit(1)
    if not is_param_file(param_file):
        console.print(
            f"[red]✗[/red] {param_file.name} is not a param file (a {{template?, parameters}} spec). "
            f"'expand' only renders param files."
        )
        raise typer.Exit(1)
    try:
        folder = expand_param_file(param_file, expand_presets=presets, output_dir=output_dir, flat=flat)
    except ParamRenderError as exc:
        console.print(f"[red]✗[/red] Param render error: {exc}")
        raise typer.Exit(1) from exc
    console.print(f"[green]✓[/green] Expanded to {folder}")
    if output_dir is None:
        console.print("[dim]Inspection only — not part of the catalog; re-run 'expand' to refresh.[/dim]")
    else:
        # Only the default expanded/ tree is auto-excluded from discovery.
        console.print(
            "[dim]Inspection only. Note: a custom --output-dir is not auto-ignored by discovery — "
            "keep it outside the catalog (or gitignored) so it isn't picked up as a service.[/dim]"
        )


# Register subcommands
app.command("validate")(specs_layout.validate)
app.command("format")(format_data.format_data)
app.command("populate")(populate.populate)
app.command("upload")(upload_cmd.upload)

# Test commands - hyphenated for clarity (verb-noun)
app.command("list-tests")(example.list_code_examples)
app.command("run-tests")(example.run_local)
app.command("show-test")(example.show_test)

# Create combined list subgroup
list_app = typer.Typer(help="List local data files")


def _list_services_impl(data_dir: Path | None):
    """Implementation of services listing."""
    # Set data directory
    if data_dir is None:
        data_dir = Path.cwd()

    if not data_dir.is_absolute():
        data_dir = Path.cwd() / data_dir

    if not data_dir.exists():
        console.print(f"[red]Data directory not found: {data_dir}[/red]")
        raise typer.Exit(code=1)

    console.print(f"[blue]Scanning for services in:[/blue] {data_dir}\n")

    # Find all listing files
    listing_results = find_files_by_schema(data_dir, "listing_v1")

    if not listing_results:
        console.print("[yellow]No services found.[/yellow]")
        raise typer.Exit(code=0)

    # Build service information
    services = []

    for listing_file, _format, listing_data in listing_results:
        # Get listing name and status
        listing_name = listing_data.get("name", "")
        listing_status = listing_data.get("status", "")

        # Find corresponding offering file (same directory)
        offering_results = find_files_by_schema(listing_file.parent, "offering_v1")
        offering_name = ""
        offering_status = ""
        offering_data: dict[str, Any] = {}
        if offering_results:
            _, _fmt, offering_data = offering_results[0]
            offering_name = offering_data.get("name", "")
            offering_status = offering_data.get("status", "")

        # Service name: listing name, or offering name if listing name not specified
        service_name = listing_name or offering_name or "unknown"

        # Provider lives beside the listing in the flat specs/ layout.
        provider_name = ""
        provider_status = ""
        provider_results = find_files_by_schema(listing_file.parent, "provider_v1")
        if provider_results:
            _, _fmt, provider_data = provider_results[0]
            provider_name = provider_data.get("name", "")
            provider_status = provider_data.get("status", "")

        # Compute service status: draft > deprecated > ready
        statuses = [s for s in [provider_status, offering_status, listing_status] if s]
        if "draft" in statuses:
            service_status = "draft"
        elif "deprecated" in statuses:
            service_status = "deprecated"
        elif statuses and all(s == "ready" for s in statuses):
            service_status = "ready"
        else:
            service_status = statuses[0] if statuses else ""

        # Get service_id from the folder's service.json if it exists
        service_id = read_service_id(listing_file.parent) or ""

        # Get relative paths
        try:
            listing_rel = listing_file.relative_to(data_dir)
        except ValueError:
            listing_rel = listing_file

        services.append(
            {
                "service_name": service_name,
                "provider_name": provider_name,
                "status": service_status,
                "listing_file": str(listing_rel),
                "service_id": service_id,
            }
        )

    # Display results in table
    table = Table(title="Services")
    table.add_column("Name", style="cyan")
    table.add_column("Provider", style="blue")
    table.add_column("Status", style="magenta")
    table.add_column("Service ID", style="yellow")
    table.add_column("File", style="dim")

    for svc in services:
        service_id = svc["service_id"][:8] + "..." if svc["service_id"] else "-"
        table.add_row(
            svc["service_name"],
            svc["provider_name"] or "-",
            svc["status"] or "-",
            service_id,
            svc["listing_file"],
        )

    console.print(table)
    console.print(f"\n[green]Total:[/green] {len(services)} service(s)")


@list_app.callback(invoke_without_command=True)
def list_callback(
    ctx: typer.Context,
    data_dir: Path = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Directory containing data files (default: current directory)",
    ),
):
    """List local data files. Without a subcommand, lists all services."""
    if ctx.invoked_subcommand is None:
        _list_services_impl(data_dir)


@list_app.command("services")
def list_services_cmd(
    data_dir: Path | None = typer.Argument(
        None,
        help="Directory containing data files (default: current directory)",
    ),
):
    """List all services with their provider, offering, and listing files."""
    _list_services_impl(data_dir)


# Add existing list commands from list.py
list_app.command("providers")(list_cmd.list_providers)
list_app.command("sellers")(list_cmd.list_sellers)
list_app.command("offerings")(list_cmd.list_offerings)
list_app.command("listings")(list_cmd.list_listings)

app.add_typer(list_app, name="list")
