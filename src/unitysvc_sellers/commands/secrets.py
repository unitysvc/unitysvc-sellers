"""``usvc secrets`` — remote seller secret operations.

Commands:

- ``list``   — list the seller's secrets (metadata only)
- ``show``   — show one secret's metadata by name
- ``set``    — set a secret (idempotent — creates or rotates)
- ``delete`` — permanently delete a secret
"""

from __future__ import annotations

import json
import sys
from getpass import getpass

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
    help="Remote secret operations (list, show, set, delete).",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _resolve_value(value: str | None, *, name: str) -> str:
    """Resolve a secret value with mainstream-CLI semantics.

    Resolution order:
      1. ``--value VALUE``  — explicit literal (also covers shell expansion
                              like ``--value "$ENV_NAME"``)
      2. piped stdin        — ``echo v | usvc secret set X``
                              (trailing newline stripped)
      3. interactive prompt — TTY only; hidden input

    Mirrors ``gh secret set`` and ``vault kv put``.
    """
    if value is not None:
        return value
    if not sys.stdin.isatty():
        # Piped (or closed) stdin: read it. Strip a single trailing
        # newline so ``echo "$X" | ...`` works as expected.
        return sys.stdin.read().rstrip("\n")
    # Terminal: prompt with hidden input.
    return getpass(f"Value for secret '{name}': ")


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
    table.add_column("Created", style="dim")
    table.add_column("Updated", style="dim")
    table.add_column("Last Used", style="dim")

    for s in secrets:
        table.add_row(
            s.get("name", ""),
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
    name: str = typer.Argument(..., help="Secret name (e.g. OPENAI_API_KEY)."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show metadata for a single secret by name."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.secrets.get(name))

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
# set (idempotent — creates or rotates)
# ---------------------------------------------------------------------------
@app.command("set")
def set_secret(
    name: str = typer.Argument(..., help="Secret name (uppercase + underscores, e.g. OPENAI_API_KEY)."),
    value: str | None = typer.Option(
        None,
        "--value",
        "-v",
        help=(
            "Secret value. If omitted: reads from stdin when piped, prompts with hidden input when run interactively."
        ),
    ),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set a secret to ``value`` (idempotent — creates or rotates).

    Maps to ``PUT /v1/seller/secrets/{name}``. The value is encrypted
    server-side and cannot be retrieved later. Resolution order:

      1. ``--value VALUE``  — explicit literal (or ``--value "$ENV"``
                              via shell expansion)
      2. piped stdin        — ``echo v | usvc secrets set X``
      3. interactive prompt — TTY only; hidden input

    Mirrors ``gh secret set`` and ``vault kv put``.
    """
    resolved_value = _resolve_value(value, name=name)

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.secrets.set(name, resolved_value))

    result = run_async(_impl(), error_prefix="Failed to set secret")

    if output_format == "json":
        console.print(json.dumps(result, indent=2, default=str))
    else:
        console.print(f"[green]✓[/green] Set secret: [bold]{result.get('name', name)}[/bold]")


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------
@app.command("delete")
def delete_secret(
    name: str = typer.Argument(..., help="Secret name (e.g. OPENAI_API_KEY)."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Permanently delete a secret. Services referencing it will stop working."""
    if not force and not typer.confirm(
        f"Delete secret '{name}'? Services referencing it will stop working immediately."
    ):
        raise typer.Exit(code=0)

    async def _impl():
        async with async_client(api_key, base_url) as client:
            await client.secrets.delete(name)

    run_async(_impl(), error_prefix="Failed to delete secret")
    console.print(f"[green]✓[/green] Deleted: [bold]{name}[/bold]")
