"""``usvc_seller groups`` — remote service group operations.

Net-new command group (no equivalent in ``unitysvc-services``). Mirrors
the structure of ``promotions``: name lookup with partial-id fallback,
list / show / delete. Group definitions are committed as files under
``groups/`` and pushed via ``usvc_seller groups upload``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ..client import Client
from ..exceptions import APIError
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
    help="Remote service group operations (list, show, delete, upload).",
)


_GROUP_STATUS_STYLES = {
    "active": "green",
    "draft": "yellow",
    "private": "cyan",
    "archived": "dim",
}


def _style_status(status: str) -> str:
    color = _GROUP_STATUS_STYLES.get(status, "")
    return f"[{color}]{status}[/{color}]" if color else status


# ---------------------------------------------------------------------------
# Lookup helper
# ---------------------------------------------------------------------------
async def _resolve_group(client, name_or_id: str) -> dict[str, Any]:
    """Find a service group by exact name or partial UUID prefix."""
    groups = model_list(await client.groups.list(limit=1000))

    for g in groups:
        if g.get("name") == name_or_id:
            return g

    matches = [g for g in groups if str(g.get("id", "")).startswith(name_or_id)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        console.print(f"[red]Error:[/red] Ambiguous group id prefix '{name_or_id}' matches {len(matches)} groups")
        raise typer.Exit(code=1)

    console.print(f"[red]Error:[/red] Group '{name_or_id}' not found")
    raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
@app.command("list")
def list_groups(
    status: str | None = typer.Option(
        None,
        "--status",
        help="Filter by status (draft, active, private, archived).",
    ),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List the seller's service groups."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_list(await client.groups.list(status=status, limit=1000))

    groups = run_async(_impl(), error_prefix="Failed to list groups")

    if not groups:
        console.print("[dim]No service groups found[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(groups, indent=2, default=str))
        return

    table = Table(title="Service Groups")
    table.add_column("Name", style="bold")
    table.add_column("Status")
    table.add_column("Members", justify="right")
    table.add_column("ID", style="dim")
    for group in groups:
        members = group.get("service_count")
        if members is None:
            members = len(group.get("services") or group.get("service_ids") or [])
        table.add_row(
            group.get("name", ""),
            _style_status(group.get("status", "")),
            str(members),
            str(group.get("id", ""))[:8],
        )
    console.print(table)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------
@app.command("show")
def show_group(
    name_or_id: str = typer.Argument(..., help="Group name or partial UUID."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show details of a single service group."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            stub = await _resolve_group(client, name_or_id)
            return model_to_dict(await client.groups.get(stub["id"]))

    group = run_async(_impl(), error_prefix="Failed to show group")

    if output_format == "json":
        console.print(json.dumps(group, indent=2, default=str))
        return

    console.print(f"\n[bold]{group.get('name', '?')}[/bold]")
    if group.get("description"):
        console.print(f"  {group['description']}")
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("id", str(group.get("id", "")))
    table.add_row("status", _style_status(group.get("status", "")))
    if group.get("group_type"):
        table.add_row("group_type", str(group["group_type"]))
    if group.get("owner_type"):
        table.add_row("owner_type", str(group["owner_type"]))
    services = group.get("services") or group.get("service_ids") or []
    table.add_row("members", str(len(services)))
    console.print(table)

    if services and isinstance(services, list):
        console.print("\n[bold]Members[/bold]")
        for svc in services[:50]:
            if isinstance(svc, dict):
                console.print(f"  • [cyan]{svc.get('name', '?')}[/cyan] [dim]{str(svc.get('id', ''))[:8]}[/dim]")
            else:
                console.print(f"  • [dim]{str(svc)[:8]}[/dim]")
        if len(services) > 50:
            console.print(f"  [dim]… and {len(services) - 50} more[/dim]")
    console.print()


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------
@app.command("delete")
def delete_group(
    name_or_id: str = typer.Argument(..., help="Group name or partial UUID."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Permanently delete a service group."""
    if not force and not typer.confirm(f"Delete service group '{name_or_id}'?"):
        raise typer.Exit(code=0)

    async def _impl():
        async with async_client(api_key, base_url) as client:
            stub = await _resolve_group(client, name_or_id)
            await client.groups.delete(stub["id"])
            return stub

    stub = run_async(_impl(), error_prefix="Failed to delete group")
    console.print(f"[green]✓[/green] Deleted: {stub.get('name', name_or_id)}")


# ---------------------------------------------------------------------------
# upload
# ---------------------------------------------------------------------------
@app.command("upload")
def upload_groups(
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Upload all service-group files from ``groups/`` directory."""
    if not api_key:
        console.print(
            "[red]✗[/red] Missing seller API key. Set $UNITYSVC_SELLER_API_KEY or pass --api-key.",
            style="bold red",
        )
        raise typer.Exit(code=1)

    data_dir = Path.cwd()
    console.print(f"[bold blue]Uploading groups from:[/bold blue] {data_dir / 'groups'}")

    def _on_progress(kind: str, status: str, name: str, detail: str = "") -> None:
        if status == "ok":
            console.print(f"  [green]✓[/green] upserted: [cyan]{name}[/cyan]")
        else:
            console.print(f"  [red]✗[/red] failed: [cyan]{name}[/cyan] — {detail}")

    try:
        with Client(api_key=api_key, base_url=base_url) as client:
            result = client.upload_groups(data_dir, on_progress=_on_progress)
    except APIError as exc:
        console.print(f"[red]✗[/red] API error: {exc}", style="bold red")
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        console.print(f"[red]✗[/red] Upload failed: {exc}", style="bold red")
        raise typer.Exit(code=1) from exc

    console.print()
    console.print(f"Groups — [green]{result.success}[/green] success, [red]{result.failed}[/red] failed")
    if result.errors:
        for err in result.errors:
            console.print(f"  [red]✗[/red] {err.get('file', '?')}: {err.get('error', '?')}")

    if result.failed > 0:
        raise typer.Exit(code=1)
    console.print("\n[green]✓[/green] Groups uploaded successfully", style="bold green")


# NOTE: ``usvc_seller groups refresh`` was removed alongside the
# backend endpoint it wrapped. Dynamic membership is now refreshed
# automatically by a background worker whenever a group is mutated, so
# there is no longer a manual refresh step for sellers to invoke.
