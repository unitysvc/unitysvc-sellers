"""``usvc secrets`` — remote seller secret operations.

Commands:

- ``list``   — list the seller's secrets (metadata only)
- ``show``   — show one secret's metadata by name
- ``set``    — set a secret (idempotent — creates or rotates)
- ``upload`` — bulk-set secrets from a sourceable file or stdin
- ``delete`` — permanently delete a secret
"""

from __future__ import annotations

import json
import re
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
    help="Remote secret operations (list, show, set, upload, delete).",
)

# Valid env-var / secret name: leading letter or underscore, then word chars.
_VALID_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


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


def _parse_secrets_text(text: str) -> list[tuple[str, str]]:
    """Parse sourceable / dotenv-style text into ``(name, value)`` pairs.

    Accepts the same lines you would ``source`` in a shell — ``NAME=value`` or
    ``export NAME=value``. ``#`` comment lines and blank lines are ignored, one
    layer of surrounding single/double quotes is stripped, and when a name is
    assigned more than once the last assignment wins (``source`` semantics).

    Values are taken verbatim after the first ``=`` (minus surrounding quotes);
    no shell expansion or escape processing is performed, which is correct for
    opaque secret material (tokens, URLs, ids). Lines that are not a valid
    assignment are skipped.
    """
    pairs: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("export ", "export\t")):
            line = line[len("export") :].lstrip()
        name, sep, value = line.partition("=")
        if not sep:
            continue
        name = name.strip()
        if not _VALID_NAME_RE.match(name):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        pairs[name] = value
    return list(pairs.items())


def _read_secrets_source(file: str | None) -> str:
    """Read secrets text from a file path or stdin — no implicit default.

    Resolution:
      - ``file == "-"`` or piped stdin → read stdin
      - ``file`` is a path             → read that file
      - nothing given (interactive)    → usage error
    """
    if file == "-":
        return sys.stdin.read()
    if file is None:
        if sys.stdin.isatty():
            console.print(
                "[red]No input.[/red] Pass a file or pipe one in:\n"
                "  usvc_seller secrets upload FILE\n"
                "  <decrypt> | usvc_seller secrets upload"
            )
            raise typer.Exit(code=2)
        return sys.stdin.read()
    path = Path(file)
    if not path.is_file():
        console.print(f"[red]Secrets file not found:[/red] {file}")
        raise typer.Exit(code=1)
    return path.read_text()


def _print_upload_summary(rows: list[tuple[str, str]], output_format: str, *, dry_run: bool) -> None:
    """Render the per-secret outcome table (or JSON) plus a one-line tally."""
    if output_format == "json":
        console.print(json.dumps([{"name": n, "status": s} for n, s in rows], indent=2))
        return
    table = Table(title="Secrets (dry run)" if dry_run else "Secrets uploaded")
    table.add_column("Name", style="bold")
    table.add_column("Status", style="dim")
    for name, status in rows:
        table.add_row(name, status)
    console.print(table)
    n_set = sum(1 for _, s in rows if s in ("set", "would set"))
    n_skip = sum(1 for _, s in rows if s.startswith("skip"))
    verb = "would upload" if dry_run else "uploaded"
    summary = f"[green]✓[/green] {verb} {n_set} secret(s)"
    if n_skip:
        summary += f", skipped {n_skip} empty"
    console.print(summary)


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
# upload (bulk set from a sourceable file or stdin)
# ---------------------------------------------------------------------------
@app.command("upload")
def upload_secrets(
    file: str | None = typer.Argument(
        None,
        help=("Secrets file to read ('export NAME=value' lines), or '-' for stdin. Omit when piping input in."),
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Parse and list names; upload nothing."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Bulk-set secrets from a sourceable file or stdin (idempotent).

    Reads the same shell-sourceable file you keep for local testing — ``export
    NAME="value"`` / ``NAME=value`` lines, surrounding quotes stripped, ``#``
    comments and blank lines ignored — and sets each via
    ``PUT /v1/seller/secrets/{name}``. Entries with an empty value are skipped
    (fine for OPTIONAL secrets); when a name repeats, the last assignment wins.

    Input is a file or a pipe — no implicit default:

      - ``FILE`` argument — a path to a sourceable secrets file
      - ``-`` or piped stdin — decrypt on the fly, e.g.::

             sops -d .secrets | usvc_seller secrets upload
             gpg -d .secrets.gpg | usvc_seller secrets upload -
    """
    entries = _parse_secrets_text(_read_secrets_source(file))
    if not entries:
        console.print("[yellow]No secrets found in input.[/yellow]")
        raise typer.Exit(code=0)

    settable = [(n, v) for n, v in entries if v != ""]
    skipped = [n for n, v in entries if v == ""]

    if dry_run:
        rows = [(n, "would set") for n, _ in settable] + [(n, "skip (empty)") for n in skipped]
        _print_upload_summary(rows, output_format, dry_run=True)
        return

    async def _impl() -> list[str]:
        done: list[str] = []
        async with async_client(api_key, base_url) as client:
            for name, value in settable:
                await client.secrets.set(name, value)
                done.append(name)
        return done

    done = run_async(_impl(), error_prefix="Failed to upload secrets")
    rows = [(n, "set") for n in done] + [(n, "skip (empty)") for n in skipped]
    _print_upload_summary(rows, output_format, dry_run=False)


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
