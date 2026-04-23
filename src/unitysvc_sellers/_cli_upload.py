"""``usvc_seller data upload`` — push a local seller catalog to the backend.

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
    data_dir: Path | None = typer.Argument(
        None,
        help="Path to the seller catalog directory (default: current directory).",
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
    upload_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Upload only one resource: services / promotions / groups. Default: upload all three.",
    ),
) -> None:
    """Upload a seller catalog (services + promotions + service groups) to UnitySVC."""
    if not api_key:
        console.print(
            "[red]✗[/red] Missing seller API key. Set $UNITYSVC_SELLER_API_KEY or pass --api-key.",
            style="bold red",
        )
        raise typer.Exit(code=1)

    if data_dir is None:
        data_dir = Path.cwd()
    if not data_dir.exists():
        console.print(f"[red]✗[/red] Directory not found: {data_dir}", style="bold red")
        raise typer.Exit(code=1)

    valid_types = {"services", "promotions", "groups"}
    if upload_type and upload_type not in valid_types:
        console.print(
            f"[red]✗[/red] Invalid --type '{upload_type}'. Must be one of: {', '.join(sorted(valid_types))}",
            style="bold red",
        )
        raise typer.Exit(code=1)

    upload_services = upload_type in (None, "services")
    upload_promotions = upload_type in (None, "promotions")
    upload_groups = upload_type in (None, "groups")

    console.print(f"[bold blue]Uploading from:[/bold blue] {data_dir}")
    console.print(f"[bold blue]Backend:[/bold blue] {base_url}")
    console.print()

    def _on_progress(kind: str, status: str, name: str, detail: str = "") -> None:
        # Services are ingested asynchronously — ``POST /services``
        # returns ``202 Accepted`` with a task_id that the backend's
        # Celery worker drains. ``upload_directory`` polls the
        # ``/tasks/batch-status`` endpoint to resolve real per-service
        # outcomes, so each service progresses through
        # ``queued → ok`` or ``queued → error``. Promotions and
        # service-groups go through PUT and finish synchronously.
        if status == "queued":
            console.print(
                f"  [blue]↳[/blue] [blue]queued[/blue] {kind}: [cyan]{name}[/cyan] [dim]({detail})[/dim]"
                if detail
                else f"  [blue]↳[/blue] [blue]queued[/blue] {kind}: [cyan]{name}[/cyan]"
            )
        elif status == "ok":
            verb = "ingested" if kind == "service" else "upserted"
            console.print(f"  [green]✓[/green] [green]{verb}[/green] {kind}: [cyan]{name}[/cyan]")
        else:  # error / anything else
            console.print(f"  [red]✗[/red] [red]failed[/red] {kind}: [cyan]{name}[/cyan] — {detail}")

    try:
        with Client(api_key=api_key, base_url=base_url) as client:
            result = client.upload(
                data_dir,
                upload_services=upload_services,
                upload_promotions=upload_promotions,
                upload_groups=upload_groups,
                on_progress=_on_progress,
            )
    except APIError as exc:
        console.print(f"[red]✗[/red] API error: {exc}", style="bold red")
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        console.print(f"[red]✗[/red] Upload failed: {exc}", style="bold red")
        raise typer.Exit(code=1) from exc

    # ----- Summary table --------------------------------------------
    console.print()
    table = Table(title="Upload Summary", show_header=True, header_style="bold cyan", border_style="cyan")
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Success", justify="right", style="green")
    table.add_column("Failed", justify="right", style="red")

    for kind, counts in (
        ("Services", result.services),
        ("Promotions", result.promotions),
        ("Groups", result.groups),
    ):
        table.add_row(
            kind,
            str(counts.success),
            str(counts.failed) if counts.failed else "",
        )
    console.print(table)

    # ----- Errors ---------------------------------------------------
    all_errors = list(result.services.errors) + list(result.promotions.errors) + list(result.groups.errors)
    if all_errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for err in all_errors:
            console.print(f"  [red]✗[/red] {err.get('file', '?')}")
            console.print(f"    {err.get('error', '?')}")

    if result.total_failed > 0:
        console.print(
            f"\n[yellow]⚠[/yellow]  Completed with {result.total_failed} failure(s)",
            style="bold yellow",
        )
        raise typer.Exit(code=1)

    console.print("\n[green]✓[/green] All uploads completed successfully", style="bold green")
