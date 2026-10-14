"""``usvc seller services {list,run,show,skip,unskip}-test(s)`` — document test ops.

These commands operate on backend ``Document`` records that represent
seller code-example or connectivity-test scripts. They use the
:class:`~unitysvc_sellers.AsyncClient`'s ``services`` and ``documents``
resources.

Test results are recorded per service by the platform's runners
(unitysvc#2628): ``GET /seller/services/{id}/test-results`` lists a
service's runs and its admission verdict, ``…/test-results/{run_id}/output``
serves one run's stdout/stderr/env/rendered script, and
``GET /seller/documents/{id}/test-details`` the latest run of a document.
A document's ``meta.test`` only carries the seller's skip flag.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from .._http import unwrap as _unwrap_response
from ..exceptions import NotFoundError
from ..utils import read_local_service_ids
from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_list,
    model_to_dict,
    run_async,
)
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


def _truncate_for_display(text: str, limit: int = 2000) -> str:
    """Cap long script/output text so the terminal doesn't drown."""
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [dim]({len(text) - limit} more chars truncated)[/dim]"


# Document categories that the backend treats as executable tests.
EXECUTABLE_CATEGORIES = {"code_example", "connectivity_test"}


def _is_executable_doc(doc: dict[str, Any]) -> bool:
    return (doc.get("category") or "") in EXECUTABLE_CATEGORIES


def _doc_statuses(results: dict[str, Any]) -> dict[str, str]:
    """Each document's test status for a service, from its test results.

    Gateway runs (through one of the service's interfaces) decide: the first
    failure, else ``success``. A document with no gateway run, or a required
    run still missing, is ``pending``; one the seller skipped is ``skip``.
    Upstream probes (no ``interface_id``) are attribution evidence only.
    """
    runs_by_doc: dict[str, list[dict[str, Any]]] = {}
    for run in results.get("runs") or []:
        runs_by_doc.setdefault(str(run.get("document_id")), []).append(run)
    statuses: dict[str, str] = {}
    for doc_id, runs in runs_by_doc.items():
        gateway = [r for r in runs if r.get("interface_id")]
        failed = [r for r in gateway if r.get("status") != "success"]
        statuses[doc_id] = "pending" if not gateway else str(failed[0].get("status")) if failed else "success"
    for gap in results.get("not_run") or []:
        doc_id = str(gap.get("document_id"))
        if statuses.get(doc_id, "success") == "success":
            statuses[doc_id] = "pending"
    for skipped in results.get("skipped") or []:
        statuses[str(skipped.get("document_id"))] = "skip"
    return statuses


