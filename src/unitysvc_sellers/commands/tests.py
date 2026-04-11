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
from ..exceptions import APIError, NotFoundError
from ..resources.upload import _format_polling_error
from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_list,
    model_to_dict,
    run_async,
)
from .services import app as services_app

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
                services = model_list(await client.services.list(limit=1000))
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

    Accepts either the positional ``DOCUMENT_ID`` or ``--document-id /
    -d / --doc-id``. Partial UUIDs (prefix of length ≥ 8) are resolved
    by walking the seller's services — mirrors ``list-tests`` so the
    IDs it prints can be pasted directly.
    """
    raw_id = document_id_arg or document_id_opt
    if not raw_id:
        console.print("[red]✗[/red] No document id provided (positional or --document-id).")
        raise typer.Exit(code=1)
    if len(raw_id) < 8:
        console.print("[red]✗[/red] Document id prefix must be at least 8 characters.")
        raise typer.Exit(code=1)

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            # Fast path: full UUID → single GET.
            if len(raw_id) == 36:
                return model_to_dict(await client.documents.get(raw_id))

            # Partial prefix → walk services the seller owns and match
            # on every executable document id. This mirrors list-tests.
            services = model_list(await client.services.list(limit=1000))
            matches: list[str] = []
            for svc in services:
                sid = str(svc.get("id") or "")
                if not sid:
                    continue
                try:
                    detail = model_to_dict(await client.services.get(sid))
                except NotFoundError:
                    continue
                for doc in detail.get("documents") or []:
                    doc_dict = doc if isinstance(doc, dict) else model_to_dict(doc)
                    did = str(doc_dict.get("id") or "")
                    if did.startswith(raw_id):
                        matches.append(did)

            if not matches:
                raise NotFoundError(f"No document with id prefix '{raw_id}'", status_code=404, detail=None)
            if len(matches) > 1:
                # Ambiguous prefix — surface all candidates so the seller
                # can rerun with a longer prefix.
                joined = ", ".join(m[:12] + "…" for m in matches[:5])
                raise ValueError(f"Prefix '{raw_id}' matches multiple documents: {joined}")

            return model_to_dict(await client.documents.get(matches[0]))

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
    table.add_row("status", _doc_test_status(doc))
    if doc.get("executed_at"):
        table.add_row("executed_at", str(doc["executed_at"]))
    if doc.get("skipped_at"):
        table.add_row("skipped_at", str(doc["skipped_at"]))
    console.print(table)

    # Per-interface results, if any.
    meta = doc.get("meta") or {}
    test = meta.get("test") if isinstance(meta, dict) else None
    tests = (test or {}).get("tests") if isinstance(test, dict) else None
    if tests:
        console.print("\n[bold]Per-interface results[/bold]")
        for iface_name, iface_data in tests.items():
            if not isinstance(iface_data, dict):
                continue
            console.print(f"  • [cyan]{iface_name}[/cyan]")
            for k in ("status", "exit_code", "stdout", "stderr", "error"):
                v = iface_data.get(k)
                if v not in (None, ""):
                    console.print(f"      {k}: {v}")
    console.print()


# ---------------------------------------------------------------------------
# run-tests
# ---------------------------------------------------------------------------
@services_app.command("run-tests")
def run_tests(
    service_id: str = typer.Argument(..., help="Service ID (full or partial, ≥8 chars)."),
    document_id: str | None = typer.Option(
        None,
        "--document-id",
        "-d",
        help="Run a single document instead of every executable doc on the service.",
    ),
    force: bool = typer.Option(False, "--force", help="Re-execute even if the document was previously skipped."),
    wait_timeout: float = typer.Option(
        300.0,
        "--wait-timeout",
        help="Max seconds to wait for Celery tasks to finish before declaring a timeout.",
    ),
    poll_interval: float = typer.Option(
        2.0,
        "--poll-interval",
        help="Seconds between task-status polls while waiting for completion.",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Trigger backend execution of a service's testable documents.

    Execution is asynchronous on the backend (Celery), so this command
    dispatches each document via ``POST /seller/documents/{id}/execute``
    and then polls ``/seller/tasks/batch-status`` until every queued task
    reaches a terminal state. The script status (``success``,
    ``script_failed``, ``unexpected_output``, ``task_failed``) is pulled
    from the task result and surfaced per-document, so a run that the
    worker rejected no longer shows up as a silent ``queued``.
    """

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            # 1. Resolve the set of documents to execute.
            if document_id:
                doc_ids: list[str] = [document_id]
            else:
                detail = model_to_dict(await client.services.get(service_id))
                docs = detail.get("documents") or []
                doc_ids = [
                    str((doc if isinstance(doc, dict) else model_to_dict(doc)).get("id"))
                    for doc in docs
                    if _is_executable_doc(doc if isinstance(doc, dict) else model_to_dict(doc))
                ]
                if not doc_ids:
                    return {"dispatch": [], "terminal": {}, "polling_error": None}

            # 2. Dispatch all executes, record the task_id per doc.
            dispatch: list[dict[str, Any]] = []
            pending: dict[str, str] = {}  # task_id -> doc_id
            for did in doc_ids:
                try:
                    response = model_to_dict(await client.documents.execute(did, force=force))
                except Exception as exc:  # noqa: BLE001
                    dispatch.append({"doc_id": did, "status": "error", "error": str(exc)})
                    continue

                status = str(response.get("status") or "")
                task_id = response.get("task_id")
                entry: dict[str, Any] = {
                    "doc_id": did,
                    "status": status,
                    "task_id": task_id,
                    "message": response.get("message"),
                }

                # The endpoint returns one of:
                #   - "queued"   → task was just apply_async'd
                #   - "running"  → a previous run is still in flight (same task_id)
                #   - "success"  → cached hit, no task dispatched (force=False path)
                #   - "skip"     → document has status=skip; nothing ran
                if status in ("queued", "running") and task_id:
                    pending[str(task_id)] = did
                dispatch.append(entry)

            if not pending:
                return {"dispatch": dispatch, "terminal": {}, "polling_error": None}

            # 3. Poll until every queued/running task reaches a terminal state.
            try:
                terminal = await client.tasks.wait_batch(
                    list(pending.keys()),
                    timeout=wait_timeout,
                    poll_interval=poll_interval,
                )
            except APIError as exc:
                return {
                    "dispatch": dispatch,
                    "terminal": {},
                    "polling_error": _format_polling_error(exc),
                    "pending": pending,
                }

            return {
                "dispatch": dispatch,
                "terminal": terminal,
                "polling_error": None,
                "pending": pending,
            }

    outcome = run_async(_impl(), error_prefix="Failed to run tests")
    dispatch: list[dict[str, Any]] = outcome["dispatch"]
    terminal: dict[str, dict[str, Any]] = outcome.get("terminal") or {}
    polling_error: str | None = outcome.get("polling_error")

    if not dispatch:
        console.print("[dim]No executable documents found[/dim]")
        return

    # If polling itself failed, surface the diagnostic once and mark
    # every still-queued doc as failed.
    if polling_error:
        console.print(f"[red]✗ Task polling failed:[/red] {polling_error}\n")

    success = 0
    failed = 0
    for entry in dispatch:
        did = entry["doc_id"]
        short = did[:8] + "…"

        if entry["status"] == "error":
            console.print(f"  [red]✗[/red] {short}: {entry.get('error')}")
            failed += 1
            continue

        if entry["status"] == "skip":
            console.print(f"  [dim]⊘[/dim] {short}: skipped")
            continue

        if entry["status"] == "success" and not entry.get("task_id"):
            # Cached pre-existing success (force=False, already passed).
            console.print(f"  [green]✓[/green] {short}: success (cached)")
            success += 1
            continue

        task_id = str(entry.get("task_id") or "")
        if polling_error:
            console.print(f"  [red]✗[/red] {short}: polling failed (task_id={task_id})")
            failed += 1
            continue

        task_status = terminal.get(task_id) or {}
        poll_state = str(task_status.get("status") or "")

        if poll_state == "completed":
            # Unwrap the script-level status from task.result.
            task_result = task_status.get("result") or {}
            if isinstance(task_result, dict):
                script_status = str(task_result.get("status") or "success")
            else:
                script_status = "success"

            if script_status == "success":
                console.print(f"  [green]✓[/green] {short}: success")
                success += 1
            else:
                # task_failed / script_failed / unexpected_output — the
                # task itself reached Celery SUCCESS, but the script it
                # ran recorded a failure in document.meta.test.
                test_meta = task_result.get("test") or {} if isinstance(task_result, dict) else {}
                error_msg = test_meta.get("error") or task_result.get("error") or script_status
                console.print(f"  [red]✗[/red] {short}: {script_status} — {error_msg}")
                failed += 1
        elif poll_state == "failed":
            error_msg = task_status.get("error") or task_status.get("message") or "task failed"
            console.print(f"  [red]✗[/red] {short}: {error_msg}")
            failed += 1
        else:
            # wait_batch hit its timeout and the task is still running.
            console.print(f"  [yellow]…[/yellow] {short}: {poll_state or 'unknown'} (timed out)")
            failed += 1

    if len(dispatch) > 1:
        console.print(f"\n[green]✓ Success:[/green] {success}/{len(dispatch)}")
        if failed:
            console.print(f"[red]✗ Failed:[/red] {failed}/{len(dispatch)}")
    if failed:
        raise typer.Exit(code=1)


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
