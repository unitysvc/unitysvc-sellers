"""``usvc_seller services`` — remote service operations.

Ports the legacy ``usvc services`` command group from
``unitysvc-services``, but routed through the seller HTTP SDK
(:class:`unitysvc_sellers.AsyncClient`) instead of raw httpx calls.

Commands:

- ``list``      — query services with filtering / pagination
- ``show``      — show full detail for one service
- ``enable-testing`` — draft|rejected|suspended → pending, no tests (makes the
  service routable for on-wire testing; a pure status change)
- ``submit``    — draft|rejected|suspended → pending AND run the activation tests
- ``withdraw``  — pending|rejected → draft
- ``deprecate`` — mark services as deprecated
- ``set-visibility VISIBILITY`` — set visibility to ``public`` / ``unlisted`` / ``private``
- ``delete``    — permanently delete services
- ``update``    — set/remove routing vars and list price

The ``dedup`` subcommand from the legacy CLI is intentionally omitted:
the backing ``POST /v1/seller/services/dedup`` endpoint was removed in
the seller-api-codegen-hygiene cleanup. Use ``delete --all --status draft``
instead.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer
from rich.console import Console
from rich.table import Table

from ..exceptions import SellerSDKError

if TYPE_CHECKING:
    from ..aclient import AsyncClient
from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    fetch_service_ids_by_status,
    model_list,
    model_to_dict,
    resolve_service_id,
    run_async,
)

_LOCAL_IDS_OPTION = typer.Option(
    False,
    "--local-ids",
    "-l",
    help="Restrict to services whose IDs are recorded in listing_v1 files under --data-dir.",
)
_DATA_DIR_OPTION = typer.Option(
    Path("."),
    "--data-dir",
    help="Data directory for --local-ids (default: current directory).",
    exists=True,
    file_okay=False,
    dir_okay=True,
)
# The positional NAME argument used by every bulk and single-target services
# command — fnmatch on ``service_name`` (= listing.name, #1138).  A literal name
# targets the active row plus any pending revision via the backend's ``ids=``
# expansion; ``cohere/*`` targets the whole namespace.
_NAME_ARGUMENT = typer.Argument(
    None,
    help=(
        "Target services by service_name (= listing.name) — fnmatch pattern, e.g. "
        "'cohere/*' for a whole provider or a literal name.  Mutually exclusive "
        "with --id, --all, --local-ids."
    ),
)
# ``--id`` is the explicit override for the rare case where a name matches
# multiple rows (e.g. active + pending revision) and the operator needs to
# pin one specific row.
_ID_OPTION = typer.Option(
    None,
    "--id",
    help=(
        "Service ID (full or partial, ≥8 chars).  Use this when a name matches "
        "multiple rows and you need to pin one specific row.  Mutually exclusive "
        "with the positional NAME, --all, --local-ids."
    ),
)

console = Console()

app = typer.Typer(
    help="Remote service operations (list, show, submit, withdraw, deprecate, set-visibility, delete, update).",
)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
@app.command("list")
def list_services(
    limit: int = typer.Option(
        50,
        "--limit",
        help="Max records per page (cursor pagination; repeat with --cursor for more).",
    ),
    cursor: str | None = typer.Option(
        None,
        "--cursor",
        help="Continuation token from a previous page's next_cursor.",
    ),
    all_pages: bool = typer.Option(
        False,
        "--all",
        help="Follow cursors and print every page as one combined result.",
    ),
    name: str | None = typer.Argument(
        None,
        help=(
            "Optional name filter — search by name, display_name, or provider "
            "name (case-insensitive partial match against ``service.name`` on the "
            "backend).  Omit to list every service the seller owns."
        ),
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        help="Filter by service status (draft, pending, review, active, rejected, suspended, deprecated).",
    ),
    visibility: str | None = typer.Option(
        None,
        "--visibility",
        help="Filter by catalog visibility (public, unlisted, private).",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        help="Filter by provider name (case-insensitive partial match).",
    ),
    fields: str = typer.Option(
        "id,name,provider_name,service_type,status,visibility",
        "--fields",
        help="Comma-separated list of columns to display.",
    ),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    local_ids: bool = _LOCAL_IDS_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List services owned by the authenticated seller.

    Default mode uses cursor-based pagination over the seller's full
    catalog: pass ``--cursor`` for a specific page or ``--all`` to follow
    cursors to completion.

    With ``--local-ids``, only the services whose IDs are recorded in
    ``listing.{json,toml}`` (or the merged ``listing.override.{json,toml}``)
    files under ``--data-dir`` are fetched and shown — handy for
    inspecting just the services managed by the current data repo
    without a wildcard query against a shared seller account. The
    ``--status`` / ``--visibility`` / ``--name`` / ``--provider`` filters
    are applied server-side via the ``ids`` query parameter added in the
    backend ``GET /services?ids=<uuid>`` endpoint.
    """

    async def _impl() -> list[dict[str, Any]]:
        from uuid import UUID

        collected: list[dict[str, Any]] = []
        async with async_client(api_key, base_url) as client:
            if local_ids:
                raw_ids = _read_ids_from_data_dir(data_dir)
                if not raw_ids:
                    console.print(
                        "[yellow]No service IDs found in listing_v1 files under the given directory.[/yellow]"
                    )
                    return []
                uuid_ids = [UUID(sid) for sid in raw_ids]
                # Use the list endpoint with ids filter — single round-trip for the
                # typical case (<= 200 services), follows cursors automatically for
                # larger data dirs. All filters (status, visibility, name, provider)
                # are applied server-side, so the returned records are ServicePublic
                # with the correct field names for the table renderer.
                page_limit = min(len(uuid_ids), 200)
                current_cursor: str | None = None
                while True:
                    response = await client.services.list(
                        ids=uuid_ids,
                        limit=page_limit,
                        status=status,
                        visibility=visibility,
                        name=name,
                        provider=provider,
                        cursor=current_cursor,
                    )
                    collected.extend(model_list(response))
                    next_cursor = getattr(response, "next_cursor", None)
                    has_more = getattr(response, "has_more", False)
                    if not has_more or not next_cursor:
                        break
                    current_cursor = str(next_cursor)
                return collected

            current_cursor = cursor
            while True:
                response = await client.services.list(
                    cursor=current_cursor,
                    limit=limit,
                    status=status,
                    visibility=visibility,
                    name=name,
                    provider=provider,
                )
                collected.extend(model_list(response))
                if not all_pages:
                    break
                next_cursor = getattr(response, "next_cursor", None)
                has_more = getattr(response, "has_more", False)
                if not has_more or not next_cursor or isinstance(next_cursor, str) is False:
                    break
                current_cursor = str(next_cursor)

        return collected

    services = run_async(_impl(), error_prefix="Failed to list services")

    if not services:
        console.print("[dim]No services found[/dim]")
        return

    if output_format == "json":
        console.print(json.dumps(services, indent=2, default=str))
        return

    field_list = [f.strip() for f in fields.split(",")]
    table = Table(title="Services")
    for col in field_list:
        table.add_column(col, style="bold" if col == "name" else "")

    for svc in services:
        row = []
        for col in field_list:
            value = svc.get(col, "")
            if value is None:
                row.append("-")
            elif col == "id":
                row.append(str(value)[:8] + "…")
            else:
                row.append(str(value))
        table.add_row(*row)
    console.print(table)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------
