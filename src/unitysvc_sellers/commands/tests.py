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
import os
import re
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from .._http import unwrap as _unwrap_response
from ..exceptions import NotFoundError
from ..utils import execute_script_content
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
_ROUTABLE_STATUSES = frozenset({"pending", "review", "active"})


def _resolve_interfaces(
    interfaces: list[dict[str, Any]],
) -> list[tuple[str, str, str, dict[str, Any]]]:
    """Extract ``(id, name, base_url, routing_key)`` tuples from the service's interfaces.

    The seller API resolves ``${API_GATEWAY_BASE_URL}`` placeholders
    before returning the interface data (see ``seller/services.py``),
    so ``base_url`` is already the public URL the seller should hit
    directly from their machine. Inactive interfaces are dropped.

    ``id`` (stringified access_interface UUID) is returned alongside
    the display ``name`` because test results on ``document.meta.test.tests``
    are keyed by interface id — a document may be shared across
    multiple services (active + draft revision of the same listing),
    so keying by id keeps each service's results addressable even when
    two services happen to share an interface name.
    """
    result: list[tuple[str, str, str, dict[str, Any]]] = []
    for iface in interfaces:
        iface_dict = iface if isinstance(iface, dict) else model_to_dict(iface)
        if not iface_dict.get("is_active", True):
            continue
        routing_key = iface_dict.get("routing_key") or {}
        if not isinstance(routing_key, dict):
            routing_key = {}
        result.append(
            (
                str(iface_dict.get("id") or ""),
                str(iface_dict.get("name", "default")),
                str(iface_dict.get("base_url") or ""),
                routing_key,
            )
        )
    # No silent fallback for an empty list. Appending a stub
    # ("", "default", "", {}) used to force the test to execute with
    # no SERVICE_BASE_URL set, recording a "SERVICE_BASE_URL is not
    # set" failure keyed by the literal string "default" — confusing
    # garbage. Callers skip the document cleanly instead.
    return result


