"""``usvc seller specs upload`` — push a local seller catalog to the backend.

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
from rich.markup import escape
from rich.table import Table

from .client import DEFAULT_SELLER_API_URL, Client
from .exceptions import APIError

console = Console()

_DURATION_UNITS = {"s": 1, "m": 60, "h": 3600}


def parse_duration(text: str) -> float:
    """Seconds from ``90``, ``90s``, ``40m`` or ``2h``."""
    value = text.strip().lower()
    unit = 1
    if value and value[-1] in _DURATION_UNITS:
        unit, value = _DURATION_UNITS[value[-1]], value[:-1]
    try:
        seconds = float(value) * unit
    except ValueError:
        seconds = 0
    if seconds <= 0:
        raise typer.BadParameter(f"{text!r} is not a duration: use seconds, or a number with s, m or h (40m).")
    return seconds


def upload(
    name: str | None = typer.Argument(
        None,
        help=(
            "Service to upload, by service_name (= listing.name) or services/specs path — "
            "fnmatch pattern, e.g. 'cohere/*' or a literal name. Omit to upload every "
            "service in the current directory."
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
    state: Path | None = typer.Option(
        None,
        "--state",
        help=(
            "A state file recording, per service, the fingerprint of the expanded content last sent and the "
            "result of its ingest. A service unchanged since its ingest completed is skipped and its record "
            "kept; the file is created if missing and rewritten at the end. Keep it between runs (a CI "
            "artifact, a cache); without it every service is sent."
        ),
        show_default=False,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="With --state, ignore the recorded state and send every service (the file is still rewritten).",
    ),
    wait_for_test: str | None = typer.Option(
        None,
        "--wait-for-test",
        metavar="DURATION",
        help=(
            "With --submit, after the ingest wait up to DURATION (90, 90s, 40m, 2h) for the platform's "
            "activation tests on each submitted service, and exit 1 if any is rejected, errors or has no "
            "decision in time. A service whose upload queued no tests (unchanged, or a revision merged without "
            "them) gets the platform's check run on it instead (the container is started and its entries "
            "fetched), so every service that was sent has a decision. A service whose tests did not pass is "
            "sent again by the next --state run."
        ),
        show_default=False,
    ),
    report: Path | None = typer.Option(
        None,
        "--report",
        help="With --wait-for-test, write the platform's decision on each service to this file.",
        show_default=False,
    ),
    verify_remote: bool = typer.Option(
        True,
        "--verify-remote/--no-verify-remote",
        help=(
            "With --state, list the target's services once and send again any the state remembers but the "
            "target no longer has (a reset, a deletion). If the listing fails nothing is skipped."
        ),
    ),
) -> None:
    """Upload service specs to UnitySVC.

    Use ``usvc seller promotions upload`` and ``usvc seller groups upload``
    for promotions and service groups.
    """
    if not api_key:
        console.print(
            "[red]✗[/red] Missing seller API key. Set $UNITYSVC_SELLER_API_KEY or pass --api-key.",
            style="bold red",
        )
        raise typer.Exit(code=1)

    wait_seconds: float | None = None
    if wait_for_test is not None:
        if not submit:
            console.print(
                "[red]✗[/red] --wait-for-test needs --submit: only a submitted service has tests.", style="bold red"
            )
            raise typer.Exit(code=1)
        wait_seconds = parse_duration(wait_for_test)
    if report is not None and wait_seconds is None:
        console.print("[red]✗[/red] --report needs --wait-for-test.", style="bold red")
        raise typer.Exit(code=1)

    data_dir = Path.cwd()
    if state is not None and not state.is_absolute():
        # ``specs`` runs inside an ephemeral copy of the repo (param files rendered); a relative state path
        # is the user's, not that copy's, which is deleted when the command ends.
        from .params_render import invocation_cwd

        state = invocation_cwd() / state
    if report is not None and not report.is_absolute():
        from .params_render import invocation_cwd

        report = invocation_cwd() / report

    console.print(f"[bold blue]Uploading from:[/bold blue] {data_dir}")
    console.print(f"[bold blue]Backend:[/bold blue] {base_url}")
    console.print()

    def _on_progress(kind: str, status: str, name: str, detail: str = "") -> None:
        if kind == "test":
            if status == "ok":
                console.print(
                    f"  [green]✓[/green] [green]tests passed[/green] [cyan]{name}[/cyan] [dim]({escape(detail)})[/dim]"
                )
            else:
                console.print(f"  [red]✗[/red] [red]tests failed[/red] [cyan]{name}[/cyan] — {escape(detail)}")
        elif status == "queued":
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
        elif status == "skipped":
            console.print(f"  [yellow]⊘[/yellow] [yellow]skipped[/yellow] [cyan]{name}[/cyan] — {escape(detail)}")
        else:
            console.print(f"  [red]✗[/red] [red]failed[/red] [cyan]{name}[/cyan] — {escape(detail)}")

    try:
        with Client(api_key=api_key, base_url=base_url) as client:
            result = client.upload(
                data_dir,
                on_progress=_on_progress,
                name=name,
                auto_submit=submit,
                state=state,
                force=force,
                verify_remote=verify_remote,
                wait_for_test=wait_seconds,
            )
    except APIError as exc:
        console.print(f"[red]✗[/red] API error: {escape(str(exc))}", style="bold red")
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        console.print(f"[red]✗[/red] Upload failed: {escape(str(exc))}", style="bold red")
        raise typer.Exit(code=1) from exc

    for note in result.notes:
        console.print(f"[yellow]![/yellow] {escape(note)}")

    # ----- Summary --------------------------------------------
    console.print()
    table = Table(title="Upload Summary", show_header=True, header_style="bold cyan", border_style="cyan")
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Success", justify="right", style="green")
    table.add_column("Failed", justify="right", style="red")
    table.add_column("Skipped", justify="right", style="yellow")
    table.add_row(
        "Services",
        str(result.services.success),
        str(result.services.failed) if result.services.failed else "",
        str(result.services.skipped) if result.services.skipped else "",
    )
    console.print(table)

    # ----- Errors ---------------------------------------------------
    if result.services.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for err in result.services.errors:
            console.print(f"  [red]✗[/red] {escape(err.get('file', '?'))}")
            console.print(f"    {escape(err.get('error', '?'))}")

    if wait_seconds is not None:
        _show_tests(result, report)

    if result.tests_failed > 0 and result.total_failed == 0:
        console.print(
            f"\n[yellow]⚠[/yellow]  The platform did not accept {result.tests_failed} service(s)",
            style="bold yellow",
        )
        raise typer.Exit(code=1)

    if result.total_failed > 0:
        console.print(
            f"\n[yellow]⚠[/yellow]  Completed with {result.total_failed} failure(s)",
            style="bold yellow",
        )
        raise typer.Exit(code=1)

    if result.services.skipped:
        # Skipped services (--state: unchanged since their last ingest) are not failures, and are not
        # re-sent; saying only "all uploads completed" would hide that.
        console.print(
            f"\n[green]✓[/green] Uploaded {result.services.success}, "
            f"skipped {result.services.skipped} unchanged since the last upload "
            "(--force sends them anyway)",
            style="bold green",
        )
        return

    console.print("\n[green]✓[/green] All uploads completed successfully", style="bold green")


_TEST_MEANING = {
    "passed": "accepted",
    "rejected": "rejected by the platform's tests",
    "failed": "failed the platform's check",
    "error": "the platform's tests did not complete",
    "timeout": "no decision in time",
}


def _show_tests(result, report: Path | None) -> None:  # noqa: ANN001 - UploadResult
    """Print, and optionally write, the platform's decision on each service that was waited for."""
    lines = ["# Platform tests", ""]
    if not result.tests:
        lines.append("No uploaded service queued activation tests; nothing was waited for.")
    for outcome in result.tests:
        mark = "OK" if outcome.passed else "FAILED"
        lines.append(f"- {mark} {outcome.name}: {_TEST_MEANING.get(outcome.status, outcome.status)}")
        if not outcome.passed and outcome.detail:
            lines.extend(f"    {line}" for line in outcome.detail.splitlines())
    console.print()
    if not result.tests:
        console.print(f"[dim]{lines[-1]}[/dim]")
    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        console.print(f"[dim]Report written to {escape(str(report))}[/dim]")