def _resolve_single_target_id(
    api_key: str | None,
    base_url: str,
    *,
    name: str | None,
    service_id: str | None,
) -> str:
    """Resolve a single-target services command's selector to one id.

    Single-target commands (``show``, ``update``) want exactly one row.
    Multi-match on a name pattern is an error with a "use ``--id`` to
    disambiguate" hint; the ``--id`` path returns immediately (the
    operator pinned this row).
    """
    if (name is None) == (service_id is None):
        console.print("[red]Error:[/red] provide exactly one of a positional NAME or ``--id``.")
        raise typer.Exit(code=1)

    if service_id is not None:
        # Defer to the existing partial-UUID resolver — it handles
        # ambiguous prefixes and not-found with its own errors.
        async def _resolve_id() -> str:
            async with async_client(api_key, base_url) as client:
                return await resolve_service_id(client, service_id)

        return run_async(_resolve_id(), error_prefix="Failed to resolve --id")

    # The mutex check above guarantees name is not None when service_id is.
    assert name is not None
    name_value: str = name

    async def _resolve_one_by_name() -> str:
        # Backend (unitysvc#1201) now applies the strict ``*``/``%`` glob
        # grammar against ``service.name`` directly — every row in the
        # response is a genuine match, so no client-side narrowing step
        # is needed.  We just walk the cursor pages and collect the ids.
        matched: list[tuple[str, str]] = []
        cursor: str | None = None
        async with async_client(api_key, base_url) as client:
            while True:
                response = await client.services.list(name=name_value, limit=200, cursor=cursor)
                for svc in model_list(response):
                    row = svc if isinstance(svc, dict) else model_to_dict(svc)
                    row_name = row.get("name") or row.get("service_name")
                    if row.get("id"):
                        matched.append((str(row["id"]), str(row_name)))
                next_cursor = getattr(response, "next_cursor", None)
                has_more = getattr(response, "has_more", False)
                if not has_more or not next_cursor:
                    break
                cursor = str(next_cursor)
        if not matched:
            console.print(f"[red]Error:[/red] no service matches '{name_value}'.")
            raise typer.Exit(code=1)
        if len(matched) > 1:
            console.print(
                f"[red]Error:[/red] '{name_value}' matched {len(matched)} services — "
                f"use ``--id`` to disambiguate. Matches:"
            )
            for sid, nm in matched:
                console.print(f"  [dim]{sid[:8]}…[/dim] {nm}")
            raise typer.Exit(code=1)
        return matched[0][0]

    return run_async(_resolve_one_by_name(), error_prefix="Failed to resolve service by name")


