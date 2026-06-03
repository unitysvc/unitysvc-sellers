"""``usvc_seller services {list,run,show,skip,unskip}-test`` — document test ops.

These commands operate on backend ``Document`` records that represent
seller code-example or connectivity-test scripts. They use the
:class:`~unitysvc_sellers.AsyncClient`'s ``services`` and ``documents``
resources.

The new ``/v1/seller/documents/{id}`` shape returned by the
seller-api-codegen-hygiene branch carries the test ``status`` and any
per-interface results inline (no separate ``/seller/documents/{id}/results``
fetch needed). The legacy CLI's much larger ``test_runner.py`` rendered
these results across multiple tables; this port aims for parity on
behavior, not on every cosmetic flourish — the JSON output format is
preserved verbatim so external tooling that consumed ``--format json``
keeps working.
"""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from .._http import unwrap as _unwrap_response
from ..exceptions import NotFoundError
from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_list,
    model_to_dict,
    run_async,
)
from .services import _NAME_OPTION
from .services import app as services_app

# Backend enforces ``limit <= 200`` on the cursor-paged services list.
# Use that as the page size when walking every service the seller owns.
_SERVICES_PAGE_LIMIT = 200


async def _iter_all_services(client: Any) -> list[dict[str, Any]]:
    """Yield every service the seller owns, paging via cursor.

    ``client.services.list`` caps ``limit`` at 200. Partial-UUID
    resolution and the no-argument form of ``list-tests`` both need
    the full catalog, so we drain pages until ``has_more`` is false.
    """
    collected: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        page = await client.services.list(cursor=cursor, limit=_SERVICES_PAGE_LIMIT)
        collected.extend(model_list(page))
        # CursorPage fields: next_cursor (None | str) and has_more.
        page_dict = model_to_dict(page)
        if not page_dict.get("has_more"):
            break
        cursor = page_dict.get("next_cursor")
        if not cursor:
            break
    return collected


console = Console()


# Document categories that the backend treats as executable tests.
EXECUTABLE_CATEGORIES = {"code_example", "connectivity_test"}


def _is_executable_doc(doc: dict[str, Any]) -> bool:
    return (doc.get("category") or "") in EXECUTABLE_CATEGORIES


def _doc_test_status(doc: dict[str, Any]) -> str:
    """Pull the test status off a document, defaulting to ``pending``."""
    # Top-level test_status (returned by the new ServiceDocumentItem shape)
    if doc.get("test_status"):
        return str(doc["test_status"])
    # Older / nested shape: meta.test.status
    meta = doc.get("meta") or {}
    test = meta.get("test") if isinstance(meta, dict) else None
    if isinstance(test, dict) and test.get("status"):
        return str(test["status"])
    return "pending"


