"""``usvc_seller params`` — system-template param files under ``params/``.

A **param file** (``params/<name>.json`` = ``{ "template", "parameters" }``) is a
compact, declarative service definition: a **system template** name (browse the
catalog with ``usvc_seller templates``) plus the values to render it with. The
``params/`` folder is the system-template mirror of ``specs/`` (which holds local
spec folders and local-template param files):

- **`list`** / **`show`** — inspect the param files in ``params/`` (offline).
- **`instantiate`** — render the system template + parameters into a backend
  service (the params-kind analog of ``specs upload``), for all param files or a
  selected subset. The backend-assigned ``service_id`` round-trips through a
  committed ``<name>.service.json`` sidecar.

A param file whose ``template`` is a pool-named system template produces a
service that joins ``/p/<pool>`` at the pool's uniform terms.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import json5
import typer
from rich.console import Console
from rich.table import Table

from ..params_render import is_param_file
from ..utils import service_name_matches
from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_to_dict,
    run_async,
)
from .templates import _resolve_template

console = Console()

app = typer.Typer(
    help="System-template param files under params/ (list, show, instantiate).",
)


# --- params/ discovery + identity sidecar (local, no network) --------------


def _params_root(data_dir: Path | None) -> Path:
    """The ``params/`` directory, resolved from a repo root or the dir itself."""
    start = (data_dir or Path.cwd()).resolve()
    candidate = start / "params"
    return candidate if candidate.is_dir() else start


def _sidecar(param_file: Path) -> Path:
    return param_file.with_name(param_file.stem + ".service.json")


def _read_service_id(param_file: Path) -> str | None:
    sidecar = _sidecar(param_file)
    if not sidecar.is_file():
        return None
    try:
        data = json.loads(sidecar.read_text())
    except Exception:
        return None
    sid = data.get("service_id") if isinstance(data, dict) else None
    return str(sid) if sid else None


def _write_service_id(param_file: Path, service_id: str) -> None:
    sidecar = _sidecar(param_file)
    data: dict[str, Any] = {}
    if sidecar.is_file():
        try:
            loaded = json.loads(sidecar.read_text())
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = {}
    data["service_id"] = str(service_id)
    sidecar.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def _entries(data_dir: Path | None, name_filter: str | None = None) -> list[dict[str, Any]]:
    """Param files under ``params/`` as ``{service_name, template, parameters,
    service_id, path}``, optionally fnmatch-filtered by name, sorted by name."""
    root = _params_root(data_dir)
    out: list[dict[str, Any]] = []
    for path in sorted(p for p in root.rglob("*.json") if is_param_file(p)):
        name = path.relative_to(root).with_suffix("").as_posix()
        if name_filter and not service_name_matches(name, name_filter):
            continue
        data = json5.loads(path.read_text())
        out.append(
            {
                "service_name": name,
                "template": data.get("template"),
                "parameters": data.get("parameters") or {},
                "service_id": _read_service_id(path),
                "path": path,
            }
        )
    return sorted(out, key=lambda e: e["service_name"])


def _extract_service_id(result: dict[str, Any]) -> str | None:
    """Pull a ``service_id`` from an ingest task result — the flat ServiceData
    record, or the pre-flatten ``{"service": {...}}`` shape."""
    if not isinstance(result, dict):
        return None
    sid = result.get("service_id")
    if not sid:
        service = result.get("service")
        if isinstance(service, dict):
            sid = service.get("service_id") or service.get("id")
    return str(sid) if sid else None


# --- commands --------------------------------------------------------------


@app.command("list")
def list_params(
    name: str | None = typer.Argument(None, help="Filter by name (fnmatch, e.g. 'acme/*' or 'acme/%')."),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Repo root or params/ directory (default: current directory).",
    ),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
) -> None:
    """List the system-template param files under ``params/`` (offline)."""
    entries = _entries(data_dir, name)
    if not entries:
        console.print("[dim]No param files found under params/[/dim]")
        return
    if output_format == "json":
        console.print(
            json.dumps(
                [{k: v for k, v in e.items() if k != "path"} for e in entries],
                indent=2,
                default=str,
            )
        )
        return
    table = Table(title="Param Files (params/)")
    table.add_column("Service", style="bold")
    table.add_column("Template")
    table.add_column("Service ID", style="dim")
    for e in entries:
        table.add_row(
            e["service_name"],
            e["template"] or "[red](missing)[/red]",
            (e["service_id"] or "")[:8],
        )
    console.print(table)


@app.command("show")
def show_param(
    name: str = typer.Argument(..., help="Service name of the param file (first column of `params list`)."),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Repo root or params/ directory (default: current directory).",
    ),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
) -> None:
    """Show one param file's template, parameters, and recorded service_id."""
    matches = [e for e in _entries(data_dir) if e["service_name"] == name]
    if not matches:
        console.print(
            f"[red]Error:[/red] No param file for '{name}' under params/. Run [cyan]usvc_seller params list[/cyan]."
        )
        raise typer.Exit(code=1)
    entry = matches[0]
    if output_format == "json":
        console.print(json.dumps({k: v for k, v in entry.items() if k != "path"}, indent=2, default=str))
        return

    console.print(f"\n[bold]{entry['service_name']}[/bold]")
    meta = Table(show_header=False, box=None, padding=(0, 2))
    meta.add_column("Field", style="cyan")
    meta.add_column("Value")
    meta.add_row(
        "template",
        entry["template"] or "[red](missing — system template name required)[/red]",
    )
    if entry["service_id"]:
        meta.add_row("service_id", entry["service_id"])
    console.print(meta)

    params = entry["parameters"]
    if params:
        console.print("\n[bold]Parameters[/bold]")
        ptable = Table()
        ptable.add_column("Key", style="bold")
        ptable.add_column("Value")
        for key, value in params.items():
            ptable.add_row(key, value if isinstance(value, str) else json.dumps(value, default=str))
        console.print(ptable)
    console.print("\n[dim]Instantiate with[/dim] [cyan]usvc_seller params instantiate[/cyan][dim].[/dim]")


