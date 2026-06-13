"""``usvc_seller templates`` — browse the platform service-template catalog.

Read-only discovery: ``list`` the active platform templates and ``show`` one's
parameter schema, so you know what you can instantiate. Creating a service from
a template lives in ``usvc_seller instances create`` (see
``commands/instances.py``).
"""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_list,
    model_to_dict,
    run_async,
)

console = Console()

app = typer.Typer(
    help="Browse the platform service-template catalog (list, show).",
)


async def _resolve_template(client, name_or_id: str) -> dict[str, Any]:
    """Find an active template by exact name or partial UUID prefix."""
    templates = model_list(await client.templates.list(limit=500))
    for t in templates:
        if t.get("name") == name_or_id:
            return t
    matches = [t for t in templates if str(t.get("id", "")).startswith(name_or_id)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        console.print(f"[red]Error:[/red] Ambiguous template prefix '{name_or_id}' matches {len(matches)} templates")
        raise typer.Exit(code=1)
    console.print(f"[red]Error:[/red] Template '{name_or_id}' not found")
    raise typer.Exit(code=1)


@app.command("list")
def list_templates(
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List the active platform templates you can instantiate."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_list(await client.templates.list(limit=500))

    templates = run_async(_impl(), error_prefix="Failed to list templates")

    if not templates:
        console.print("[dim]No templates available[/dim]")
        return
    if output_format == "json":
        console.print(json.dumps(templates, indent=2, default=str))
        return

    table = Table(title="Service Templates")
    table.add_column("Name", style="bold")
    table.add_column("Version")
    table.add_column("Type")
    table.add_column("Pool")
    table.add_column("ID", style="dim")
    for t in templates:
        pool = t.get("pool_name")
        table.add_row(
            t.get("name", ""),
            str(t.get("version", "")),
            str(t.get("service_type", "")),
            f"/p/{pool}" if pool else "",
            str(t.get("id", ""))[:8],
        )
    console.print(table)


@app.command("show")
def show_template(
    name_or_id: str = typer.Argument(..., help="Template name or partial UUID."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show a template's metadata and its parameter schema."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            stub = await _resolve_template(client, name_or_id)
            return model_to_dict(await client.templates.get(stub["id"]))

    tpl = run_async(_impl(), error_prefix="Failed to show template")

    if output_format == "json":
        console.print(json.dumps(tpl, indent=2, default=str))
        return

    console.print(f"\n[bold]{tpl.get('display_name') or tpl.get('name', '?')}[/bold]")
    if tpl.get("description"):
        console.print(f"  {tpl['description']}")
    console.print()
    meta = Table(show_header=False, box=None, padding=(0, 2))
    meta.add_column("Field", style="cyan")
    meta.add_column("Value")
    for key in ("id", "name", "version", "service_type", "pool_name"):
        if tpl.get(key) is not None:
            meta.add_row(key, str(tpl[key]))
    console.print(meta)

    props = (tpl.get("parameter_schema") or {}).get("properties") or {}
    if props:
        console.print("\n[bold]Parameters[/bold] (use --param key=value)")
        ptable = Table()
        ptable.add_column("Parameter", style="bold")
        ptable.add_column("Type")
        ptable.add_column("Default")
        ptable.add_column("Description")
        for key, prop in props.items():
            secret = " [dim](secret name)[/dim]" if prop.get("format") == "secret" else ""
            ptable.add_row(
                key + secret,
                str(prop.get("type", "")),
                str(prop.get("default", "")),
                prop.get("description", ""),
            )
        console.print(ptable)
    console.print(
        "\n[dim]Create a service from this template with[/dim] "
        "[cyan]usvc_seller instances create[/cyan][dim].[/dim]"
    )