# ---------------------------------------------------------------------------
# list-tests
# ---------------------------------------------------------------------------
@services_app.command("list-tests")
def list_tests(
    service_id: str | None = typer.Argument(
        None,
        help="Service ID (full or partial, ≥8 chars). If omitted, lists tests across all services.",
    ),
    all_docs: bool = typer.Option(False, "--all", "-a", help="Show all documents, not just executable tests."),
    status_filter: str | None = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by test status (success, script_failed, pending, …).",
    ),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List testable documents for one service or every service the seller owns."""

    async def _impl() -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        async with async_client(api_key, base_url) as client:
            if service_id:
                detail = model_to_dict(await client.services.get(service_id))
                full_id = str(detail.get("service_id") or detail.get("id") or service_id)
                svc_name = detail.get("service_name") or detail.get("name") or full_id[:8]
                services_to_walk: list[tuple[str, str]] = [(full_id, str(svc_name))]
            else:
                services = await _iter_all_services(client)
                services_to_walk = [
                    (str(s.get("id")), str(s.get("name") or s.get("id", "")[:8])) for s in services if s.get("id")
                ]

            for sid, sname in services_to_walk:
                try:
                    detail = model_to_dict(await client.services.get(sid))
                except NotFoundError:
                    continue

                docs = detail.get("documents") or []
                for doc in docs:
                    doc_dict = doc if isinstance(doc, dict) else model_to_dict(doc)
                    if not all_docs and not _is_executable_doc(doc_dict):
                        continue
                    status = _doc_test_status(doc_dict)
                    if status_filter and status != status_filter:
                        continue
                    rows.append(
                        {
                            "service_id": sid[:8] + "…" if sid else "-",
                            "service_name": sname,
                            "doc_id": str(doc_dict.get("id", ""))[:8] + "…",
                            "title": str(doc_dict.get("title", "")),
                            "category": str(doc_dict.get("category", "")),
                            "status": status,
                        }
                    )
        return rows

    rows = run_async(_impl(), error_prefix="Failed to list tests")

    if not rows:
        console.print("[dim]No tests found[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(rows, indent=2, default=str))
        return

    table = Table(title="Tests")
    for col in ("service_id", "service_name", "doc_id", "title", "category", "status"):
        table.add_column(col)
    for row in rows:
        table.add_row(*(row[c] for c in ("service_id", "service_name", "doc_id", "title", "category", "status")))
    console.print(table)


# ---------------------------------------------------------------------------
# show-test
# ---------------------------------------------------------------------------
@services_app.command("show-test")
def show_test(
    document_id_arg: str | None = typer.Argument(
        None,
        metavar="[DOCUMENT_ID]",
        help="Document ID (full or partial, ≥8 chars). Optional if --document-id/--doc-id is passed.",
    ),
    document_id_opt: str | None = typer.Option(
        None,
        "--document-id",
        "-d",
        "--doc-id",
        help="Document ID (alternative to positional). Matches the legacy `usvc services show-test --doc-id` form.",
    ),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show the latest test result for a single document.

    Accepts a document id — full UUID or an 8+ character prefix — via
    either the positional argument or ``--document-id / -d / --doc-id``.
    Prefix resolution is handled server-side by
    ``GET /seller/documents/{id}`` so the CLI makes exactly one API
    call regardless of how many services the seller owns.
    """
    raw_id = document_id_arg or document_id_opt
    if not raw_id:
        console.print("[red]✗[/red] No document id provided (positional or --document-id).")
        raise typer.Exit(code=1)
    if len(raw_id) < 8:
        console.print("[red]✗[/red] Document id prefix must be at least 8 characters.")
        raise typer.Exit(code=1)

    async def _impl() -> dict[str, Any]:
        # The backend's GET /seller/documents/{id} route already
        # accepts partial ids via complete_id() — a single indexed
        # prefix query on the document table resolves the UUID without
        # the client needing to enumerate services first.
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.documents.get(raw_id))

    doc = run_async(_impl(), error_prefix="Failed to show test")

    if output_format == "json":
        console.print(json.dumps(doc, indent=2, default=str))
        return

    console.print(f"\n[bold]{doc.get('title', '?')}[/bold]")
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("id", str(doc.get("id", "")))
    table.add_row("category", str(doc.get("category", "")))
    table.add_row("mime_type", str(doc.get("mime_type", "")))
    status = _doc_test_status(doc)
    status_color = "green" if status == "success" else "red" if status not in ("pending", "skip") else "yellow"
    table.add_row("status", f"[{status_color}]{status}[/{status_color}]")
    if doc.get("filename"):
        table.add_row("filename", str(doc["filename"]))
    if doc.get("executed_at"):
        table.add_row("executed_at", str(doc["executed_at"]))
    if doc.get("skipped_at"):
        table.add_row("skipped_at", str(doc["skipped_at"]))
    console.print(table)

    # meta.test holds the execution outcome recorded by the Celery
    # worker (exit_code, stdout, stderr, error, masked env vars).
    # These are the fields sellers actually need when a script fails,
    # so print them even though the top-level table doesn't include
    # them.
    meta = doc.get("meta") or {}
    test = meta.get("test") if isinstance(meta, dict) else None
    if isinstance(test, dict):
        if test.get("error"):
            console.print(f"\n[bold red]Error:[/bold red] {test['error']}")
        if test.get("exit_code") is not None:
            console.print(f"[cyan]exit_code:[/cyan] {test['exit_code']}")
        if test.get("stdout"):
            console.print("\n[bold]stdout:[/bold]")
            console.print(str(test["stdout"]))
        if test.get("stderr"):
            console.print("\n[bold]stderr:[/bold]")
            console.print(str(test["stderr"]))
        env = test.get("env")
        if isinstance(env, dict) and env:
            console.print("\n[bold]env:[/bold]")
            env_table = Table(show_header=False, box=None, padding=(0, 2))
            env_table.add_column("Key", style="cyan")
            env_table.add_column("Value")
            for k, v in env.items():
                env_table.add_row(k, str(v))
            console.print(env_table)

        # Per-interface results. The map is keyed by access_interface
        # id (stringified UUID) so results for documents shared across
        # multiple services don't collide; the human-friendly interface
        # name is carried inside each entry for display.
        tests = test.get("tests")
        if isinstance(tests, dict) and tests:
            console.print("\n[bold]Per-interface results[/bold]")
            for iface_key, iface_data in tests.items():
                if not isinstance(iface_data, dict):
                    continue
                display = iface_data.get("name") or iface_key
                console.print(f"  • [cyan]{display}[/cyan] [dim]({iface_key})[/dim]")
                for k in ("status", "exit_code", "stdout", "stderr", "error"):
                    v = iface_data.get(k)
                    if v not in (None, ""):
                        console.print(f"      {k}: {v}")

    # Script source — useful when the failure is "can't find file" or
    # an env-var interpolation bug. Truncate long files so the terminal
    # doesn't drown.
    file_content = doc.get("file_content")
    if file_content:
        console.print("\n[bold]file_content:[/bold]")
        text = str(file_content)
        if len(text) > 2000:
            text = text[:2000] + f"\n... [dim]({len(file_content) - 2000} more chars truncated)[/dim]"
        console.print(text)

    console.print()


