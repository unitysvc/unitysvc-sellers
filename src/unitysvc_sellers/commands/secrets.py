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
import os
import re
import sys
from collections.abc import Mapping
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


# ``${NAME}`` / ``${NAME:-default}`` / ``${NAME-default}`` — the one expansion
# form the manifest resolves against the process environment. Anything else is
# taken verbatim (opaque secret material: tokens, URLs, ids).
_EXPANSION_RE = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)(?::?-(.*))?\}$")


def _resolve_rhs(rhs: str, environ: Mapping[str, str]) -> str:
    """Resolve one assignment's right-hand side.

    ``${NAME:-default}`` (or ``${NAME-default}`` / ``${NAME}``) uses the process
    env value for ``NAME`` when it is set and non-empty, else the default — the
    same ``source``-compatible semantics that let one file seed a seller's local
    test values AND, in CI, pick up GitHub-provided values. Any other RHS is
    taken verbatim (one layer of surrounding quotes stripped).
    """
    rhs = rhs.strip()
    if len(rhs) >= 2 and rhs[0] == rhs[-1] and rhs[0] in ("'", '"'):
        return rhs[1:-1]
    m = _EXPANSION_RE.match(rhs)
    if not m:
        return rhs
    name, default = m.group(1), m.group(2)
    env_val = environ.get(name)
    if env_val:
        return env_val
    return default if default is not None else ""


def _parse_secrets_text(text: str, environ: Mapping[str, str] | None = None) -> list[tuple[str, str, str | None]]:
    """Parse a ``.env``-style manifest into ``(name, value, description)`` triples.

    Accepts the same lines you would ``source`` in a shell — ``NAME=value`` or
    ``export NAME=value``. The contiguous ``#`` comment lines directly above a
    definition become its **description**; a blank line separates blocks, so a
    file header (comments followed by a blank line) attaches to no secret. The
    value is resolved by :func:`_resolve_rhs` — the ``${NAME:-default}`` form is
    environment-aware, everything else is verbatim. When a name is assigned more
    than once the last assignment (and its description) wins.
    """
    environ = os.environ if environ is None else environ
    values: dict[str, tuple[str, str | None]] = {}
    order: list[str] = []
    comments: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            comments = []  # blank line separates blocks
            continue
        if line.startswith("#"):
            comments.append(line.lstrip("#").strip())
            continue
        if line.startswith(("export ", "export\t")):
            line = line[len("export") :].lstrip()
        name, sep, rhs = line.partition("=")
        name = name.strip()
        if not sep or not _VALID_NAME_RE.match(name):
            comments = []
            continue
        description = "\n".join(comments).strip() or None
        if name not in values:
            order.append(name)
        values[name] = (_resolve_rhs(rhs, environ), description)
        comments = []
    return [(n, values[n][0], values[n][1]) for n in order]


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
    """Render the per-secret outcome table (or JSON) plus a one-line tally.

    ``status`` is ``set`` / ``would set``, suffixed ``(+desc)`` when the entry
    also carried a description.
    """
    if output_format == "json":
        console.print(json.dumps([{"name": n, "status": s} for n, s in rows], indent=2))
        return
    table = Table(title="Secrets (dry run)" if dry_run else "Secrets uploaded")
    table.add_column("Name", style="bold")
    table.add_column("Status", style="dim")
    for name, status in rows:
        table.add_row(name, status)
    console.print(table)
    n_desc = sum(1 for _, s in rows if "(+desc)" in s)
    verb = "would upload" if dry_run else "uploaded"
    summary = f"[green]✓[/green] {verb} {len(rows)} secret(s)"
    if n_desc:
        summary += f", {n_desc} with a description"
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
    table.add_row("description", str(secret.get("description") or "—"))
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
    description: str | None = typer.Option(
        None,
        "--description",
        "-d",
        help=(
            "Customer-facing guidance for this secret (Markdown) — what it is "
            "and how to obtain one. Stored on the row and shown to customers who "
            "must supply it. Omit to leave any existing description untouched."
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

    Pass ``--description`` to author the customer-facing guidance for the name;
    for many secrets at once, keep them in a ``.env.example`` manifest and use
    ``secrets upload``. Mirrors ``gh secret set`` and ``vault kv put``.
    """
    resolved_value = _resolve_value(value, name=name)

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.secrets.set(name, resolved_value, description=description))

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
    """Bulk-set secrets from an ``.env``-style manifest (idempotent).

    Reads a shell-sourceable ``.env.example`` — ``NAME=value`` / ``export
    NAME=value`` lines — and sets each via ``PUT /v1/seller/secrets/{name}``,
    with two conventions that make one file drive both local testing and
    customer-facing documentation:

    - **Environment-aware**: ``NAME=${NAME:-default}`` resolves ``NAME`` from the
      process environment when set, else the default. So the file reuses values
      already exported in your shell (and, in CI, GitHub-provided ones), falling
      back to test defaults. Opaque literals (``NAME=sk-abc``) are taken verbatim.
    - **Description-aware**: the contiguous ``#`` comment lines directly above a
      definition become that secret's ``description`` — the guidance surfaced to
      customers who must supply it (unitysvc#1618). A blank line ends a block, so
      a file header attaches to no secret.

    Every declared entry is set (source semantics: the manifest is authoritative),
    so an empty value still creates the row that carries its description. When a
    name repeats, the last assignment wins.

    Input is a file or a pipe — no implicit default:

      - ``FILE`` argument — a path to the manifest (e.g. ``.env.example``)
      - ``-`` or piped stdin — decrypt on the fly, e.g.::

             sops -d .secrets | usvc_seller secrets upload
             gpg -d .secrets.gpg | usvc_seller secrets upload -
    """
    entries = _parse_secrets_text(_read_secrets_source(file))
    if not entries:
        console.print("[yellow]No secrets found in input.[/yellow]")
        raise typer.Exit(code=0)

    def _status(description: str | None, *, done: bool) -> str:
        return ("set" if done else "would set") + (" (+desc)" if description else "")

    if dry_run:
        rows = [(n, _status(d, done=False)) for n, _v, d in entries]
        _print_upload_summary(rows, output_format, dry_run=True)
        return

    async def _impl() -> list[tuple[str, str | None]]:
        done: list[tuple[str, str | None]] = []
        async with async_client(api_key, base_url) as client:
            for name, value, description in entries:
                await client.secrets.set(name, value, description=description)
                done.append((name, description))
        return done

    done = run_async(_impl(), error_prefix="Failed to upload secrets")
    rows = [(n, _status(d, done=True)) for n, d in done]
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
