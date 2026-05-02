"""``usvc_seller services`` — remote service operations.

Ports the legacy ``usvc services`` command group from
``unitysvc-services``, but routed through the seller HTTP SDK
(:class:`unitysvc_sellers.AsyncClient`) instead of raw httpx calls.

Commands:

- ``list``      — query services with filtering / pagination
- ``show``      — show full detail for one service
- ``submit``    — draft → pending (sets status='pending')
- ``withdraw``  — pending|rejected → draft
- ``deprecate`` — mark services as deprecated
- ``publish``   — set visibility to public
- ``unlist``    — set visibility to unlisted
- ``hide``      — set visibility to private
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
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ..exceptions import SellerSDKError
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

_FROM_DATA_OPTION = typer.Option(
    False, "--from-data",
    help="Act on services whose IDs are found in listing_v1 files under --data-dir.",
)
_DATA_DIR_OPTION = typer.Option(
    Path("."), "--data-dir",
    help="Data directory for --from-data (default: current directory).",
    exists=True, file_okay=False, dir_okay=True,
)

console = Console()

app = typer.Typer(
    help="Remote service operations (list, show, submit, withdraw, deprecate, publish, unlist, hide, delete, update).",
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
    name: str | None = typer.Option(
        None,
        "--name",
        "-n",
        help="Search by name, display_name, or provider name (case-insensitive partial match).",
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
    from_data: bool = _FROM_DATA_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List services owned by the authenticated seller.

    Default mode uses cursor-based pagination over the seller's full
    catalog: pass ``--cursor`` for a specific page or ``--all`` to follow
    cursors to completion.

    With ``--from-data``, only the services whose IDs are recorded in
    ``listing.{json,toml}`` (or the merged ``listing.override.{json,toml}``)
    files under ``--data-dir`` are fetched and shown — handy for
    inspecting just the services managed by the current data repo
    without a wildcard query against a shared seller account. The
    ``--status`` / ``--visibility`` / ``--name`` / ``--provider`` filters
    are then applied client-side; ``--cursor`` / ``--all`` / ``--limit``
    are ignored because the set is fixed.
    """

    async def _impl() -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        async with async_client(api_key, base_url) as client:
            if from_data:
                ids = _read_ids_from_data_dir(data_dir)
                if not ids:
                    console.print(
                        "[yellow]No service IDs found in listing_v1 files under the given directory.[/yellow]"
                    )
                    return []
                # Fetch each id concurrently. ``services.get`` returns a
                # ServiceDetailResponse whose to_dict() shape is a strict
                # superset of ServicePublic for the columns we render —
                # callers who pass --fields targeting only Public-shape
                # columns get the same output either way.
                import asyncio

                async def _fetch_one(sid: str) -> dict[str, Any] | None:
                    try:
                        return model_to_dict(await client.services.get(sid))
                    except SellerSDKError as exc:
                        console.print(
                            f"[yellow]⚠[/yellow] could not fetch service "
                            f"[cyan]{sid}[/cyan] (skipping): {exc}"
                        )
                        return None

                results = await asyncio.gather(*(_fetch_one(sid) for sid in ids))
                collected = [r for r in results if r is not None]

                # Apply remote-list filters client-side now that we have
                # the records. This makes ``--from-data --status active``
                # do exactly what the operator expects ("show me the
                # services in this repo that are currently active") even
                # though the backend list filters never ran.
                if status:
                    collected = [s for s in collected if s.get("status") == status]
                if visibility:
                    collected = [s for s in collected if s.get("visibility") == visibility]
                if name:
                    needle = name.lower()
                    collected = [
                        s
                        for s in collected
                        if needle in str(s.get("name") or "").lower()
                        or needle in str(s.get("display_name") or "").lower()
                        or needle in str(s.get("provider_name") or "").lower()
                    ]
                if provider:
                    p = provider.lower()
                    collected = [
                        s for s in collected if p in str(s.get("provider_name") or "").lower()
                    ]
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
@app.command("show")
def show_service(
    service_id: str = typer.Argument(..., help="Service ID (full or partial, ≥8 chars)."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show details of a single service, including documents and access interfaces."""

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
    """Collect service_ids from all listing_v1 files (with overrides merged) under data_dir."""
    from unitysvc_core.utils import find_files_by_schema

    ids: list[str] = []
    for _path, _fmt, data in find_files_by_schema(data_dir, "listing_v1"):
        sid = data.get("service_id")
        if sid:
            ids.append(str(sid))
    return ids


def _resolve_or_fetch_ids(
    *,
    api_key: str | None,
    base_url: str,
    service_ids: list[str] | None,
    use_all: bool,
    statuses_when_all: list[str],
    provider: str | None,
    flag_name: str,
    use_from_data: bool = False,
    data_dir: Path = Path("."),
    visibilities_when_all: list[str] | None = None,
) -> list[str]:
    """Resolve the target service IDs from exactly one of three mutually exclusive sources.

    Sources (only one may be active):
    - explicit positional ``service_ids``
    - ``--all``: fetch from the API filtered by status/visibility/provider.
    - ``--from-data``: read IDs from listing_v1 files under ``data_dir``;
      ``--provider`` filters by the ``provider_name`` field in each listing.

    ``visibilities_when_all`` further restricts the ``--all`` fetch to
    services whose current visibility is in the given list.
    """
    # --- strict mutual exclusivity ---
    modes = sum([bool(service_ids), use_all, use_from_data])
    if modes > 1:
        console.print(
            "[red]Error:[/red] --all, --from-data, and explicit service IDs are mutually exclusive. "
            "Provide exactly one."
        )
        raise typer.Exit(code=1)

    # --- --from-data: local listing_v1 files ---
    if use_from_data:
        ids = _read_ids_from_data_dir(data_dir)
        if provider:
            from unitysvc_core.utils import find_files_by_schema

            provider_lower = provider.lower()
            allowed = {
                str(data["service_id"])
                for _, _, data in find_files_by_schema(data_dir, "listing_v1")
                if provider_lower in (data.get("provider_name") or "").lower()
                and data.get("service_id")
            }
            ids = [i for i in ids if i in allowed]
        if not ids:
            console.print("[yellow]No service IDs found in listing_v1 files under the given directory.[/yellow]")
            raise typer.Exit(code=0)
        console.print(f"[cyan]Found {len(ids)} service ID(s) from {data_dir}[/cyan]\n")
        return ids

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

    # --- explicit IDs ---
    if provider:
        console.print("[red]Error:[/red] --provider requires --all or --from-data")
        raise typer.Exit(code=1)
    if not service_ids:
        console.print(
            f"[red]Error:[/red] Provide service IDs, --{flag_name}, or --from-data"
        )
        raise typer.Exit(code=1)
    return list(service_ids)


# ---------------------------------------------------------------------------
# submit / withdraw / deprecate
# ---------------------------------------------------------------------------


@app.command("submit")
def submit_service(
    service_ids: list[str] = typer.Argument(None, help="Service ID(s) to submit (≥8 chars)."),
    all_drafts: bool = typer.Option(False, "--all", help="Submit all draft and rejected services."),
    from_data: bool = _FROM_DATA_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --from-data is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Submit services for review (draft|rejected → pending)."""
    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        service_ids=service_ids,
        use_all=all_drafts,
        statuses_when_all=["draft", "rejected"],
        provider=provider,
        flag_name="all",
        use_from_data=from_data,
        data_dir=data_dir,
    )
    _bulk_status_change(
        api_key=api_key,
        base_url=base_url,
        service_ids=ids,
        status="pending",
        success_verb="Submitted",
        confirm_prompt=f"Submit {len(ids)} service(s) for review?",
        yes=yes,
    )


@app.command("withdraw")
def withdraw_service(
    service_ids: list[str] = typer.Argument(None, help="Service ID(s) to withdraw (≥8 chars)."),
    all_pending: bool = typer.Option(False, "--all", help="Withdraw all pending and rejected services."),
    from_data: bool = _FROM_DATA_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --from-data is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Withdraw services back to draft (pending|rejected → draft)."""
    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        service_ids=service_ids,
        use_all=all_pending,
        statuses_when_all=["pending", "rejected"],
        provider=provider,
        flag_name="all",
        use_from_data=from_data,
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
    service_ids: list[str] = typer.Argument(None, help="Service ID(s) to deprecate (≥8 chars)."),
    all_active: bool = typer.Option(False, "--all", help="Deprecate all active services."),
    from_data: bool = _FROM_DATA_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --from-data is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Mark services as deprecated."""
    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        service_ids=service_ids,
        use_all=all_active,
        statuses_when_all=["active"],
        provider=provider,
        flag_name="all",
        use_from_data=from_data,
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
# publish / unlist / hide
# ---------------------------------------------------------------------------
@app.command("publish")
def publish_service(
    service_ids: list[str] = typer.Argument(None, help="Service ID(s) to publish (≥8 chars)."),
    all_active: bool = typer.Option(
        False,
        "--all",
        help="Publish all active services that aren't already public.",
    ),
    from_data: bool = _FROM_DATA_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --from-data is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set visibility to public (visible in the catalog to all users)."""
    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        service_ids=service_ids,
        use_all=all_active,
        statuses_when_all=["active"],
        visibilities_when_all=["unlisted", "private"],
        provider=provider,
        flag_name="all",
        use_from_data=from_data,
        data_dir=data_dir,
    )
    _bulk_visibility_change(
        api_key=api_key,
        base_url=base_url,
        service_ids=ids,
        visibility="public",
        success_verb="Published",
        confirm_prompt=f"Set {len(ids)} service(s) to public?",
        yes=yes,
    )


@app.command("unlist")
def unlist_service(
    service_ids: list[str] = typer.Argument(None, help="Service ID(s) to unlist (≥8 chars)."),
    all_active: bool = typer.Option(
        False,
        "--all",
        help="Unlist all active services that aren't already unlisted.",
    ),
    from_data: bool = _FROM_DATA_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --from-data is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set visibility to unlisted (accessible by direct link, not shown in catalog)."""
    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        service_ids=service_ids,
        use_all=all_active,
        statuses_when_all=["active"],
        visibilities_when_all=["public", "private"],
        provider=provider,
        flag_name="all",
        use_from_data=from_data,
        data_dir=data_dir,
    )
    _bulk_visibility_change(
        api_key=api_key,
        base_url=base_url,
        service_ids=ids,
        visibility="unlisted",
        success_verb="Unlisted",
        confirm_prompt=f"Set {len(ids)} service(s) to unlisted?",
        yes=yes,
    )


@app.command("hide")
def hide_service(
    service_ids: list[str] = typer.Argument(None, help="Service ID(s) to hide (≥8 chars)."),
    all_active: bool = typer.Option(
        False,
        "--all",
        help="Hide all active services that aren't already private.",
    ),
    from_data: bool = _FROM_DATA_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --from-data is set."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Set visibility to private (hidden from all catalog views)."""
    ids = _resolve_or_fetch_ids(
        api_key=api_key,
        base_url=base_url,
        service_ids=service_ids,
        use_all=all_active,
        statuses_when_all=["active"],
        visibilities_when_all=["public", "unlisted"],
        provider=provider,
        flag_name="all",
        use_from_data=from_data,
        data_dir=data_dir,
    )
    _bulk_visibility_change(
        api_key=api_key,
        base_url=base_url,
        service_ids=ids,
        visibility="private",
        success_verb="Hidden",
        confirm_prompt=f"Hide {len(ids)} service(s) (set to private)?",
        yes=yes,
    )


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------
@app.command("delete")
def delete_service(
    service_ids: list[str] = typer.Argument(None, help="Service ID(s) to delete (≥8 chars)."),
    all_deletable: bool = typer.Option(
        False,
        "--all",
        help="Delete all deletable services (draft, pending, review, rejected, suspended, deprecated).",
    ),
    from_data: bool = _FROM_DATA_OPTION,
    data_dir: Path = _DATA_DIR_OPTION,
    status: str | None = typer.Option(None, "--status", help="Restrict --all to a single deletable status."),
    provider: str | None = typer.Option(
        None, "--provider", help="Filter by provider when --all or --from-data is set."
    ),
    dryrun: bool = typer.Option(False, "--dryrun", help="Show what would be deleted without doing it."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Permanently delete services."""
    deletable_statuses = ["draft", "pending", "review", "rejected", "suspended", "deprecated"]
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
        service_ids=service_ids,
        use_all=all_deletable,
        statuses_when_all=statuses,
        provider=provider,
        flag_name="all",
        use_from_data=from_data,
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
    service_id: str = typer.Argument(..., help="Service ID (full or partial, ≥8 chars)."),
    visibility: str | None = typer.Option(
        None,
        "--visibility", "-v",
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
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Update visibility, routing vars, and/or list price on a live service.

    All updates are sent in a single PATCH request.
    """
    has_routing = bool(set_routing_var or remove_routing_var or load_routing_vars)
    has_price = bool(set_price or remove_price_field)

    if not has_routing and not has_price and not visibility:
        console.print(
            "[yellow]Nothing to do:[/yellow] provide --visibility,"
            " --set-routing-var, --remove-routing-var, --load-routing-vars,"
            " --set-price, or --remove-price-field"
        )
        raise typer.Exit(code=0)

    # Build unified update body
    update_body: dict[str, Any] = {}

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