# ---------------------------------------------------------------------------
# run-tests
# ---------------------------------------------------------------------------
# Replaced in unitysvc/unitysvc#1105: previously this command pulled
# each document's rendered script from ``GET /seller/documents/{id}/render``
# (now deleted), executed it locally with ``subprocess.run``, and POSTed
# results back via ``PATCH /seller/documents/{id}``.  The local-execution
# path went through the public ingress and tested what the seller's
# laptop could reach, not what the gateway sees from inside the cluster.
#
# The new path queues a server-side ``run_service_diagnostic`` celery
# task via the SDK wrapper ``client.services.run_tests(...)``, which
# polls ``/seller/tasks/{task_id}`` until the task completes and
# returns a typed :class:`RunTestsResult`.  This command is now a thin
# layer: parse typer args → call the SDK → render the result with rich.


async def _resolve_service_ids_by_name(api_key: str | None, base_url: str, name: str) -> list[tuple[str, str | None]]:
    """Resolve a ``--name`` fnmatch pattern to ``[(service_id, display_name), …]``.

    Trimmed-down sibling of ``services.py:_resolve_or_fetch_ids``'s
    name path.  We don't apply a status / visibility filter here —
    ``run-tests`` should attempt the diagnostic against whatever the
    user named and let the backend explain if the service can't be
    tested (e.g. no active interfaces).  The seller list endpoint's
    ``ids=`` expansion already auto-includes pending revisions of
    matched parents, so a literal name targets the active row plus
    any draft revision under it.
    """
    from ..utils import literal_pattern_prefix, service_name_matches

    server_hint = literal_pattern_prefix(name)
    matched: list[tuple[str, str | None]] = []
    cursor: str | None = None
    async with async_client(api_key, base_url) as client:
        while True:
            response = await client.services.list(name=server_hint, limit=200, cursor=cursor)
            for svc in model_list(response):
                row = svc if isinstance(svc, dict) else model_to_dict(svc)
                row_name = row.get("name") or row.get("service_name")
                if not service_name_matches(row_name, name):
                    continue
                if row.get("id"):
                    matched.append((str(row["id"]), row_name))
            next_cursor = getattr(response, "next_cursor", None)
            has_more = getattr(response, "has_more", False)
            if not has_more or not next_cursor:
                break
            cursor = str(next_cursor)
    return matched


