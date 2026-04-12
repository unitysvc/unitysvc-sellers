"""``usvc_seller secrets`` — remote seller secret operations.

Commands:

- ``list``   — list the seller's secrets (metadata only)
- ``show``   — show one secret's metadata (by name or partial id)
- ``create`` — create a new secret
- ``check``  — check whether a secret name exists
- ``rotate`` — rotate (update) an existing secret's value
- ``delete`` — permanently delete a secret
"""

from __future__ import annotations

import json
import sys
from getpass import getpass
from pathlib import Path

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
    help="Remote secret operations (list, show, create, check, rotate, delete).",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _read_value(
    value: str | None,
    value_file: Path | None,
    value_stdin: bool,
) -> str:
    """Resolve a secret value from flags or interactive prompt.

    Priority: --value-stdin > --value-file > --value > interactive prompt.
    """
    if value_stdin:
        v = sys.stdin.read().strip()
        if not v:
            console.print("[red]Error:[/red] No value received on stdin")
            raise typer.Exit(code=1)
        return v
    if value_file is not None:
        if not value_file.exists():
            console.print(f"[red]Error:[/red] File not found: {value_file}")
            raise typer.Exit(code=1)
        return value_file.read_text().strip()
    if value is not None:
        return value
    # Interactive secure prompt
    v = getpass("Secret value: ")
    if not v:
        console.print("[red]Error:[/red] No value provided")
        raise typer.Exit(code=1)
    return v


async def _resolve_secret(client, name_or_id: str) -> dict:
    """Resolve a secret by exact name or partial id."""
    secrets = model_list(await client.secrets.list(limit=1000))

    # Exact name match
    for s in secrets:
        if s.get("name") == name_or_id:
            return s

    # Partial UUID prefix
    matches = [s for s in secrets if str(s.get("id", "")).startswith(name_or_id)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        console.print(
            f"[red]Error:[/red] Ambiguous id prefix '{name_or_id}' matches {len(matches)} secrets"
        )
        raise typer.Exit(code=1)

    console.print(f"[red]Error:[/red] Secret '{name_or_id}' not found")
    raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
@app.command("list")
def list_secrets(
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List the seller's secrets (metadata only — values are never returned)."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_list(await client.secrets.list(limit=1000))

    secrets = run_async(_impl(), error_prefix="Failed to list secrets")

    if not secrets:
        console.print("[dim]No secrets found[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(secrets, indent=2, default=str))
        return

    table = Table(title="Secrets")
    table.add_column("Name", style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Created", style="dim")
    table.add_column("Updated", style="dim")
    table.add_column("Last Used", style="dim")

    for s in secrets:
        table.add_row(
            s.get("name", ""),
            str(s.get("id", ""))[:8],
            str(s.get("created_at", ""))[:10],
            str(s.get("updated_at") or "—")[:10],
            str(s.get("last_used_at") or "—")[:10],
        )
    console.print(table)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------
@app.command("show")
def show_secret(
    name_or_id: str = typer.Argument(..., help="Secret name or partial UUID."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show metadata for a single secret."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return await _resolve_secret(client, name_or_id)

    secret = run_async(_impl(), error_prefix="Failed to show secret")

    if output_format == "json":
        console.print(json.dumps(secret, indent=2, default=str))
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="dim")
    table.add_column()
    table.add_row("name", secret.get("name", ""))
    table.add_row("id", str(secret.get("id", "")))
    table.add_row("owner_type", str(secret.get("owner_type", "")))
    table.add_row("owner_id", str(secret.get("owner_id", "")))
    table.add_row("created_at", str(secret.get("created_at", "")))
    table.add_row("updated_at", str(secret.get("updated_at") or "—"))
    table.add_row("last_used_at", str(secret.get("last_used_at") or "—"))
    console.print(table)


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------
@app.command("create")
def create_secret(
    name: str = typer.Argument(..., help="Secret name (uppercase + underscores, e.g. OPENAI_API_KEY)."),
    value: str | None = typer.Option(None, "--value", "-v", help="Secret value. Omit to prompt securely."),
    value_file: Path | None = typer.Option(None, "--value-file", help="Read value from file."),
    value_stdin: bool = typer.Option(False, "--value-stdin", help="Read value from stdin."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Create a new secret. The value cannot be retrieved after creation."""
    resolved_value = _read_value(value, value_file, value_stdin)

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.secrets.create(name, resolved_value))

    result = run_async(_impl(), error_prefix="Failed to create secret")

    if output_format == "json":
        console.print(json.dumps(result, indent=2, default=str))
    else:
        console.print(f"[green]✓[/green] Created secret: [bold]{result.get('name', name)}[/bold]")


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------
@app.command("check")
def check_secret(
    name: str = typer.Argument(..., help="Secret name to check."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Check whether a secret with the given name exists."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.secrets.check(name))

    result = run_async(_impl(), error_prefix="Failed to check secret")

    if result.get("exists"):
        console.print(f"[green]✓[/green] Secret [bold]{name}[/bold] exists")
    else:
        console.print(f"[yellow]✗[/yellow] Secret [bold]{name}[/bold] does not exist")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# rotate
# ---------------------------------------------------------------------------
@app.command("rotate")
def rotate_secret(
    name_or_id: str = typer.Argument(..., help="Secret name or partial UUID."),
    value: str | None = typer.Option(None, "--value", "-v", help="New secret value. Omit to prompt securely."),
    value_file: Path | None = typer.Option(None, "--value-file", help="Read value from file."),
    value_stdin: bool = typer.Option(False, "--value-stdin", help="Read value from stdin."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Rotate (update) the value of an existing secret."""
    resolved_value = _read_value(value, value_file, value_stdin)

    async def _impl():
        async with async_client(api_key, base_url) as client:
            secret = await _resolve_secret(client, name_or_id)
            return model_to_dict(await client.secrets.rotate(secret["id"], resolved_value))

    result = run_async(_impl(), error_prefix="Failed to rotate secret")
    console.print(f"[green]✓[/green] Rotated secret: [bold]{result.get('name', name_or_id)}[/bold]")


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------
@app.command("delete")
def delete_secret(
    name_or_id: str = typer.Argument(..., help="Secret name or partial UUID."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Permanently delete a secret. Services referencing it will stop working."""
    if not force and not typer.confirm(
        f"Delete secret '{name_or_id}'? Services referencing it will stop working immediately."
    ):
        raise typer.Exit(code=0)

    async def _impl():
        async with async_client(api_key, base_url) as client:
            secret = await _resolve_secret(client, name_or_id)
            await client.secrets.delete(secret["id"])
            return secret

    secret = run_async(_impl(), error_prefix="Failed to delete secret")
    console.print(f"[green]✓[/green] Deleted: [bold]{secret.get('name', name_or_id)}[/bold]")