@app.command("instantiate")
def instantiate(
    name: str | None = typer.Argument(None, help="Param-file selector (fnmatch; omit = all under params/)."),
    submit: bool = typer.Option(
        True,
        "--submit/--no-submit",
        help="Submit each rendered service for review (default), or leave a draft.",
    ),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        "-d",
        help="Repo root or params/ directory (default: current directory).",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Instantiate system-template param files into services — all, or those
    matching ``NAME``.

    Each param file's ``template`` (a system template — see ``usvc_seller
    templates``) is rendered with its ``parameters`` into a backend service. The
    returned ``service_id`` is written to a committed ``<name>.service.json``
    sidecar; an entry that already has one is skipped (re-instantiating to update
    the same service needs backend support, unitysvc/unitysvc#1273).
    """
    entries = _entries(data_dir, name)
    if not entries:
        where = f" matching '{name}'" if name else " under params/"
        console.print(f"[yellow]No param files{where}[/yellow]")
        raise typer.Exit(code=1)

    async def _impl() -> None:
        async with async_client(api_key, base_url) as client:
            for entry in entries:
                label = entry["service_name"]
                if entry["service_id"]:
                    console.print(f"[dim]• {label}: already instantiated ({entry['service_id'][:8]}) — skipping[/dim]")
                    continue
                if not entry["template"]:
                    console.print(f"[red]✗ {label}: no 'template' (system template name required)[/red]")
                    continue
                try:
                    stub = await _resolve_template(client, entry["template"])
                    queued = model_to_dict(
                        await client.instances.create(
                            stub["id"],
                            parameters=entry["parameters"],
                            name=label,
                            submit=submit,
                        )
                    )
                except Exception as exc:  # noqa: BLE001 — report and continue
                    console.print(f"[red]✗ {label}: {exc}[/red]")
                    continue

                task_id = queued.get("task_id")
                service_id = None
                if task_id:
                    statuses = await client.tasks.wait(str(task_id))
                    status = statuses.get(str(task_id), {})
                    if status.get("status") == "completed":
                        service_id = _extract_service_id(status.get("result") or {})
                if service_id:
                    _write_service_id(entry["path"], service_id)
                    console.print(f"[green]✓[/green] {label}: service_id={service_id}")
                else:
                    detail = f"task_id={task_id}" if task_id else "queued"
                    console.print(f"[green]✓[/green] {label}: submitted ({detail})")

    run_async(_impl(), error_prefix="Failed to instantiate param files")
    console.print("\n[dim]Services appear under your staging list once ingest completes.[/dim]")