def _make_exec_env(user_api_key: str) -> dict[str, str]:
    """Build the env the test runner exposes to rendered scripts.

    Only ``UNITYSVC_API_KEY`` is injected — every other field
    (``service_base_url``, ``routing_key.*``, ``host``, ``region``, …) is
    rendered into the script body at template-render time by the backend
    ``GET /seller/documents/{id}/render`` endpoint.  Keys are deliberately
    never inlined into rendered output, so the API key is the one value that
    has to come through env on every code path.
    """
    return {"UNITYSVC_API_KEY": user_api_key} if user_api_key else {}


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
    timeout: int = typer.Option(30, "--timeout", help="Per-script execution timeout in seconds."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Run a service's testable documents locally against the gateway.

    Ported from the legacy ``usvc services run-tests`` flow. Unlike the
    backend-dispatched execute path (Celery), this command pulls each
    document's rendered ``file_content`` from the backend and runs it
    on the seller's own machine, using ``UNITYSVC_API_KEY`` from the
    local environment and the interface's resolved ``base_url``.

    Because the gateway route resolver only accepts services in
    ``pending``, ``review``, or ``active`` status, the command
    temporarily elevates ``draft`` or ``rejected`` services to
    ``pending`` (with ``run_tests=False`` so the backend does not
    auto-queue its own Celery run) and restores the original status
    on exit. Per-interface results are POSTed back via
    ``PATCH /seller/documents/{id}`` so the document's ``meta.test``
    stays in sync with what the seller saw locally.
    """
    user_api_key = os.environ.get("UNITYSVC_API_KEY", "")

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            # 1. Resolve full service id + fetch detail (includes interfaces + docs).
            #    If a document_id was supplied without a service_id being
            #    a full UUID, we still need a service to elevate — so
            #    treat service_id as canonical here.
            detail = model_to_dict(await client.services.get(service_id))
            full_service_id = str(detail.get("service_id") or detail.get("id") or service_id)
            original_status = str(detail.get("status") or "")
            service_name = str(detail.get("service_name") or full_service_id[:8])

            docs_raw = detail.get("documents") or []
            docs = [d if isinstance(d, dict) else model_to_dict(d) for d in docs_raw]

            # Pick target documents.
            if document_id:
                target_docs = [d for d in docs if str(d.get("id", "")) == document_id]
                if not target_docs:
                    # Allow partial-id match on the requested doc.
                    target_docs = [d for d in docs if str(d.get("id", "")).startswith(document_id)]
            else:
                target_docs = [d for d in docs if _is_executable_doc(d)]

            if not target_docs:
                return {"docs": [], "original_status": original_status, "elevated": False}

            interfaces_raw = detail.get("interfaces") or []
            interfaces = [i if isinstance(i, dict) else model_to_dict(i) for i in interfaces_raw]
            interfaces_list = _resolve_interfaces(interfaces)

            # 2. Ensure service is routable before running tests. Only
            #    draft / rejected need elevation — pending / review /
            #    active already route correctly.
            elevated = False
            if original_status in ("draft", "rejected"):
                await client.services.update(
                    full_service_id,
                    {"status": "pending", "run_tests": False},
                )
                elevated = True

            # 3. Iterate docs, pulling file_content + running each
            #    interface. Results are collected per-document so we
            #    can POST them back in one PATCH after all interfaces
            #    run.
            doc_results: list[dict[str, Any]] = []
            try:
                for doc in target_docs:
                    did = str(doc.get("id", ""))
                    title = str(doc.get("title") or did[:8])

                    # Skip already-passed / skipped unless --force.
                    doc_test_status = _doc_test_status(doc)
                    if not force:
                        if doc_test_status == "success":
                            doc_results.append(
                                {
                                    "doc_id": did,
                                    "title": title,
                                    "status": "skipped",
                                    "reason": "already passed",
                                    "iface_results": {},
                                }
                            )
                            continue
                        if doc_test_status == "skip":
                            doc_results.append(
                                {
                                    "doc_id": did,
                                    "title": title,
                                    "status": "skipped",
                                    "reason": "marked as skip",
                                    "iface_results": {},
                                }
                            )
                            continue

                    full_doc = model_to_dict(await client.documents.get(did))
                    full_meta = full_doc.get("meta") or {}
                    output_contains = full_meta.get("output_contains") if isinstance(full_meta, dict) else None
                    fallback_mime = str(full_doc.get("mime_type") or "")

                    if not interfaces_list:
                        # No active interfaces to test against. The render
                        # endpoint requires an interface UUID for gateway
                        # mode, and rendering with no upstream config makes
                        # no sense for the seller — skip cleanly.
                        doc_results.append(
                            {
                                "doc_id": did,
                                "title": title,
                                "status": "skipped",
                                "reason": "service has no active interfaces",
                                "iface_results": {},
                            }
                        )
                        continue

                    # Preserve any prior entries written by sibling
                    # services that share this document — they're keyed
                    # by *their* interface ids so we won't clobber them,
                    # but we need to keep them in the payload since the
                    # backend overwrites the whole `tests` map.
                    prior = full_meta.get("test") if isinstance(full_meta, dict) else None
                    iface_results: dict[str, dict[str, Any]] = dict((prior or {}).get("tests") or {})
                    exec_env = _make_exec_env(user_api_key)
                    # ``iface_rk`` (routing_key) is unused now — the backend
                    # render endpoint inlines it into the script body, so
                    # there's no env-var to flatten it into anymore.
                    for iface_id, iface_name, iface_url, _iface_rk in interfaces_list:
                        key = iface_id or iface_name  # fallback if server didn't return an id

                        # Pull the interface-specific rendered script from the
                        # backend (``GET /seller/documents/{id}/render?interface=<uuid>``).
                        # The body has ``service_base_url`` / ``routing_key.*`` /
                        # any listing-level vars (``enrollment_vars`` / ``params`` /
                        # ``routing_vars``) inlined, so the rendered output is
                        # ready to execute as-is — no env-var injection beyond
                        # ``UNITYSVC_API_KEY``.
                        if not iface_id:
                            iface_results[key] = {
                                "name": iface_name,
                                "status": "task_failed",
                                "base_url": iface_url,
                                "env_vars": exec_env,
                                "error": (
                                    "Interface has no id — backend did not return one "
                                    "(cannot call /documents/{id}/render?interface=<uuid>)"
                                ),
                            }
                            continue

                        try:
                            rendered = await client.documents.render(did, interface=iface_id)
                        except Exception as render_err:  # noqa: BLE001
                            iface_results[key] = {
                                "name": iface_name,
                                "status": "task_failed",
                                "base_url": iface_url,
                                "env_vars": exec_env,
                                "error": f"Failed to render document for interface: {render_err}",
                            }
                            continue

                        rendered_dict = model_to_dict(rendered)
                        rendered_content = str(rendered_dict.get("content") or "")
                        rendered_mime = str(rendered_dict.get("mime_type") or fallback_mime)
                        if not rendered_content:
                            iface_results[key] = {
                                "name": iface_name,
                                "status": "task_failed",
                                "base_url": iface_url,
                                "env_vars": exec_env,
                                "error": "Render returned empty content",
                            }
                            continue

                        exec_result = execute_script_content(
                            script=rendered_content,
                            mime_type=rendered_mime,
                            env_vars=exec_env,
                            output_contains=str(output_contains) if output_contains else None,
                            timeout=timeout,
                        )
                        entry: dict[str, Any] = {
                            "name": iface_name,
                            "status": exec_result["status"],
                            "base_url": iface_url,
                            "env_vars": exec_env,
                            # Rendered script + mime captured here so the
                            # local failure-dump (below) can write the *exact*
                            # interface-specific script that ran, not a
                            # nominal pre-render template.
                            "rendered_content": rendered_content,
                            "rendered_mime_type": rendered_mime,
                        }
                        if exec_result.get("exit_code") is not None:
                            entry["exit_code"] = exec_result["exit_code"]
                        if exec_result.get("error"):
                            entry["error"] = exec_result["error"]
                        if exec_result.get("stdout"):
                            entry["stdout"] = exec_result["stdout"][:10000]
                        if exec_result.get("stderr"):
                            entry["stderr"] = exec_result["stderr"][:10000]
                        iface_results[key] = entry

                    # Aggregate per-interface outcome into a single
                    # document status — worst wins, restricted to *this*
                    # service's interfaces so a sibling revision's prior
                    # failure doesn't make our fresh success look bad.
                    this_service_keys = {(iid or name) for iid, name, _url, _rk in interfaces_list}
                    failed_entries = [
                        e for k, e in iface_results.items() if k in this_service_keys and e["status"] != "success"
                    ]
                    worst_status = failed_entries[0]["status"] if failed_entries else "success"

                    # POST results back to the backend. This keeps
                    # meta.test in sync with what the seller saw
                    # locally so `show-test` reflects the latest run.
                    try:
                        await client.documents.update_test(
                            did,
                            {"status": worst_status, "tests": iface_results},
                        )
                    except Exception as update_err:  # noqa: BLE001
                        # Non-fatal — surface a warning but keep going.
                        doc_results.append(
                            {
                                "doc_id": did,
                                "title": title,
                                "status": worst_status,
                                "iface_results": iface_results,
                                "service_name": service_name,
                                "update_warning": str(update_err),
                            }
                        )
                        continue

                    doc_results.append(
                        {
                            "doc_id": did,
                            "title": title,
                            "status": worst_status,
                            "iface_results": iface_results,
                            "service_name": service_name,
                        }
                    )
            finally:
                # 4. Restore original status if we changed it. Wrapped
                #    in try/except so a restore failure surfaces as a
                #    warning, not a hard crash that masks the test
                #    results.
                if elevated and original_status:
                    try:
                        await client.services.update(
                            full_service_id,
                            {"status": original_status, "run_tests": False},
                        )
                    except Exception as exc:  # noqa: BLE001
                        console.print(
                            f"[yellow]⚠  Failed to restore service status "
                            f"from 'pending' → '{original_status}': {exc}[/yellow]"
                        )

            return {
                "docs": doc_results,
                "original_status": original_status,
                "elevated": elevated,
            }

    outcome = run_async(_impl(), error_prefix="Failed to run tests")
    doc_results: list[dict[str, Any]] = outcome["docs"]

    if not doc_results:
        console.print("[dim]No testable documents found[/dim]")
        return

    if not user_api_key:
        console.print(
            "[yellow]⚠  UNITYSVC_API_KEY is not set in the local environment — "
            "scripts that call the gateway will see an empty bearer token.[/yellow]\n"
        )

    success = 0
    failed = 0
    skipped = 0
    for entry in doc_results:
        did = str(entry["doc_id"])
        short = did[:8] + "…"
        title = entry.get("title") or short
        status = entry["status"]

        if status == "skipped":
            reason = entry.get("reason") or "skipped"
            console.print(f"  [dim]⊘[/dim] {short} {title}: {reason}")
            skipped += 1
            continue

        if status == "success":
            console.print(f"  [green]✓[/green] {short} {title}: success")
            success += 1
        else:
            iface_results = entry.get("iface_results") or {}
            first_failure: dict[str, Any] = next(
                (r for r in iface_results.values() if r.get("status") != "success"),
                {},
            )
            err = first_failure.get("error") or status
            console.print(f"  [red]✗[/red] {short} {title}: {status} — {err}")
            failed += 1

            # Write script / stdout / stderr / env files for each
            # failing interface, mirroring usvc_seller data run-tests.
            #
            # Each interface ran its OWN rendered script (the backend renders
            # per-interface so ``service_base_url`` etc. match that
            # interface's gateway URL), so the failure dump pulls the
            # interface's ``rendered_content`` rather than a doc-level
            # script — the file the seller ``source``s + reruns is the
            # exact one that just failed.
            svc = re.sub(r"[^\w-]", "_", entry.get("service_name") or short)
            doc_slug = re.sub(r"[^\w-]", "_", title)
            for iface_entry in iface_results.values():
                if iface_entry.get("status") == "success":
                    continue
                iface_slug = re.sub(r"[^\w-]", "_", str(iface_entry.get("name") or "default"))
                base = f"failed_{svc}_{doc_slug}_{iface_slug}"
                iface_mime = iface_entry.get("rendered_mime_type") or ""
                ext = ".py" if "python" in iface_mime else ".sh"
                iface_script = iface_entry.get("rendered_content") or ""
                for path, content in [
                    (f"{base}{ext}", iface_script),
                    (f"{base}.out", iface_entry.get("stdout") or ""),
                    (f"{base}.err", iface_entry.get("stderr") or ""),
                ]:
                    try:
                        Path(path).write_text(content, encoding="utf-8")
                        console.print(f"      [yellow]→ saved:[/yellow] {path}")
                    except Exception as write_err:
                        console.print(f"      [yellow]⚠ could not write {path}: {write_err}[/yellow]")
                env_path = f"{base}.env"
                env_vars: dict[str, str] = iface_entry.get("env_vars") or {}
                try:
                    Path(env_path).write_text(
                        "".join(f"{k}={v}\n" for k, v in env_vars.items()),
                        encoding="utf-8",
                    )
                    console.print(f"      [yellow]→ saved:[/yellow] {env_path}")
                    console.print(f"      [dim]  (source to reproduce: source {env_path})[/dim]")
                except Exception as write_err:
                    console.print(f"      [yellow]⚠ could not write {env_path}: {write_err}[/yellow]")

        if entry.get("update_warning"):
            console.print(f"      [yellow](result upload failed: {entry['update_warning']})[/yellow]")

    total = len(doc_results)
    if total > 1:
        console.print(f"\n[green]✓ Success:[/green] {success}/{total}")
        if skipped:
            console.print(f"[dim]⊘ Skipped:[/dim] {skipped}/{total}")
        if failed:
            console.print(f"[red]✗ Failed:[/red] {failed}/{total}")
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
