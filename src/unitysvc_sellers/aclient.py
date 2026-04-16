"""Asynchronous seller SDK client.

Mirror of :class:`unitysvc_sellers.Client` that uses the generated
``asyncio_detailed`` entry points instead of ``sync_detailed``. Every
resource method on :class:`AsyncClient` is an ``async def`` returning
the same typed model the sync version returns.

Example::

    import asyncio
    from unitysvc_sellers import AsyncClient

    async def main():
        async with AsyncClient(api_key="svcpass_...") as client:
            services = await client.services.list()
            for s in services.data:
                print(s.name)

    asyncio.run(main())

The underlying low-level client is shared between sync and async — the
same :class:`unitysvc_sellers._generated.client.AuthenticatedClient`
exposes both ``get_httpx_client`` and ``get_async_httpx_client``. So an
:class:`AsyncClient` can be used in either an asyncio context manager
or with manual ``aclose()``.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import httpx

from ._generated.client import AuthenticatedClient as _LowLevelClient
from .client import DEFAULT_SELLER_API_URL, ENV_SELLER_API_KEY, ENV_SELLER_API_URL

if TYPE_CHECKING:
    from .adocuments import AsyncDocuments
    from .agroups import AsyncGroups
    from .apromotions import AsyncPromotions
    from .asecrets import AsyncSecrets
    from .aservices import AsyncServices
    from .atasks import AsyncTasks


class AsyncClient:
    """Asynchronous seller SDK client.

    Args:
        api_key: A seller API key (``svcpass_...``). Encodes the seller
            context, so no separate ``seller_id`` is required.
        base_url: Override the default base URL. If not provided, falls
            back to ``UNITYSVC_SELLER_API_URL``, then to
            :data:`unitysvc_sellers.DEFAULT_SELLER_API_URL`.
        timeout: Per-request timeout in seconds. Default 30s.
        verify_ssl: Whether to verify TLS certificates. Default ``True``.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float | httpx.Timeout | None = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        resolved_base_url = base_url or os.environ.get(ENV_SELLER_API_URL) or DEFAULT_SELLER_API_URL

        if isinstance(timeout, (int, float)):
            timeout_obj = httpx.Timeout(float(timeout))
        else:
            timeout_obj = timeout  # type: ignore[assignment]

        self._client = _LowLevelClient(
            base_url=resolved_base_url,
            token=api_key,
            timeout=timeout_obj,
            verify_ssl=verify_ssl,
            raise_on_unexpected_status=False,
        )
        self._api_key = api_key
        self._base_url = resolved_base_url

        self._services: AsyncServices | None = None
        self._promotions: AsyncPromotions | None = None
        self._groups: AsyncGroups | None = None
        self._documents: AsyncDocuments | None = None
        self._tasks: AsyncTasks | None = None
        self._secrets: AsyncSecrets | None = None

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_env(cls, **kwargs: object) -> AsyncClient:
        """Construct an :class:`AsyncClient` from environment variables."""
        api_key = os.environ.get(ENV_SELLER_API_KEY)
        if not api_key:
            raise RuntimeError(
                f"Environment variable {ENV_SELLER_API_KEY} is not set. "
                f"Set it to a seller API key (svcpass_...) or pass api_key= explicitly."
            )
        return cls(api_key=api_key, **kwargs)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Resource namespaces (lazy)
    # ------------------------------------------------------------------
    @property
    def services(self) -> AsyncServices:
        if self._services is None:
            from .aservices import AsyncServices

            self._services = AsyncServices(self._client)
        return self._services

    @property
    def promotions(self) -> AsyncPromotions:
        if self._promotions is None:
            from .apromotions import AsyncPromotions

            self._promotions = AsyncPromotions(self._client)
        return self._promotions

    @property
    def groups(self) -> AsyncGroups:
        if self._groups is None:
            from .agroups import AsyncGroups

            self._groups = AsyncGroups(self._client)
        return self._groups

    @property
    def documents(self) -> AsyncDocuments:
        if self._documents is None:
            from .adocuments import AsyncDocuments

            self._documents = AsyncDocuments(self._client)
        return self._documents

    @property
    def tasks(self) -> AsyncTasks:
        if self._tasks is None:
            from .atasks import AsyncTasks

            self._tasks = AsyncTasks(self._client)
        return self._tasks

    @property
    def secrets(self) -> AsyncSecrets:
        if self._secrets is None:
            from .asecrets import AsyncSecrets

            self._secrets = AsyncSecrets(self._client)
        return self._secrets

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def aclose(self) -> None:
        """Close the underlying async httpx client."""
        try:
            await self._client.get_async_httpx_client().aclose()
        except Exception:
            pass

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()