@app.command("show")
def show_service(
    name: str | None = typer.Argument(
        None,
        help=(
            "Service to show, by service_name (= listing.name) — literal name or "
            "single-match fnmatch.  If multiple rows match (e.g. an active service "
            "plus its pending revision), the command errors and asks for --id."
        ),
    ),
    service_id: str | None = _ID_OPTION,
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show details of a single service, including documents and access interfaces."""
    service_id = _resolve_single_target_id(api_key, base_url, name=name, service_id=service_id)

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.services.get(service_id))

    service = run_async(_impl(), error_prefix="Failed to show service")

    if output_format == "json":
        console.print(json.dumps(service, indent=2, default=str))
        return

    # Identity table
    console.print("\n[bold]Service Identity[/bold]")
    id_table = Table(show_header=False, box=None)
    id_table.add_column("Field", style="cyan")
    id_table.add_column("Value")
    id_table.add_row("ID", str(service.get("service_id") or service.get("id") or "N/A"))
    id_table.add_row("Name", str(service.get("service_name") or service.get("name") or "N/A"))
    id_table.add_row("Status", str(service.get("status", "N/A")))
    if service.get("status_message"):
        id_table.add_row("Status message", str(service["status_message"]))
    if service.get("provider_name"):
        id_table.add_row("Provider", str(service["provider_name"]))
    if service.get("routing_vars"):
        id_table.add_row("Routing vars", json.dumps(service["routing_vars"]))
    console.print(id_table)

    # Documents
    documents = service.get("documents") or []
    if documents:
        console.print(f"\n[bold]Documents[/bold] ({len(documents)})")
        doc_table = Table()
        doc_table.add_column("ID", style="dim")
        doc_table.add_column("Title")
        doc_table.add_column("Category")
        doc_table.add_column("Status")
        for doc in documents:
            doc_dict = model_to_dict(doc) if not isinstance(doc, dict) else doc
            doc_table.add_row(
                str(doc_dict.get("id", ""))[:8],
                str(doc_dict.get("title", "")),
                str(doc_dict.get("category", "")),
                str(doc_dict.get("test_status") or ""),
            )
        console.print(doc_table)

    # Upstream channels (#1281/#1297): the offering's upstream_access_config,
    # one entry per channel, with the per-channel type + customer secrets the
    # backend stamps at ingest (#1305). Orthogonal to the user-facing access
    # interfaces below: a channel is *how the service reaches upstream*, an
    # interface is *how a customer reaches the service*.
    offering = service.get("offering")
    offering_dict = model_to_dict(offering) if offering and not isinstance(offering, dict) else (offering or {})
    channels = offering_dict.get("upstream_access_config") if isinstance(offering_dict, dict) else None
    if isinstance(channels, dict) and channels:
        console.print(f"\n[bold]Upstream Channels[/bold] ({len(channels)})")
        for ch_name, cfg in channels.items():
            if not isinstance(cfg, dict):
                continue
            ch_type = cfg.get("type")
            # The enrollable channel is the one that hosts enrollment.
            marker = "  [yellow](enrollment channel)[/yellow]" if ch_type == "enrollable" else ""
            type_label = f" [dim]({ch_type})[/dim]" if ch_type else ""
            console.print(f"  • [cyan]{ch_name}[/cyan]{type_label}{marker}")
            if cfg.get("access_method"):
                console.print(f"      access_method: {cfg['access_method']}")
            required = cfg.get("customer_secrets_required")
            if required:
                console.print(f"      customer_secrets_required: {', '.join(required)}")
            optional = cfg.get("customer_secrets_optional")
            if optional:
                names = ", ".join(
                    str(o.get("name")) if isinstance(o, dict) else str(o) for o in optional
                )
                console.print(f"      customer_secrets_optional: {names}")

    # Interfaces
    interfaces = service.get("interfaces") or []
    if interfaces:
        console.print(f"\n[bold]Access Interfaces[/bold] ({len(interfaces)})")
        for iface in interfaces:
            iface_dict = model_to_dict(iface) if not isinstance(iface, dict) else iface
            console.print(f"  • [cyan]{iface_dict.get('name', '?')}[/cyan]")
            for k, v in iface_dict.items():
                if k != "name" and v not in (None, ""):
                    console.print(f"      {k}: {v}")
    console.print()


# ---------------------------------------------------------------------------
# Bulk-status helpers
# ---------------------------------------------------------------------------
def _bulk_status_change(
    *,
    api_key: str | None,
    base_url: str,
    service_ids: list[str],
    status: str,
    success_verb: str,
    confirm_prompt: str,
    yes: bool,
) -> None:
    """Apply status change across many services with consistent UX."""
    count = len(service_ids)
    if not yes:
        if not typer.confirm(confirm_prompt):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(code=0)

    async def _impl() -> list[tuple[str, Exception | None]]:
        results: list[tuple[str, Exception | None]] = []
        async with async_client(api_key, base_url) as client:
            for sid in service_ids:
                try:
                    await client.services.update(sid, {"status": status})
                    results.append((sid, None))
                except Exception as exc:  # noqa: BLE001
                    results.append((sid, exc))
        return results

    results = run_async(_impl(), error_prefix=f"{success_verb} failed")

    success = 0
    failed = 0
    for sid, err in results:
        if err is None:
            console.print(f"  [green]✓[/green] {sid}: {success_verb}")
            success += 1
        else:
            console.print(f"  [red]✗[/red] {sid}: {err}")
            failed += 1

    if count > 1:
        console.print(f"\n[green]✓ Success:[/green] {success}/{count}")
        if failed:
            console.print(f"[red]✗ Failed:[/red] {failed}/{count}")
            raise typer.Exit(code=1)


def _bulk_submit(
    *,
    api_key: str | None,
    base_url: str,
    service_ids: list[str],
    confirm_prompt: str,
    yes: bool,
) -> None:
    """Submit services for review via ``POST /services/{id}/submit``.

    Unlike :func:`_bulk_status_change` (a pure status PATCH), this validates
    each service and dispatches the activation test pipeline server-side.  A
    duplicate-content submit comes back as a 200 no-op whose ``message``
    explains why; an invalid service raises and is reported as a failure.
    """
    count = len(service_ids)
    if not yes:
        if not typer.confirm(confirm_prompt):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(code=0)

    async def _impl() -> list[tuple[str, Any | None, Exception | None]]:
        results: list[tuple[str, Any | None, Exception | None]] = []
        async with async_client(api_key, base_url) as client:
            for sid in service_ids:
                try:
                    resp = await client.services.submit_for_review(sid)
                    results.append((sid, resp, None))
                except Exception as exc:  # noqa: BLE001
                    results.append((sid, None, exc))
        return results

    results = run_async(_impl(), error_prefix="Submit failed")

    success = 0
    failed = 0
    for sid, resp, err in results:
        if err is None:
            detail = getattr(resp, "message", None) or getattr(resp, "status", "submitted")
            console.print(f"  [green]✓[/green] {sid}: {detail}")
            success += 1
        else:
            console.print(f"  [red]✗[/red] {sid}: {err}")
            failed += 1

    if count > 1:
        console.print(f"\n[green]✓ Success:[/green] {success}/{count}")
        if failed:
            console.print(f"[red]✗ Failed:[/red] {failed}/{count}")
            raise typer.Exit(code=1)


def _bulk_visibility_change(
    *,
    api_key: str | None,
    base_url: str,
    service_ids: list[str],
    visibility: str,
    success_verb: str,
    confirm_prompt: str,
    yes: bool,
) -> None:
    """Apply visibility change across many services with consistent UX."""
    count = len(service_ids)
    if not yes:
        if not typer.confirm(confirm_prompt):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(code=0)

    async def _impl() -> list[tuple[str, Exception | None]]:
        results: list[tuple[str, Exception | None]] = []
        async with async_client(api_key, base_url) as client:
            for sid in service_ids:
                try:
                    await client.services.update(sid, {"visibility": visibility})
                    results.append((sid, None))
                except Exception as exc:  # noqa: BLE001
                    results.append((sid, exc))
        return results

    results = run_async(_impl(), error_prefix=f"{success_verb} failed")

    success = 0
    failed = 0
    for sid, err in results:
        if err is None:
            console.print(f"  [green]✓[/green] {sid}: {success_verb}")
            success += 1
        else:
            console.print(f"  [red]✗[/red] {sid}: {err}")
            failed += 1

    if count > 1:
        console.print(f"\n[green]✓ Success:[/green] {success}/{count}")
        if failed:
            console.print(f"[red]✗ Failed:[/red] {failed}/{count}")
            raise typer.Exit(code=1)


def _read_ids_from_data_dir(data_dir: Path) -> list[str]:
    """Collect service_ids from every service folder's service.json under data_dir.

    Thin wrapper over the shared :func:`unitysvc_sellers.utils.read_local_service_ids`
    utility (kept for the module-internal callers and existing tests).
    """
    from ..utils import read_local_service_ids

    return read_local_service_ids(data_dir)


async def _filter_ids_by_state(
    client: AsyncClient,
    ids: list[str],
    *,
    statuses: list[str],
    visibilities: list[str] | None,
) -> tuple[list[str], list[tuple[str, str]]]:
    """Resolve eligible service ids for a state-restricted action.

    Uses the seller list endpoint with the ``ids`` filter (one round-trip,
    follows cursors for large data dirs).  Crucially, the backend expands
    ``ids`` to also include any service whose ``revision_of`` matches one
    of the requested ids (see backend PR #915), so submitting against a
    data dir of active services correctly picks up their pending draft
    revisions.  Status / visibility filtering is applied client-side
    against the returned set so callers can pass multiple acceptable
    statuses in one call.

    Returns:
        A ``(eligible, skipped)`` tuple. ``skipped`` only contains
        ``(id, reason)`` pairs for the rare list-endpoint failures
        (network / auth) — those are real problems the caller should
        surface. State / visibility mismatches are silently dropped;
        the summary ``Eligible: X of Y`` count makes the partition
        obvious without per-id noise.
    """
    from uuid import UUID

    uuid_ids = [UUID(sid) for sid in ids]
    # Page size is capped at 200 server-side; if the data dir + their
    # revisions exceed that we'll follow cursors below.
    page_limit = min(max(len(uuid_ids) * 2, 50), 200)

    eligible: list[str] = []
    skipped: list[tuple[str, str]] = []
    current_cursor: str | None = None
    try:
        while True:
            response = await client.services.list(
                ids=uuid_ids,
                limit=page_limit,
                cursor=current_cursor,
            )
            for svc in model_list(response):
                row = svc if isinstance(svc, dict) else model_to_dict(svc)
                status = (str(row.get("status") or "")) or None
                vis = (str(row.get("visibility") or "")) or None
                if status not in statuses:
                    continue
                if visibilities and vis not in visibilities:
                    continue
                sid = row.get("id")
                if sid:
                    eligible.append(str(sid))
            next_cursor = getattr(response, "next_cursor", None)
            has_more = getattr(response, "has_more", False)
            if not has_more or not next_cursor:
                break
            current_cursor = str(next_cursor)
    except SellerSDKError as exc:
        skipped.append(("?", f"could not list services: {exc}"))

    return eligible, skipped


def _resolve_or_fetch_ids(
    *,
    api_key: str | None,
    base_url: str,
    name: str | None,
    service_id: str | None,
    use_all: bool,
    statuses_when_all: list[str],
    provider: str | None,
    use_local_ids: bool = False,
    data_dir: Path = Path("."),
    visibilities_when_all: list[str] | None = None,
) -> list[str]:
    """Resolve the target service IDs from exactly one of four mutually exclusive sources.

    Sources (only one may be active):
    - positional ``name`` — resolve **all** backend services whose
      ``service_name`` (= listing.name, #1138) matches the given fnmatch
      pattern, then keep those in an eligible state. A literal name still
      maps to several rows (e.g. an active service plus its pending
      revision via the backend's ``ids=`` expansion); ``cohere/*`` maps
      to the whole namespace.
    - ``--id``: resolve a partial or full UUID via prefix match; returns
      exactly one row.  Used to pin a specific row when the name would
      match multiple (active + revision, etc.); **no status filter** is
      applied — the operator named this exact row, do it.
    - ``--all``: fetch from the API filtered server-side by
      status/visibility/provider, so only eligible services are returned.
    - ``--local-ids``: read IDs from listing_v1 files under ``data_dir``
      and resolve them via the seller list endpoint with the ``ids``
      filter (which the backend expands to also include any pending
      revisions of the requested ids — see backend PR #915). The same
      status/visibility filter ``--all`` would have applied server-side
      is then applied client-side against the returned set.

    ``visibilities_when_all`` further restricts the fetch to
    services whose current visibility is in the given list.
    """
    # --- strict mutual exclusivity ---
    modes = sum([name is not None, service_id is not None, use_all, use_local_ids])
    if modes != 1:
        console.print("[red]Error:[/red] provide exactly one of: positional NAME, --id, --all, --local-ids.")
        raise typer.Exit(code=1)

    # --- --id: single row via prefix match, no status filter ---
    if service_id is not None:

        async def _resolve_one() -> list[str]:
            async with async_client(api_key, base_url) as client:
                full_id = await resolve_service_id(client, service_id)
                return [full_id]

        return run_async(_resolve_one(), error_prefix="Failed to resolve --id")

    # --- --name: all backend rows whose service_name matches the pattern ---
    if name is not None:
        # Backend (unitysvc#1201) precise-matches ``service.name`` against
        # the strict ``*``/``%`` glob grammar, so every row returned is a
        # genuine name match.  We still apply the status / visibility
        # filters client-side because those are per-command policy (the
        # ``--all`` server-side filter doesn't apply when targeting by
        # name — the operator named these rows, action is gated on
        # whether they're currently eligible for the requested
        # transition).
        async def _fetch_by_name() -> list[str]:
            matched: list[str] = []
            cursor: str | None = None
            async with async_client(api_key, base_url) as client:
                while True:
                    response = await client.services.list(name=name, limit=200, cursor=cursor, provider=provider)
                    for svc in model_list(response):
                        row = svc if isinstance(svc, dict) else model_to_dict(svc)
                        if (str(row.get("status") or "") or None) not in statuses_when_all:
                            continue
                        if (
                            visibilities_when_all
                            and (str(row.get("visibility") or "") or None) not in visibilities_when_all
                        ):
                            continue
                        if row.get("id"):
                            matched.append(str(row["id"]))
                    next_cursor = getattr(response, "next_cursor", None)
                    has_more = getattr(response, "has_more", False)
                    if not has_more or not next_cursor:
                        break
                    cursor = str(next_cursor)
            return matched

        ids = run_async(_fetch_by_name(), error_prefix="Failed to fetch services by name")
        if not ids:
            console.print(f"[yellow]No services matching '{name}' match the required state for this action.[/yellow]")
            raise typer.Exit(code=0)
        console.print(f"[green]Found {len(ids)} service(s) matching '{name}'[/green]\n")
        return ids

    # --- --local-ids: local listing_v1 files ---
    if use_local_ids:
        from ..utils import read_local_service_ids

        ids = read_local_service_ids(data_dir, provider)
        if not ids:
            console.print("[yellow]No service IDs found in listing_v1 files under the given directory.[/yellow]")
            raise typer.Exit(code=0)
        console.print(f"[cyan]Found {len(ids)} service ID(s) from {data_dir}[/cyan]")

        # Mirror --all's server-side filter: fetch each and drop the ones
        # whose current status/visibility doesn't match what the action
        # is valid for.  Without this step the action runs on the whole
        # local set and the operator gets a wall of 400s for services
        # that were never going to be eligible (e.g. ``submit
        # --local-ids`` against a repo with already-active services
        # would always 400 on those).
        async def _filter_local() -> tuple[list[str], list[tuple[str, str]]]:
            async with async_client(api_key, base_url) as client:
                return await _filter_ids_by_state(
                    client,
                    ids,
                    statuses=statuses_when_all,
                    visibilities=visibilities_when_all,
                )

        eligible, skipped = run_async(
            _filter_local(),
            error_prefix="Failed to inspect service states",
        )
        for sid, reason in skipped:
            console.print(f"[dim]⊘ skipping[/dim] {sid[:8]}…: [dim]{reason}[/dim]")
        if not eligible:
            console.print("[yellow]No services in the data dir match the required state for this action.[/yellow]")
            raise typer.Exit(code=0)
        console.print(f"[green]Eligible: {len(eligible)} of {len(ids)} service(s)[/green]\n")
        return eligible

    # --- --all: remote API ---
    if use_all:
        msg = f"[cyan]Fetching services with status: {', '.join(statuses_when_all)}"
        if visibilities_when_all:
            msg += f", visibility: {', '.join(visibilities_when_all)}"
        if provider:
            msg += f" for provider '{provider}'"
        msg += "...[/cyan]"
        console.print(msg)

        async def _fetch() -> list[str]:
            async with async_client(api_key, base_url) as client:
                return await fetch_service_ids_by_status(
                    client,
                    statuses_when_all,
                    provider=provider,
                    visibilities=visibilities_when_all,
                )

        ids = run_async(_fetch(), error_prefix="Failed to fetch services")
        if not ids:
            console.print("[yellow]No matching services found.[/yellow]")
            raise typer.Exit(code=0)
        console.print(f"[green]Found {len(ids)} service(s)[/green]\n")
        return ids

    # Unreachable — the mutex check above guarantees exactly one mode is
    # active, and each mode returns from its own branch.
    raise AssertionError("unreachable: mutex check should have caught this")


# ---------------------------------------------------------------------------
# submit / withdraw / deprecate
# ---------------------------------------------------------------------------


@app.command("submit")
def submit_service(
    name: str | None = _NAME_ARGUMENT,
    service_id: str | None = _ID_OPTION,
    all_drafts: bool = typer.Option(
        False, "--all", help="Submit all draft, rejected, and suspended services."
    ),
    local_ids: bool = _LOCAL_IDS_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --local-ids is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Submit services for review (draft|rejected|suspended → pending).

    This validates each service and runs the activation test pipeline that
    drives ``review`` / ``active`` / ``rejected``.  To make a service routable
    *without* running tests — e.g. to test code examples on-wire while you
    iterate — use ``enable-testing`` instead.
    """
    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        name=name,
        service_id=service_id,
        use_all=all_drafts,
        statuses_when_all=["draft", "rejected", "suspended"],
        provider=provider,
        use_local_ids=local_ids,
        data_dir=data_dir,
    )
    _bulk_submit(
        api_key=api_key,
        base_url=base_url,
        service_ids=ids,
        confirm_prompt=f"Submit {len(ids)} service(s) for review?",
        yes=yes,
    )


@app.command("enable-testing")
def enable_testing_service(
    name: str | None = _NAME_ARGUMENT,
    service_id: str | None = _ID_OPTION,
    all_eligible: bool = typer.Option(
        False, "--all", help="Enable testing for all draft, rejected, and suspended services."
    ),
    local_ids: bool = _LOCAL_IDS_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --local-ids is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Make services routable for on-wire testing (draft|rejected|suspended → pending).

    A pure status change (status becomes ``pending``) that makes a service
    routable so you can test its code examples on-wire — e.g. with
    ``services run-tests`` — while you iterate.  It does **not** run the
    activation test pipeline and won't progress the service to ``active``; it is
    NOT a submission for review.  Use ``submit`` when you're ready for that.
    """
    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        name=name,
        service_id=service_id,
        use_all=all_eligible,
        statuses_when_all=["draft", "rejected", "suspended"],
        provider=provider,
        use_local_ids=local_ids,
        data_dir=data_dir,
    )
    _bulk_status_change(
        api_key=api_key,
        base_url=base_url,
        service_ids=ids,
        status="pending",
        success_verb="Enabled for testing",
        confirm_prompt=f"Enable testing for {len(ids)} service(s) (routable, no tests)?",
        yes=yes,
    )


@app.command("withdraw")
def withdraw_service(
    name: str | None = _NAME_ARGUMENT,
    service_id: str | None = _ID_OPTION,
    all_pending: bool = typer.Option(False, "--all", help="Withdraw all pending and rejected services."),
    local_ids: bool = _LOCAL_IDS_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --local-ids is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Withdraw services back to draft (pending|rejected → draft)."""
    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        name=name,
        service_id=service_id,
        use_all=all_pending,
        statuses_when_all=["pending", "rejected"],
        provider=provider,
        use_local_ids=local_ids,
        data_dir=data_dir,
    )
    _bulk_status_change(
        api_key=api_key,
        base_url=base_url,
        service_ids=ids,
        status="draft",
        success_verb="Withdrawn",
        confirm_prompt=f"Withdraw {len(ids)} service(s) to draft?",
        yes=yes,
    )


@app.command("deprecate")
def deprecate_service(
    name: str | None = _NAME_ARGUMENT,
    service_id: str | None = _ID_OPTION,
    all_active: bool = typer.Option(False, "--all", help="Deprecate all active services."),
    local_ids: bool = _LOCAL_IDS_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --local-ids is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Mark services as deprecated."""
    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        name=name,
        service_id=service_id,
        use_all=all_active,
        statuses_when_all=["active"],
        provider=provider,
        use_local_ids=local_ids,
        data_dir=data_dir,
    )
    _bulk_status_change(
        api_key=api_key,
        base_url=base_url,
        service_ids=ids,
        status="deprecated",
        success_verb="Deprecated",
        confirm_prompt=f"Mark {len(ids)} service(s) as deprecated?",
        yes=yes,
    )


# ---------------------------------------------------------------------------
# set-visibility
# ---------------------------------------------------------------------------
_VISIBILITIES: tuple[str, ...] = ("public", "unlisted", "private")

# Per-target visibility, the *other* visibilities the ``--all`` filter
# treats as candidates for change (everything except the target).
_OTHER_VISIBILITIES: dict[str, list[str]] = {
    "public": ["unlisted", "private"],
    "unlisted": ["public", "private"],
    "private": ["public", "unlisted"],
}

# Statuses where setting visibility is meaningful.  Visibility is a
# flag, not a transition — it persists through the entire lifecycle
# and only takes effect when the service reaches ``active``.  Setting
# ``visibility=public`` on a ``draft`` is the canonical "Pattern B"
# behaviour: the seller declares intent, the flag stays on the
# service through review, and the moment admin approves activation
# the service is in the public catalog.  ``deprecated`` is the
# terminal status where flipping visibility is a no-op (the service
# is permanently removed from routing), so we exclude it.
_VISIBILITY_TARGETABLE_STATUSES: list[str] = [
    "active",
    "draft",
    "pending",
    "rejected",
    "review",
    "suspended",
]


def _set_visibility_impl(
    *,
    visibility: str,
    name: str | None,
    service_id: str | None,
    all_active: bool,
    local_ids: bool,
    data_dir: Path,
    provider: str | None,
    yes: bool,
    api_key: str | None,
    base_url: str,
) -> None:
    """Shared implementation for the canonical ``set-visibility`` command
    and the deprecated ``publish`` / ``unlist`` / ``hide`` aliases."""
    if visibility not in _VISIBILITIES:
        console.print(
            f"[red]✗[/red] Invalid visibility {visibility!r}. Use one of: {', '.join(_VISIBILITIES)}.",
            style="bold red",
        )
        raise typer.Exit(code=2)

    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        name=name,
        service_id=service_id,
        use_all=all_active,
        statuses_when_all=_VISIBILITY_TARGETABLE_STATUSES,
        visibilities_when_all=_OTHER_VISIBILITIES[visibility],
        provider=provider,
        use_local_ids=local_ids,
        data_dir=data_dir,
    )
    _bulk_visibility_change(
        api_key=api_key,
        base_url=base_url,
        service_ids=ids,
        visibility=visibility,
        success_verb=f"Set to {visibility}",
        confirm_prompt=f"Set {len(ids)} service(s) to {visibility}?",
        yes=yes,
    )


@app.command("set-visibility")
def set_visibility(
    visibility: str = typer.Argument(
        ...,
        help="Target visibility: one of public, unlisted, private.",
        metavar="VISIBILITY",
    ),
    name: str | None = _NAME_ARGUMENT,
    service_id: str | None = _ID_OPTION,
    all_active: bool = typer.Option(
        False,
        "--all",
        help=(
            "Apply to every non-deprecated service (draft, pending, review, "
            "active, rejected, suspended) not already at the target "
            "visibility.  Status is irrelevant — visibility is a flag that "
            "persists through the lifecycle and only takes effect on "
            "``active``."
        ),
    ),
    local_ids: bool = _LOCAL_IDS_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --local-ids is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set the visibility of one or more services.

    ``VISIBILITY`` is one of:

    - ``public``   — service is listed in the public catalog (effective
      only once the service is in the ``active`` status; setting this
      on a draft service marks the *intent* to be public when the
      service is activated).
    - ``unlisted`` — accessible by direct link, hidden from public
      catalog browse views.
    - ``private``  — hidden from every catalog view; only the seller
      and admins can see it.

    This command is a pure flag flip on the visibility column.  It
    does not transition status, does not validate that the service
    *should* be at the requested visibility, and does not interact
    with any review workflow.
    """
    _set_visibility_impl(
        visibility=visibility,
        name=name,
        service_id=service_id,
        all_active=all_active,
        local_ids=local_ids,
        data_dir=data_dir,
        provider=provider,
        yes=yes,
        api_key=api_key,
        base_url=base_url,
    )


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------
@app.command("delete")
def delete_service(
    name: str | None = _NAME_ARGUMENT,
    service_id: str | None = _ID_OPTION,
    all_deletable: bool = typer.Option(
        False,
        "--all",
        help="Delete all deletable services (draft, pending, review, rejected).",
    ),
    local_ids: bool = _LOCAL_IDS_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    status: str | None = typer.Option(None, "--status", help="Restrict --all to a single deletable status."),
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --local-ids is set."
    ),
    dryrun: bool = typer.Option(False, "--dryrun", help="Show what would be deleted without doing it."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Permanently delete services.

    Only services that have **never been active** are deletable:
    ``draft``, ``pending``, ``review``, ``rejected``.  Services in
    ``active``, ``suspended``, or ``deprecated`` have an archived
    ``ServiceData`` history that the platform retains for audit
    purposes; the backend rejects delete attempts on those even when
    they're currently inactive.  Status changes don't recover
    deletability: a service that was once activated stays
    non-deletable forever, even after a round-trip through
    ``deprecated → active → deprecated``.
    """
    # Statuses for which the service has never reached ``active``,
    # i.e. no archived ``ServiceData`` row exists.  Kept in sync with
    # ``_check_service_deletable`` in
    # ``backend/app/api/routes/seller/services.py`` (which is the
    # source of truth — it checks the archived-history table rather
    # than the status enum, but in practice these are the only
    # statuses without history).
    deletable_statuses = ["draft", "pending", "review", "rejected"]
    if status:
        if status not in deletable_statuses:
            valid = ", ".join(deletable_statuses)
            console.print(f"[red]Error:[/red] Status '{status}' is not deletable. Use one of: {valid}")
            raise typer.Exit(code=1)
        statuses = [status]
    else:
        statuses = deletable_statuses

    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        name=name,
        service_id=service_id,
        use_all=all_deletable,
        statuses_when_all=statuses,
        provider=provider,
        use_local_ids=local_ids,
        data_dir=data_dir,
    )

    count = len(ids)
    if not yes and not dryrun:
        prompt = (
            f"⚠️  Permanently delete service '{ids[0]}' and all associated data?"
            if count == 1
            else f"⚠️  Permanently delete {count} services and all associated data?"
        )
        if not typer.confirm(prompt):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(code=0)

    async def _impl() -> list[tuple[str, Exception | None]]:
        results: list[tuple[str, Exception | None]] = []
        async with async_client(api_key, base_url) as client:
            for sid in ids:
                try:
                    await client.services.delete(sid, dryrun=dryrun)
                    results.append((sid, None))
                except Exception as exc:  # noqa: BLE001
                    results.append((sid, exc))
        return results

    results = run_async(_impl(), error_prefix="Delete failed")

    success = 0
    failed = 0
    for sid, err in results:
        if err is None:
            verb = "Would be deleted" if dryrun else "Deleted"
            console.print(f"  [green]✓[/green] {sid}: {verb}")
            success += 1
        else:
            console.print(f"  [red]✗[/red] {sid}: {err}")
            failed += 1

    if dryrun:
        console.print("\n[yellow]Dry-run mode: no actual deletions performed[/yellow]")

    if count > 1:
        console.print(f"[green]✓ Success:[/green] {success}/{count}")
        if failed:
            console.print(f"[red]✗ Failed:[/red] {failed}/{count}")
            raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------
def _parse_set_options(items: list[str], option_name: str) -> dict[str, Any]:
    """Parse ``--set-*`` options: try JSON object first, then fall back to ``key=value``."""
    result: dict[str, Any] = {}
    for item in items:
        item = item.strip()
        if item.startswith("{"):
            try:
                parsed = json.loads(item)
            except json.JSONDecodeError as exc:
                console.print(f"[red]Error:[/red] {option_name}: invalid JSON ({exc})")
                raise typer.Exit(code=1) from exc
            if not isinstance(parsed, dict):
                console.print(f"[red]Error:[/red] {option_name}: JSON must be an object")
                raise typer.Exit(code=1)
            result.update(parsed)
            continue
        if "=" not in item:
            console.print(f"[red]Error:[/red] {option_name} '{item}' must be JSON object or key=value")
            raise typer.Exit(code=1)
        key, _, raw = item.partition("=")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = raw
        result[key.strip()] = value
    return result


@app.command("update")
def update_service(
    name: str | None = typer.Argument(
        None,
        help=(
            "Service to update, by service_name (= listing.name) — literal name or "
            "single-match fnmatch.  If multiple rows match (e.g. an active service "
            "plus its pending revision), the command errors and asks for --id."
        ),
    ),
    service_id: str | None = _ID_OPTION,
    visibility: str | None = typer.Option(
        None,
        "--visibility",
        "-v",
        help="Set catalog visibility: public, unlisted, or private.",
    ),
    set_routing_var: list[str] = typer.Option(
        None,
        "--set-routing-var",
        help="Set routing var(s): key=value or JSON object '{...}' (repeatable).",
    ),
    remove_routing_var: list[str] = typer.Option(
        None,
        "--remove-routing-var",
        help="Remove a routing var by key or dotted path (repeatable).",
    ),
    load_routing_vars: str | None = typer.Option(
        None,
        "--load-routing-vars",
        help="Replace all routing vars from a JSON file.",
    ),
    set_price: list[str] = typer.Option(
        None,
        "--set-price",
        help="Set list_price: key=value, JSON '{...}', or plain number for constant pricing (repeatable).",
    ),
    remove_price_field: list[str] = typer.Option(
        None,
        "--remove-price-field",
        help="Remove a list_price field by key or dotted path (repeatable).",
    ),
    sync_price: bool = typer.Option(
        False,
        "--sync-price",
        help=(
            "Reset the service-level price override to the listing's list_price "
            "(source of truth) and clear any price-divergence warning. Mutually "
            "exclusive with --set-price / --remove-price-field."
        ),
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Update visibility, routing vars, and/or list price on a live service.

    All updates are sent in a single PATCH request.
    """
    service_id = _resolve_single_target_id(api_key, base_url, name=name, service_id=service_id)

    has_routing = bool(set_routing_var or remove_routing_var or load_routing_vars)
    has_price = bool(set_price or remove_price_field)

    if sync_price and has_price:
        console.print(
            "[red]--sync-price cannot be combined with --set-price / "
            "--remove-price-field[/red] (sync resets to the listing price)."
        )
        raise typer.Exit(code=1)

    if not has_routing and not has_price and not sync_price and not visibility:
        console.print(
            "[yellow]Nothing to do:[/yellow] provide --visibility,"
            " --set-routing-var, --remove-routing-var, --load-routing-vars,"
            " --set-price, --remove-price-field, or --sync-price"
        )
        raise typer.Exit(code=0)

    # Build unified update body
    update_body: dict[str, Any] = {}

    if sync_price:
        update_body["sync_price"] = True

    if visibility:
        valid = {"public", "unlisted", "private"}
        if visibility not in valid:
            console.print(f"[red]Invalid visibility '{visibility}'. Must be one of: {', '.join(sorted(valid))}[/red]")
            raise typer.Exit(code=1)
        update_body["visibility"] = visibility

    # Routing vars
    if has_routing:
        if load_routing_vars and not set_routing_var and not remove_routing_var:
            # Full replacement from file
            try:
                with open(load_routing_vars, encoding="utf-8") as f:
                    loaded = json.load(f)
            except (OSError, json.JSONDecodeError) as exc:
                console.print(f"[red]Error:[/red] Failed to load {load_routing_vars}: {exc}")
                raise typer.Exit(code=1) from exc
            if not isinstance(loaded, dict):
                console.print("[red]Error:[/red] JSON file must contain an object (dict)")
                raise typer.Exit(code=1)
            update_body["routing_vars"] = loaded
        else:
            # Partial update via set/remove
            rv_body: dict[str, Any] = {}
            set_dict: dict[str, Any] = {}
            remove_list = list(remove_routing_var) if remove_routing_var else []

            if set_routing_var:
                set_dict.update(_parse_set_options(set_routing_var, "--set-routing-var"))
            if load_routing_vars:
                try:
                    with open(load_routing_vars, encoding="utf-8") as f:
                        loaded = json.load(f)
                except (OSError, json.JSONDecodeError) as exc:
                    console.print(f"[red]Error:[/red] Failed to load {load_routing_vars}: {exc}")
                    raise typer.Exit(code=1) from exc
                if not isinstance(loaded, dict):
                    console.print("[red]Error:[/red] JSON file must contain an object (dict)")
                    raise typer.Exit(code=1)
                set_dict.update(loaded)

            if set_dict:
                rv_body["set"] = set_dict
            if remove_list:
                rv_body["remove"] = remove_list
            if rv_body:
                update_body["routing_vars"] = rv_body

    # List price
    if has_price:
        price_dict: dict[str, Any] = {}
        price_remove = list(remove_price_field) if remove_price_field else []

        if set_price:
            for item in set_price:
                # Plain number shorthand → constant pricing
                if "=" not in item and not item.startswith("{"):
                    try:
                        float(item)
                        price_dict.update({"type": "constant", "price": item})
                        continue
                    except ValueError:
                        pass
                price_dict.update(_parse_set_options([item], "--set-price"))

        lp_body: dict[str, Any] = {}
        if price_dict:
            lp_body["set"] = price_dict
        if price_remove:
            lp_body["remove"] = price_remove
        if lp_body:
            update_body["list_price"] = lp_body

    if not update_body:
        console.print("[yellow]Nothing to do[/yellow]")
        raise typer.Exit(code=0)

    async def _update() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.services.update(service_id, update_body))

    result = run_async(_update(), error_prefix="Failed to update service")
    sid = result.get("id", service_id)

    if result.get("visibility"):
        console.print(f"[green]\u2713[/green] visibility={result['visibility']} for service {sid}")
    if result.get("routing_vars") is not None:
        console.print(f"[green]\u2713[/green] routing_vars updated for service {sid}")
        console.print(json.dumps(result["routing_vars"], indent=2))
    if result.get("list_price") is not None:
        console.print(f"[green]\u2713[/green] list_price updated for service {sid}")
        console.print(json.dumps(result["list_price"], indent=2))
    if result.get("message"):
        console.print(f"[green]\u2713[/green] {result['message']}")


# Suppress unused-import warning for SellerSDKError, kept available for callers.
__all__ = ["app", "SellerSDKError", "resolve_service_id"]
