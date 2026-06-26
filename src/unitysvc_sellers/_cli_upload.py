"""``usvc_seller specs upload`` — push a local seller catalog to the backend.

Thin Typer wrapper over :meth:`unitysvc_sellers.Client.upload`. Reads
credentials from the environment::

    UNITYSVC_SELLER_API_KEY    seller API key (svcpass_...)
    UNITYSVC_SELLER_API_URL   override the default https://seller.unitysvc.com

Or pass them as flags.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .client import DEFAULT_SELLER_API_URL, Client
from .exceptions import APIError

console = Console()


def upload(
    name: str | None = typer.Argument(
        None,
        help=(
            "Service to upload, by service_name (= listing.name) — fnmatch pattern, e.g. "
            "'cohere/*' or a literal name. Omit to upload every service in the current "
            "directory."
        ),
    ),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="UNITYSVC_SELLER_API_KEY",
        help="Seller API key (svcpass_...). Defaults to $UNITYSVC_SELLER_API_KEY.",
        show_default=False,
    ),
    base_url: str = typer.Option(
        DEFAULT_SELLER_API_URL,
        "--base-url",
        envvar="UNITYSVC_SELLER_API_URL",
        help="Backend base URL.",
    ),
    submit: bool = typer.Option(
        False,
        "--submit",
        help=(
            "Also submit each freshly published service for review (validate → pending → "
            "run tests) in the same ingest task. Default: leave services as reviewable "
            "drafts to submit later."
        ),
    ),
) -> None:
    """Upload service specs to UnitySVC.

    Use ``usvc_seller promotions upload`` and ``usvc_seller groups upload``
    for promotions and service groups.
    """
    if not api_key:
        console.print(
            "[red]✗[/red] Missing seller API key. Set $UNITYSVC_SELLER_API_KEY or pass --api-key.",
            style="bold red",
        )
        raise typer.Exit(code=1)

    data_dir = Path.cwd()

    console.print(f"[bold blue]Uploading from:[/bold blue] {data_dir}")
    console.print(f"[bold blue]Backend:[/bold blue] {base_url}")
    console.print()

    def _on_progress(kind: str, status: str, name: str, detail: str = "") -> None:
        if status == "queued":
            console.print(
                f"  [blue]↳[/blue] [blue]queued[/blue] [cyan]{name}[/cyan] [dim]({detail})[/dim]"
                if detail
                else f"  [blue]↳[/blue] [blue]queued[/blue] [cyan]{name}[/cyan]"
            )
        elif status == "ok":
            console.print(
                f"  [green]✓[/green] [green]ingested[/green] [cyan]{name}[/cyan] [dim]({detail})[/dim]"
                if detail
                else f"  [green]✓[/green] [green]ingested[/green] [cyan]{name}[/cyan]"
            )
        else:
            console.print(f"  [red]✗[/red] [red]failed[/red] [cyan]{name}[/cyan] — {detail}")

    try:
        with Client(api_key=api_key, base_url=base_url) as client:
            result = client.upload(data_dir, on_progress=_on_progress, name=name, auto_submit=submit)
    except APIError as exc:
        console.print(f"[red]✗[/red] API error: {exc}", style="bold red")
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        console.print(f"[red]✗[/red] Upload failed: {exc}", style="bold red")
        raise typer.Exit(code=1) from exc

    # ----- Summary --------------------------------------------
    console.print()
    table = Table(title="Upload Summary", show_header=True, header_style="bold cyan", border_style="cyan")
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Success", justify="right", style="green")
    table.add_column("Failed", justify="right", style="red")
    table.add_row(
        "Services",
        str(result.services.success),
        str(result.services.failed) if result.services.failed else "",
    )
    console.print(table)

    # ----- Errors ---------------------------------------------------
    if result.services.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for err in result.services.errors:
            console.print(f"  [red]✗[/red] {err.get('file', '?')}")
            console.print(f"    {err.get('error', '?')}")

    if result.total_failed > 0:
        console.print(
            f"\n[yellow]⚠[/yellow]  Completed with {result.total_failed} failure(s)",
            style="bold yellow",
        )
        raise typer.Exit(code=1)

    console.print("\n[green]✓[/green] All uploads completed successfully", style="bold green")
