"""``usvc_seller promotions`` — remote promotion operations.

Ports the legacy ``usvc promotions`` command group from
``unitysvc-services`` onto :class:`unitysvc_sellers.AsyncClient`.

Commands:

- ``list``     — list the seller's promotions
- ``show``     — show one promotion (by name or partial id)
- ``activate`` — set status to ``active``
- ``pause``    — set status to ``paused``
- ``delete``   — permanently delete a promotion

The legacy ``activate`` / ``pause`` HTTP routes were absorbed into
``PATCH /v1/seller/promotions/{id}`` with a ``status`` field as part of
the seller-api-codegen-hygiene cleanup. The CLI keeps both as
ergonomic shortcuts that internally call ``promotions.update``.
"""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table
from unitysvc_core.models.promotion_data import describe_scope

from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_list,
    model_to_dict,
    resolve_promotion,
    run_async,
)

console = Console()

app = typer.Typer(
    help="Remote promotion operations (list, show, activate, pause, delete).",
)


_STATUS_STYLES = {
    "active": "green",
    "draft": "yellow",
    "paused": "red",
    "scheduled": "cyan",
    "expired": "dim",
    "cancelled": "dim",
}


def _style_status(status: str) -> str:
    color = _STATUS_STYLES.get(status, "")
    if color:
        return f"[{color}]{status}[/{color}]"
    return status


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
@app.command("list")
def list_promotions(
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List the seller's promotions on the backend."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_list(await client.promotions.list(limit=1000))

    rules = run_async(_impl(), error_prefix="Failed to list promotions")

    if not rules:
        console.print("[dim]No promotions found[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(rules, indent=2, default=str))
        return

    table = Table(title="Promotions")
    table.add_column("Name", style="bold")
    table.add_column("Scope")
    table.add_column("Code")
    table.add_column("Status")
    table.add_column("Priority", justify="right")
    table.add_column("ID", style="dim")

    for rule in rules:
        table.add_row(
            rule.get("name", ""),
            describe_scope(rule.get("scope")),
            rule.get("code", ""),
            _style_status(rule.get("status", "")),
            str(rule.get("priority", 0)),
            str(rule.get("id", ""))[:8],
        )
    console.print(table)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------
@app.command("show")
def show_promotion(
    name_or_id: str = typer.Argument(..., help="Promotion name or partial UUID."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show details of a single promotion."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return await resolve_promotion(client, name_or_id)

    rule = run_async(_impl(), error_prefix="Failed to show promotion")

    if output_format == "json":
        console.print(json.dumps(rule, indent=2, default=str))
        return

    console.print(f"\n[bold]{rule.get('name', '?')}[/bold]")
    if rule.get("description"):
        console.print(f"  {rule['description']}")
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="dim")
    table.add_column()
    table.add_row("id", str(rule.get("id", "")))
    table.add_row("scope", describe_scope(rule.get("scope")))
    table.add_row("code", str(rule.get("code") or "(none)"))
    table.add_row("pricing", json.dumps(rule.get("pricing", {}), indent=2))
    table.add_row("apply_at", str(rule.get("apply_at", "")))
    table.add_row("priority", str(rule.get("priority", 0)))
    table.add_row("status", _style_status(rule.get("status", "")))
    console.print(table)


# ---------------------------------------------------------------------------
# activate / pause (sugar over update with status)
# ---------------------------------------------------------------------------
def _set_promotion_status(
    name_or_id: str,
    *,
    new_status: str,
    api_key: str | None,
    base_url: str,
    success_verb: str,
) -> None:
    async def _impl():
        async with async_client(api_key, base_url) as client:
            promo = await resolve_promotion(client, name_or_id)
            return model_to_dict(await client.promotions.update(promo["id"], {"status": new_status}))

    result = run_async(_impl(), error_prefix=f"Failed to {success_verb}")
    console.print(
        f"[green]✓[/green] {success_verb}: "
        f"{result.get('name', name_or_id)} → {_style_status(result.get('status', new_status))}"
    )


@app.command("activate")
def activate_promotion(
    name_or_id: str = typer.Argument(..., help="Promotion name or partial UUID."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set a promotion's status to ``active``."""
    _set_promotion_status(
        name_or_id,
        new_status="active",
        api_key=api_key,
        base_url=base_url,
        success_verb="Activated",
    )


@app.command("pause")
def pause_promotion(
    name_or_id: str = typer.Argument(..., help="Promotion name or partial UUID."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set a promotion's status to ``paused``."""
    _set_promotion_status(
        name_or_id,
        new_status="paused",
        api_key=api_key,
        base_url=base_url,
        success_verb="Paused",
    )


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------
@app.command("delete")
def delete_promotion(
    name_or_id: str = typer.Argument(..., help="Promotion name or partial UUID."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Permanently delete a promotion."""
    if not force and not typer.confirm(f"Delete promotion '{name_or_id}'?"):
        raise typer.Exit(code=0)

    async def _impl():
        async with async_client(api_key, base_url) as client:
            promo = await resolve_promotion(client, name_or_id)
            await client.promotions.delete(promo["id"])
            return promo

    promo = run_async(_impl(), error_prefix="Failed to delete promotion")
    console.print(f"[green]✓[/green] Deleted: {promo.get('name', name_or_id)}")