# ---------------------------------------------------------------------------
# list-tests
# ---------------------------------------------------------------------------
@services_app.command("list-tests")
def list_tests(
    name: str | None = typer.Argument(
        None,
        help=(
            "Service to list tests for, by service_name (= listing.name) — literal "
            "name or single-match fnmatch.  If multiple rows match, the command "
            "errors and asks for --id.  Omit to list tests across every service."
        ),
    ),
    service_id: str | None = typer.Option(
        None,
        "--id",
        help="Service ID (full or partial, ≥8 chars).  Mutually exclusive with the positional NAME.",
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
    if name is not None and service_id is not None:
        console.print("[red]Error:[/red] positional NAME and --id are mutually exclusive.")
        raise typer.Exit(code=1)

    # Resolve the selector to a single service_id if one was provided.
    # Single-target semantics — multi-match name errors with a --id hint.
    if name is not None or service_id is not None:
        from .services import _resolve_single_target_id

        service_id = _resolve_single_target_id(api_key, base_url, name=name, service_id=service_id)

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
                    results = model_to_dict(await client.services.test_results(sid))
                except NotFoundError:
                    continue
                statuses = _doc_statuses(results)

                docs = [doc if isinstance(doc, dict) else model_to_dict(doc) for doc in detail.get("documents") or []]
                if results.get("platform_service_id"):
                    # A platform member is tested on its platform service's
                    # documents (unitysvc#2622), not its own: list those.
                    seen: dict[str, dict[str, Any]] = {}
                    for item in (results.get("runs") or []) + (results.get("not_run") or []):
                        doc_id = str(item.get("document_id"))
                        seen.setdefault(
                            doc_id,
                            {
                                "id": doc_id,
                                "title": item.get("document_title") or "",
                                "category": item.get("category") or "platform",
                            },
                        )
                    docs = list(seen.values())
                for doc_dict in docs:
                    if not all_docs and not _is_executable_doc(doc_dict) and not results.get("platform_service_id"):
                        continue
                    status = statuses.get(str(doc_dict.get("id")), "pending")
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

    async def _impl() -> tuple[dict[str, Any], dict[str, Any] | None]:
        # The backend's GET /seller/documents/{id} route already
        # accepts partial ids via complete_id() — a single indexed
        # prefix query on the document table resolves the UUID without
        # the client needing to enumerate services first.
        async with async_client(api_key, base_url) as client:
            doc = model_to_dict(await client.documents.get(raw_id))
            # The latest recorded run of the document by one of the
            # seller's services, with its output (unitysvc#2628). 404 means
            # it has never run.
            try:
                run = model_to_dict(await client.documents.test_details(str(doc["id"])))
            except NotFoundError:
                run = None
            return doc, run

    doc, run = run_async(_impl(), error_prefix="Failed to show test")

    if output_format == "json":
        console.print(json.dumps({**doc, "latest_run": run}, indent=2, default=str))
        return

    console.print(f"\n[bold]{doc.get('title', '?')}[/bold]")
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("id", str(doc.get("id", "")))
    table.add_row("category", str(doc.get("category", "")))
    table.add_row("mime_type", str(doc.get("mime_type", "")))
    meta = doc.get("meta") or {}
    test = meta.get("test") if isinstance(meta, dict) else None
    skipped = isinstance(test, dict) and test.get("status") == "skip"
    status = "skip" if skipped else str((run or {}).get("status") or "pending")
    status_color = "green" if status == "success" else "red" if status not in ("pending", "skip") else "yellow"
    table.add_row("status", f"[{status_color}]{status}[/{status_color}]")
    if doc.get("filename"):
        table.add_row("filename", str(doc["filename"]))
    if run and run.get("executed_at"):
        table.add_row("executed_at", str(run["executed_at"]))
    if run and run.get("exit_code") is not None:
        table.add_row("exit_code", str(run["exit_code"]))
    console.print(table)

    if run is None:
        console.print("\n[dim]No recorded run — use `usvc seller services run-tests` to run it.[/dim]\n")
        return
    _print_run_output(run)
    console.print(
        "\n[dim]Latest run across your services; per-service results: "
        "usvc seller services show-test-results <service>[/dim]\n"
    )


def _print_run_output(output: dict[str, Any]) -> None:
    """Print a run's error, streams, masked env and rendered script."""
    if output.get("expired"):
        console.print(
            "\n[yellow]output expired — re-run with `usvc seller services run-tests --force` to reproduce it[/yellow]"
        )
    if output.get("error"):
        console.print(f"\n[bold red]Error:[/bold red] {output['error']}")
    if output.get("stdout"):
        console.print("\n[bold]stdout:[/bold]")
        console.print(str(output["stdout"]))
    if output.get("stderr"):
        console.print("\n[bold]stderr:[/bold]")
        console.print(str(output["stderr"]))
    env = output.get("env")
    if isinstance(env, dict) and env:
        console.print("\n[bold]env:[/bold]")
        env_table = Table(show_header=False, box=None, padding=(0, 2))
        env_table.add_column("Key", style="cyan")
        env_table.add_column("Value")
        for k, v in env.items():
            env_table.add_row(k, str(v))
        console.print(env_table)
    if output.get("rendered_script"):
        console.print("\n[bold]rendered script (executed):[/bold]")
        console.print(_truncate_for_display(str(output["rendered_script"])))


# ---------------------------------------------------------------------------
# show-test-results
# ---------------------------------------------------------------------------
def _show_test_results(
    name: str | None,
    service_id: str | None,
    run_id: str | None,
    output_format: str,
    api_key: str | None,
    base_url: str,
) -> None:
    if (name is None) == (service_id is None):
        console.print("[red]Error:[/red] provide exactly one of: positional NAME or --id.")
        raise typer.Exit(code=1)
    from .services import _resolve_single_target_id

    sid = _resolve_single_target_id(api_key, base_url, name=name, service_id=service_id)

    async def _impl() -> tuple[dict[str, Any], dict[str, Any] | None]:
        async with async_client(api_key, base_url) as client:
            results = model_to_dict(await client.services.test_results(sid))
            output = None
            if run_id is not None:
                matches = [str(r["id"]) for r in results.get("runs") or [] if str(r["id"]).startswith(run_id)]
                if len(matches) != 1:
                    raise ValueError(
                        f"run id '{run_id}' matches {len(matches)} of this service's runs; "
                        "give more characters (see the run ids listed without --run)"
                    )
                output = model_to_dict(await client.services.test_run_output(sid, matches[0]))
            return results, output

    results, output = run_async(_impl(), error_prefix="Failed to show test results")

    if output_format == "json":
        console.print(json.dumps(output if output is not None else results, indent=2, default=str))
        return
    if output is not None:
        console.print(f"\n[bold]run {run_id}[/bold]: {output.get('status')} (exit {output.get('exit_code')})")
        _print_run_output(output)
        console.print()
        return

    if results.get("platform_service_id"):
        console.print(
            f"\nPlatform member of [bold]{results.get('platform_service_name')}[/bold] — tested on its "
            "documents through /p, pinned to this service."
        )
    verdict = "[green]passed[/green]" if results.get("passed") else f"[red]{results.get('error') or 'not passed'}[/red]"
    console.print(f"\nVerdict: {verdict}")

    runs = results.get("runs") or []
    if runs:
        table = Table(title="Runs")
        for col in ("run", "document", "interface", "channel", "status", "exit", "executed_at"):
            table.add_column(col)
        for r in runs:
            status = str(r.get("status"))
            color = "green" if status == "success" else "red"
            stale = " [yellow](stale)[/yellow]" if r.get("stale") else ""
            table.add_row(
                str(r.get("id", ""))[:8],
                str(r.get("document_title") or str(r.get("document_id", ""))[:8]),
                str(r.get("interface_id") or "")[:8] or "upstream",
                str(r.get("channel_name") or "-"),
                f"[{color}]{status}[/{color}]{stale}",
                "-" if r.get("exit_code") is None else str(r.get("exit_code")),
                str(r.get("executed_at") or "-"),
            )
        console.print(table)
    for gap in results.get("not_run") or []:
        console.print(f"[yellow]not run ({gap.get('reason')}):[/yellow] {gap.get('document_title')}")
    for skipped in results.get("skipped") or []:
        console.print(f"[dim]skipped:[/dim] {skipped.get('document_title')}")
    if runs:
        console.print("\n[dim]Output of a run: usvc seller services show-test-results <service> --run <run>[/dim]\n")


_RUN_OPTION_HELP = "Run id (or ≥8-char prefix) to print the output of: stdout, stderr, env, rendered script."


@services_app.command("show-test-results")
def show_test_results(
    name: str | None = typer.Argument(
        None,
        help="Service by service_name (= listing.name). Errors on multiple matches — use --id.",
    ),
    service_id: str | None = typer.Option(None, "--id", help="Service ID (full or partial, ≥8 chars)."),
    run_id: str | None = typer.Option(None, "--run", "-r", help=_RUN_OPTION_HELP),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show a service's test results: verdict, recorded runs, missing runs.

    Every runner (submission review, run-tests, single-document runs, the
    daily sweep) records its runs per service. A platform member's runs are
    of its platform service's documents, pinned to it.

        usvc seller services show-test-results cohere/command-r
        usvc seller services show-test-results --id 6c55d6d9 --run 1f2e3d4c
    """
    _show_test_results(name, service_id, run_id, output_format, api_key, base_url)


@services_app.command("show-platform-tests", hidden=True)
def show_platform_tests(
    name: str | None = typer.Argument(None, help="Platform member by service_name."),
    service_id: str | None = typer.Option(None, "--id", help="Service ID (full or partial, ≥8 chars)."),
    run_id: str | None = typer.Option(None, "--run", "-r", help=_RUN_OPTION_HELP),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Alias of ``show-test-results`` — the name platform-member rejection
    messages point at."""
    _show_test_results(name, service_id, run_id, output_format, api_key, base_url)


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


async def _resolve_service_ids_by_name(
    api_key: str | None, base_url: str, name: str
) -> list[tuple[str, str | None, str | None]]:
    """Resolve a ``--name`` fnmatch pattern to ``[(service_id, display_name,
    status), …]``.

    Trimmed-down sibling of ``services.py:_resolve_or_fetch_ids``'s
    name path.  We don't apply a status / visibility filter here —
    the caller decides (active services are skipped by default, see
    ``_skip_active``).  The seller list endpoint's ``ids=`` expansion
    already auto-includes pending revisions of matched parents, so a
    literal name targets the active row plus any draft revision under it.
    """
    # Backend (unitysvc#1201) precise-matches ``service.name`` against
    # the strict ``*``/``%`` glob grammar — every returned row is a
    # genuine match, so no client-side narrowing step is needed.
    matched: list[tuple[str, str | None, str | None]] = []
    cursor: str | None = None
    async with async_client(api_key, base_url) as client:
        while True:
            response = await client.services.list(name=name, limit=200, cursor=cursor)
            for svc in model_list(response):
                row = svc if isinstance(svc, dict) else model_to_dict(svc)
                row_name = row.get("name") or row.get("service_name")
                status = row.get("status")
                if row.get("id"):
                    matched.append((str(row["id"]), row_name, str(status) if status else None))
            next_cursor = getattr(response, "next_cursor", None)
            has_more = getattr(response, "has_more", False)
            if not has_more or not next_cursor:
                break
            cursor = str(next_cursor)
    return matched


def _skip_active(
    matched: list[tuple[str, str | None, str | None]],
) -> tuple[list[tuple[str, str | None]], list[tuple[str, str | None]]]:
    """Split name-matched rows into (targets, skipped_active).

    ACTIVE services are skipped by default — mirroring ``submit``, which also
    ignores them. An active service already passed its tests at activation,
    its content is frozen (re-uploads become revisions instead of mutating
    it), and the daily health sweep watches it for upstream drift — so
    re-testing it interactively spends real upstream calls for information
    we already have. When a name matches an active service plus its pending
    revision, this naturally tests only the revision. ``--include-active``
    (or pinning with ``--id``) restores active services.
    """
    targets = [(sid, n) for sid, n, status in matched if status != "active"]
    skipped = [(sid, n) for sid, n, status in matched if status == "active"]
    return targets, skipped


async def _resolve_document_by_filename(client: Any, service_id: str, test_file: str) -> str:
    """Resolve ``--test-file`` to a single document id for one service.

    Matches a document whose ``filename`` equals or ends with ``test_file``
    (mirrors ``specs run-tests --test-file`` suffix matching). Raises on no
    match or ambiguity so the caller surfaces a clear error.
    """
    detail = model_to_dict(await client.services.get(service_id))
    matches: list[dict[str, Any]] = []
    for doc in detail.get("documents") or []:
        d = doc if isinstance(doc, dict) else model_to_dict(doc)
        filename = str(d.get("filename") or "")
        if filename and (filename == test_file or filename.endswith(test_file)):
            matches.append(d)
    if not matches:
        raise ValueError(f"no document with filename matching '{test_file}' on service {service_id[:8]}")
    if len(matches) > 1:
        names = ", ".join(sorted(str(d.get("filename")) for d in matches))
        raise ValueError(f"--test-file '{test_file}' matches multiple documents ({names}); be more specific")
    return str(matches[0].get("id"))


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
    local_ids: bool = typer.Option(
        False,
        "--local-ids",
        "-l",
        help=(
            "Run tests for every service whose backend id is recorded in a "
            "service.json under --data-dir (the local specs/ catalog). Mutually "
            "exclusive with NAME and --id."
        ),
    ),
    data_dir: Path = typer.Option(
        Path("."),
        "--data-dir",
        help="Data directory for --local-ids (default: current directory).",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    document_id: str | None = typer.Option(
        None,
        "--document-id",
        "-d",
        help=(
            "Run a single document instead of every executable doc on the service. "
            "Accepts a full UUID or an 8+ character prefix (resolved like show-test)."
        ),
    ),
    test_file: str | None = typer.Option(
        None,
        "--test-file",
        "-t",
        help=(
            "Run only the document whose filename matches (e.g. 'code-example.py.j2'), "
            "resolved per service. Mirrors `specs run-tests --test-file`. Mutually "
            "exclusive with --document-id."
        ),
    ),
    category: str | None = typer.Option(
        None,
        "--category",
        help=(
            "Run only documents of this category ('connectivity_test' or "
            "'code_example') across every matched service — no need to look up a "
            "document id first. Composable across services (unlike --document-id, "
            "which is a single global id); mutually exclusive with --document-id "
            "and --test-file."
        ),
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Re-execute documents whose previous per-iface result was 'success'.",
    ),
    include_active: bool = typer.Option(
        False,
        "--include-active",
        help=(
            "Also test ACTIVE services. By default they are skipped (mirroring "
            "submit): an active service already passed its tests at activation, "
            "its content is frozen, and the daily health sweep monitors it — so "
            "a name matching an active service plus its pending revision tests "
            "only the revision, and a name matching only active services tests "
            "nothing. Pinning with --id always tests the pinned service."
        ),
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
    (unitysvc/unitysvc#1105).  Each run is recorded for the service on the
    backend; the rendered table here is a summary.  Use
    ``usvc seller services show-test-results <service> --run <run>`` to see
    full stdout/stderr for any failure.

    Targeting:
        usvc seller services run-tests cohere/command-r-plus
        usvc seller services run-tests 'cohere/*' --force
        usvc seller services run-tests --id 6c55d6d9              # disambiguate
        usvc seller services run-tests cohere/command-r -d 6c55d6d9   # one doc (id prefix ok)
        usvc seller services run-tests cohere/command-r -t code-example.py.j2  # one doc by filename
        usvc seller services run-tests 'cohere/*' --category connectivity_test --include-active
    """
    modes = sum([name is not None, service_id is not None, local_ids])
    if modes != 1:
        console.print("[red]Error:[/red] provide exactly one of: positional NAME, ``--id``, or ``--local-ids``.")
        raise typer.Exit(code=1)

    if document_id is not None and test_file is not None:
        console.print("[red]Error:[/red] --document-id and --test-file are mutually exclusive.")
        raise typer.Exit(code=1)
    if document_id is not None and len(document_id) < 8:
        console.print("[red]✗[/red] --document-id prefix must be at least 8 characters.")
        raise typer.Exit(code=1)
    if category is not None and (document_id is not None or test_file is not None):
        console.print("[red]Error:[/red] --category is mutually exclusive with --document-id and --test-file.")
        raise typer.Exit(code=1)
    if category is not None and category not in EXECUTABLE_CATEGORIES:
        console.print(f"[red]✗[/red] --category must be one of {sorted(EXECUTABLE_CATEGORIES)!r}; got {category!r}.")
        raise typer.Exit(code=1)

    if name is not None:
        matched = run_async(
            _resolve_service_ids_by_name(api_key, base_url, name),
            error_prefix="Failed to resolve services by name",
        )
        if not matched:
            console.print(f"[yellow]No services match '{name}'.[/yellow]")
            raise typer.Exit(code=0)
        if include_active:
            targets = [(sid, n) for sid, n, _status in matched]
            skipped_active: list[tuple[str, str | None]] = []
        else:
            targets, skipped_active = _skip_active(matched)
        console.print(f"[green]Found {len(matched)} service(s) matching '{name}'[/green]")
        for sid, n in skipped_active:
            console.print(
                f"[dim]Skipping active service {sid[:8]}… ({n}) — already "
                f"validated at activation; use --include-active or --id to test it.[/dim]"
            )
        if not targets:
            console.print(
                "[yellow]All matches are active services (skipped by default). "
                "Use --include-active to test them anyway.[/yellow]"
            )
            raise typer.Exit(code=0)
        console.print()
    elif local_ids:
        # Read backend ids from the local specs/ catalog; the diagnostic runs
        # per id with no status filter (mirrors ``--id`` — the operator pointed
        # at these services explicitly).
        ids = read_local_service_ids(data_dir)
        if not ids:
            console.print("[yellow]No service IDs found in service.json files under the given directory.[/yellow]")
            raise typer.Exit(code=0)
        console.print(f"[cyan]Found {len(ids)} service ID(s) from {data_dir}[/cyan]\n")
        targets = [(sid, None) for sid in ids]
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
                # Resolve the target document id. --test-file is per-service
                # (doc ids differ across services); --document-id is a global id
                # whose prefix we expand to a full UUID (the run-tests endpoint,
                # unlike GET /documents/{id}, does not complete prefixes itself).
                doc_id = document_id
                if test_file is not None:
                    doc_id = await _resolve_document_by_filename(client, _sid, test_file)
                elif document_id is not None:
                    resolved = model_to_dict(await client.documents.get(document_id))
                    doc_id = str(resolved.get("id"))
                return await client.services.run_tests(
                    _sid,
                    document_id=doc_id,
                    category=category,
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
            f"(see [bold]usvc seller services show-test-results <service>[/bold] "
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
    # Multi-channel services (#1281/#1297) probe each upstream channel; show
    # one line per channel when the per-channel breakdown is present, else
    # fall back to the singleton representative probe.
    channels = getattr(row, "upstream_channels", None)
    if channels:
        for ch_name, rec in channels.items():
            ustatus = (rec or {}).get("status")
            if ustatus == "success":
                console.print(f"      [dim]↳ upstream[{ch_name}]: success (platform fault)[/dim]")
            elif ustatus:
                console.print(f"      [dim]↳ upstream[{ch_name}]: {ustatus} (upstream fault)[/dim]")
    elif row.upstream:
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
__all__ = ["list_tests", "show_test", "show_test_results", "run_tests", "skip_test", "unskip_test"]
_unwrap_response  # noqa: B018  — keep import to make refactor easy
