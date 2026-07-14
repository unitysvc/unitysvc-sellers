"""``usvc_seller files`` — seller account file browser (unitysvc#1533).

- ``usvc_seller files ls [PATH]``      — list one folder level
- ``usvc_seller files get KEY [DEST]`` — download a file
- ``usvc_seller files put SRC [PATH]`` — upload into a folder
- ``usvc_seller files url KEY``        — print a presigned URL

Paths and keys are relative to the seller's own folder (sellers have no
team structure, so there are no scopes). Upload and download bytes go
directly between this machine and storage — never through the UnitySVC
API. Distinct from ``usvc_seller upload``, which stores content-addressed
*documents* referenced by service listings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    run_async,
)

console = Console()

app = typer.Typer(
    help="Seller account files (ls, get, put, url).",
)


# ---------------------------------------------------------------------------
# ls
# ---------------------------------------------------------------------------
@app.command("ls")
def list_files(
    path: str = typer.Argument("", help="Folder path relative to your files root."),
    output_format: str = typer.Option("table", "--format", "-f", help="table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List one folder level of your account files."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            resp = await client.files.list(path)
            return {
                "folders": list(resp.common_prefixes),
                "files": [
                    {"key": o.key, "size": o.size, "last_modified": o.last_modified} for o in resp.objects
                ],
                "truncated": resp.is_truncated,
            }

    listing = run_async(_impl(), error_prefix="Failed to list files")

    if output_format == "json":
        console.print(json.dumps(listing, indent=2, default=str))
        return

    if not listing["folders"] and not listing["files"]:
        console.print("[dim]Empty folder[/dim]")
        return

    table = Table(title=f"Seller files — {path or '/'}")
    table.add_column("Name", style="bold")
    table.add_column("Size", justify="right")
    table.add_column("Modified")
    for folder in listing["folders"]:
        table.add_row(f"[cyan]{folder}[/cyan]", "—", "—")
    for f in listing["files"]:
        table.add_row(f["key"], str(f["size"]), str(f["last_modified"]))
    console.print(table)
    if listing.get("truncated"):
        console.print("[dim]Listing truncated — more files exist[/dim]")


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------
@app.command("get")
def get_file(
    key: str = typer.Argument(..., help="File key relative to your files root."),
    dest: Path | None = typer.Argument(None, help="Destination file or directory (default: basename in cwd)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Download one file (bytes stream storage → disk directly)."""

    async def _impl() -> Path:
        async with async_client(api_key, base_url) as client:
            return await client.files.download(key, dest)

    written = run_async(_impl(), error_prefix="Failed to download")
    console.print(f"[green]✓[/green] Downloaded [bold]{key}[/bold] → {written}")


# ---------------------------------------------------------------------------
# put
# ---------------------------------------------------------------------------
@app.command("put")
def put_file(
    src: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="Local file to upload."),
    path: str = typer.Argument("", help="Folder to upload into, e.g. exports or reports/2026."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Upload one file into a folder (bytes go disk → storage directly).

    The size ceiling is enforced by the server-signed upload policy;
    uploading to an existing name overwrites it.
    """

    async def _impl() -> str:
        async with async_client(api_key, base_url) as client:
            return await client.files.upload(src, path)

    key = run_async(_impl(), error_prefix="Failed to upload")
    console.print(f"[green]✓[/green] Uploaded [bold]{src.name}[/bold] → {key}")


# ---------------------------------------------------------------------------
# url
# ---------------------------------------------------------------------------
@app.command("url")
def presign_url(
    key: str = typer.Argument(..., help="File key relative to your files root."),
    expires_in: int = typer.Option(900, "--expires", help="URL validity in seconds (60-3600)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Print a short-TTL presigned download URL (for scripts / sharing)."""

    async def _impl() -> str:
        async with async_client(api_key, base_url) as client:
            resp = await client.files.download_url(key, expires_in=expires_in)
            return resp.url

    url = run_async(_impl(), error_prefix="Failed to presign")
    # Bare print: the URL is the output — keep it pipeable.
    print(url)
