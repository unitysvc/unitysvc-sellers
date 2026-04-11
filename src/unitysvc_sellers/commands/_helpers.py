"""Internal helpers shared by the ``usvc_seller`` async command groups.

These wrap common patterns:

- ``run_async`` — invoke a coroutine from a Typer command, mapping
  :class:`unitysvc_sellers.SellerSDKError` to a clean ``typer.Exit(1)``
  with a Rich-formatted error.
- ``async_client_from_env`` — read credentials from the environment
  (or explicit args) and yield an :class:`AsyncClient` inside an
  ``async with``.
- ``model_to_dict`` — coerce an attrs-generated model into a plain
  ``dict`` so the existing Rich tables / JSON formatters keep working.
- ``resolve_promotion`` — exact-name match then partial-id match across
  the seller's promotions, mirroring the legacy
  ``_find_promotion_by_name`` semantics.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable
from contextlib import asynccontextmanager
from typing import Any, TypeVar

import typer
from rich.console import Console

from ..aclient import AsyncClient
from ..client import DEFAULT_SELLER_API_URL, ENV_SELLER_API_KEY, ENV_SELLER_API_URL
from ..exceptions import SellerSDKError

T = TypeVar("T")

console = Console()


def run_async(coro: Awaitable[T], *, error_prefix: str = "Failed") -> T:
    """Run a coroutine and translate SDK errors into ``typer.Exit(1)``.

    Use this from inside Typer command handlers::

        async def _impl():
            async with async_client(api_key, base_url) as client:
                return await client.services.list()

        services = run_async(_impl(), error_prefix="Failed to list services")
    """
    try:
        return asyncio.run(coro)
    except SellerSDKError as exc:
        console.print(f"[red]✗[/red] {error_prefix}: {exc}", style="bold red")
        raise typer.Exit(code=1) from exc
    except typer.Exit:
        raise
    except Exception as exc:  # noqa: BLE001 — surface to user, not crash
        console.print(f"[red]✗[/red] {error_prefix}: {exc}", style="bold red")
        raise typer.Exit(code=1) from exc


@asynccontextmanager
async def async_client(
    api_key: str | None = None,
    base_url: str | None = None,
):
    """Yield an :class:`AsyncClient` configured from args or environment.

    Args:
        api_key: Override the seller API key. Defaults to ``$UNITYSVC_SELLER_API_KEY``.
        base_url: Override the backend URL. Defaults to ``$UNITYSVC_SELLER_API_URL``
            then to :data:`unitysvc_sellers.DEFAULT_SELLER_API_URL`.

    Raises:
        typer.Exit: If no API key is available.
    """
    resolved_key = api_key or os.environ.get(ENV_SELLER_API_KEY)
    if not resolved_key:
        console.print(
            f"[red]✗[/red] Missing seller API key. Set ${ENV_SELLER_API_KEY} or pass --api-key.",
            style="bold red",
        )
        raise typer.Exit(code=1)

    resolved_url = base_url or os.environ.get(ENV_SELLER_API_URL) or DEFAULT_SELLER_API_URL
    async with AsyncClient(api_key=resolved_key, base_url=resolved_url) as client:
        yield client


def model_to_dict(obj: Any) -> dict[str, Any]:
    """Coerce a generated attrs model (or anything dict-like) into a dict.

    The generated low-level models all expose ``to_dict``. We use that
    so the legacy CLI's table-rendering code can keep operating on plain
    dicts without having to know about every typed model in
    ``unitysvc_sellers._generated.models``.
    """
    if isinstance(obj, dict):
        return dict(obj)
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    raise TypeError(f"Cannot coerce {type(obj).__name__} to dict")


def model_list(obj: Any) -> list[dict[str, Any]]:
    """Coerce a list-shaped response (``{data: [...], count: N}``) into ``list[dict]``."""
    if isinstance(obj, list):
        return [model_to_dict(item) for item in obj]
    if hasattr(obj, "data"):
        data = obj.data
        return [model_to_dict(item) for item in data]
    if isinstance(obj, dict) and "data" in obj:
        return [model_to_dict(item) for item in obj["data"]]
    return [model_to_dict(obj)]


# ---------------------------------------------------------------------------
# Promotion name / partial-id resolution
# ---------------------------------------------------------------------------
async def resolve_promotion(client: AsyncClient, name_or_id: str) -> dict[str, Any]:
    """Find a promotion by exact name or partial id.

    Mirrors the legacy ``_find_promotion_by_name`` from
    ``unitysvc-services/promotions.py``: tries an exact name match
    first, then a UUID prefix match. Raises ``typer.Exit(1)`` on miss
    or ambiguous match.
    """
    rules = model_list(await client.promotions.list(limit=1000))

    # Exact name match wins.
    for rule in rules:
        if rule.get("name") == name_or_id:
            return rule

    # Then partial UUID prefix.
    matches = [r for r in rules if str(r.get("id", "")).startswith(name_or_id)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        console.print(
            f"[red]Error:[/red] Ambiguous promotion id prefix '{name_or_id}' matches {len(matches)} promotions"
        )
        raise typer.Exit(code=1)

    console.print(f"[red]Error:[/red] Promotion '{name_or_id}' not found")
    raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# Service id resolution
# ---------------------------------------------------------------------------
async def resolve_service_id(client: AsyncClient, partial_id: str) -> str:
    """Resolve a partial service id (≥8 chars) to a full UUID.

    The new ``services_get`` endpoint accepts the raw path segment and
    leaves resolution to the backend, but for bulk operations we still
    need a list-and-prefix-match step. Returns the full id as a string,
    or raises ``typer.Exit(1)`` on miss / ambiguous.
    """
    if len(partial_id) >= 8:
        # Try to fetch directly first — backend handles partial ids.
        try:
            detail = model_to_dict(await client.services.get(partial_id))
            sid = detail.get("service_id") or detail.get("id")
            if sid:
                return str(sid)
        except SellerSDKError:
            pass

    # Fall back to listing and prefix match.
    services = model_list(await client.services.list(limit=1000))
    matches = [s for s in services if str(s.get("id", "")).startswith(partial_id)]
    if len(matches) == 1:
        return str(matches[0]["id"])
    if len(matches) > 1:
        console.print(f"[red]Error:[/red] Ambiguous service id prefix '{partial_id}' matches {len(matches)} services")
        raise typer.Exit(code=1)
    console.print(f"[red]Error:[/red] Service '{partial_id}' not found")
    raise typer.Exit(code=1)


async def fetch_service_ids_by_status(
    client: AsyncClient,
    statuses: list[str],
    *,
    provider: str | None = None,
) -> list[str]:
    """List all service ids matching any of ``statuses``, optionally filtered by provider.

    Replacement for the legacy
    ``unitysvc_services.lifecycle.fetch_service_ids_by_status`` helper.
    """
    provider_lower = provider.lower() if provider else None
    all_ids: list[str] = []

    for status in statuses:
        try:
            services = model_list(await client.services.list(status=status, limit=1000))
        except SellerSDKError:
            continue

        for svc in services:
            if not svc.get("id"):
                continue
            if provider_lower:
                svc_provider = svc.get("provider_name", "") or ""
                if provider_lower not in svc_provider.lower():
                    continue
            all_ids.append(str(svc["id"]))

    return all_ids


# ---------------------------------------------------------------------------
# Common Typer option factories
# ---------------------------------------------------------------------------
def api_key_option():
    """Reusable ``--api-key`` option (env-fallback)."""
    return typer.Option(
        None,
        "--api-key",
        envvar=ENV_SELLER_API_KEY,
        help=f"Seller API key (svcpass_...). Defaults to ${ENV_SELLER_API_KEY}.",
        show_default=False,
    )


def base_url_option():
    """Reusable ``--base-url`` option (env-fallback)."""
    return typer.Option(
        DEFAULT_SELLER_API_URL,
        "--base-url",
        envvar=ENV_SELLER_API_URL,
        help="Backend base URL.",
    )