@services_app.command("run-tests")
def run_tests(
    name: str | None = typer.Argument(
        None,
        help=(
            "Service(s) to test, by service_name (= listing.name) — fnmatch pattern, "
            "e.g. 'cohere/*' or a literal name. Matching multiple services runs the "
            "diagnostic once per match in sequence. Mutually exclusive with ``--id``."
        ),
    ),
    service_id: str | None = typer.Option(
        None,
        "--id",
        help=(
            "Service ID (full or partial, ≥8 chars).  Use this when a name matches "
            "multiple rows (e.g. an active service plus its pending revision) and you "
            "need to pin one specific row."
        ),
    ),
    document_id: str | None = typer.Option(
        None,
        "--document-id",
        "-d",
        help="Run a single document instead of every executable doc on the service.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Re-execute documents whose previous per-iface result was 'success'.",
    ),
    poll_interval: float = typer.Option(
        2.0,
        "--poll-interval",
        help="Seconds between task-status polls while waiting for the diagnostic.",
    ),
    timeout: float = typer.Option(
        600.0,
        "--timeout",
        help="Hard cap on total wait, including queue time, in seconds.",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Run a service's testable documents via a server-side diagnostic.

    Queues ``run_service_diagnostic`` on the backend, which renders and
    executes every executable document (connectivity tests + code
    examples) across every active access interface — inside the cluster,
    using the same network path customers hit — and falls back to an
    upstream-mode probe on any iface-level gateway failure so the
    result attributes the fault as ``platform_fault`` vs
    ``upstream_fault``.

    Replaces the previous local-execution path
    (unitysvc/unitysvc#1105).  Test results are persisted on the
    backend in ``Document.meta.test.tests[<iface_id>]``; the rendered
    table here is a summary.  Use ``usvc_seller services show-test --doc-id <id>``
    to see full stdout/stderr for any failure.

    Targeting:
        usvc_seller services run-tests cohere/command-r-plus
        usvc_seller services run-tests 'cohere/*' --force
        usvc_seller services run-tests --id 6c55d6d9          # disambiguate
    """
    if (name is None) == (service_id is None):
        console.print("[red]Error:[/red] provide exactly one of a positional NAME or ``--id``.")
        raise typer.Exit(code=1)

    if name is not None:
        targets = run_async(
            _resolve_service_ids_by_name(api_key, base_url, name),
            error_prefix="Failed to resolve services by name",
        )
        if not targets:
            console.print(f"[yellow]No services match '{name}'.[/yellow]")
            raise typer.Exit(code=0)
        console.print(f"[green]Found {len(targets)} service(s) matching '{name}'[/green]\n")
    else:
        # service_id is non-None — the mutex check above guarantees it.
        assert service_id is not None
        targets = [(service_id, None)]

    overall_exit = 0
    for sid, display_name in targets:
        if len(targets) > 1:
            label = display_name or sid
            console.print(f"\n[bold cyan]── {label} ──[/bold cyan]")

        async def _impl(_sid: str = sid) -> Any:
            async with async_client(api_key, base_url) as client:
                return await client.services.run_tests(
                    _sid,
                    document_id=document_id,
                    force=force,
                    poll_interval=poll_interval,
                    timeout=timeout,
                )

        try:
            result = run_async(_impl(), error_prefix="Failed to run tests")
        except typer.Exit as exc:
            overall_exit = max(overall_exit, getattr(exc, "exit_code", 1) or 1)
            continue
        rendered_exit = _render_run_tests_result(result)
        overall_exit = max(overall_exit, rendered_exit)

    if overall_exit:
        raise typer.Exit(code=overall_exit)


def _render_run_tests_result(result: Any) -> int:
    """Render one service's RunTestsResult; return a non-zero exit code on failure."""

    # ------------------------------------------------------------------
    # Render the result.  The SDK returns a typed RunTestsResult; we
    # display per-(doc × iface) rows and a summary at the bottom.
    # Group rows by document so a multi-iface failure shows up cleanly.
    # ------------------------------------------------------------------
    if result.status == "error":
        console.print(f"[red]✗[/red] Diagnostic task failed: {result.outcome or '(no detail)'}")
        return 1

    if result.outcome == "no_executable_documents":
        console.print("[dim]No testable documents found on this service.[/dim]")
        return 0

    if not result.results:
        console.print(f"[dim]Diagnostic completed with no rows (outcome={result.outcome or 'unknown'}).[/dim]")
        return 0

    # Per-row rendering.  Skipped → dim ⊘, success → green ✓, failure →
    # red ✗ with the outcome attribution (platform_fault / upstream_fault).
    from collections import defaultdict

    by_doc: dict[str, list[Any]] = defaultdict(list)
    for row in result.results:
        by_doc[row.document_id].append(row)

    for doc_id, rows in by_doc.items():
        short = (doc_id or "")[:8] + "…" if doc_id else "default"
        title = rows[0].document_title or short
        if len(rows) == 1:
            row = rows[0]
            _render_iface_row(row, prefix=f"  {short} {title}")
        else:
            console.print(f"  {short} {title}")
            for row in rows:
                _render_iface_row(row, prefix=f"    [{row.interface_name or 'default'}]")

    total = result.success_count + result.fail_count + result.skipped_count
    console.print()
    if result.success_count:
        console.print(f"[green]✓ Success:[/green] {result.success_count}/{total}")
    if result.skipped_count:
        console.print(f"[dim]⊘ Skipped:[/dim] {result.skipped_count}/{total}")
    if result.fail_count:
        console.print(
            f"[red]✗ Failed:[/red] {result.fail_count}/{total} "
            f"(see [bold]usvc_seller services show-test --doc-id <id>[/bold] "
            f"for full stdout/stderr)"
        )
        return 1
    return 0


def _render_iface_row(row: Any, *, prefix: str) -> None:
    """Render one per-(doc × iface) result row from a RunTestsResult."""
    status = row.status
    if status == "skipped":
        reason = row.outcome or "skipped"
        console.print(f"  [dim]⊘[/dim] {prefix}: {reason}")
        return
    if status == "success":
        console.print(f"  [green]✓[/green] {prefix}: success")
        return
    # Failure — surface the outcome attribution and a short error message.
    parts: list[str] = [status]
    if row.outcome and row.outcome != status:
        parts.append(row.outcome)
    if row.error:
        parts.append(str(row.error).splitlines()[0])
    detail = " — ".join(parts)
    console.print(f"  [red]✗[/red] {prefix}: {detail}")
    # When upstream fallback ran, show how it landed too — that's the
    # signal that distinguishes "platform broke" from "upstream broke".
    if row.upstream:
        ustatus = row.upstream.get("status")
        if ustatus == "success":
            console.print("      [dim]↳ upstream: success (platform fault)[/dim]")
        elif ustatus:
            console.print(f"      [dim]↳ upstream: {ustatus} (upstream fault)[/dim]")


# ---------------------------------------------------------------------------
# skip-test / unskip-test
# ---------------------------------------------------------------------------
def _set_test_status(
    document_id: str,
    *,
    new_status: str,
    api_key: str | None,
    base_url: str,
    success_verb: str,
) -> None:
    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.documents.update_test(document_id, {"status": new_status}))

    result = run_async(_impl(), error_prefix=f"Failed to {success_verb}")
    console.print(
        f"[green]✓[/green] {success_verb}: {result.get('id', document_id)} → {result.get('status', new_status)}"
    )


@services_app.command("skip-test")
def skip_test(
    document_id: str = typer.Argument(..., help="Document ID (full UUID)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Mark a code-example document as skipped (won't run)."""
    _set_test_status(
        document_id,
        new_status="skip",
        api_key=api_key,
        base_url=base_url,
        success_verb="skipped",
    )


@services_app.command("unskip-test")
def unskip_test(
    document_id: str = typer.Argument(..., help="Document ID (full UUID)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Unskip a previously-skipped document so it runs again."""
    _set_test_status(
        document_id,
        new_status="pending",
        api_key=api_key,
        base_url=base_url,
        success_verb="unskipped",
    )


# Quiet ruff about the imported _unwrap_response which we don't use directly here.
__all__ = ["list_tests", "show_test", "run_tests", "skip_test", "unskip_test"]
_unwrap_response  # noqa: B018  — keep import to make refactor easy
