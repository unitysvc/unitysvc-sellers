"""Async mirror of :mod:`services`.

Same active-record contract as the sync :class:`Service` /
:class:`ServiceList`, with ``async def`` methods that delegate to
the parent :class:`AsyncClient`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.service_data_input import ServiceDataInput
    from ._generated.models.service_delete_response import ServiceDeleteResponse
    from ._generated.models.service_detail_response import ServiceDetailResponse
    from ._generated.models.service_public import ServicePublic
    from ._generated.models.service_update_response import ServiceUpdateResponse
    from ._generated.models.task_queued_response import TaskQueuedResponse
    from ._generated.models.test_env_response import TestEnvResponse
    from .aclient import AsyncClient


class AsyncService:
    """Async active-record wrapper. See :class:`unitysvc_sellers.services.Service`."""

    __slots__ = ("_raw", "_parent")

    def __init__(
        self,
        raw: ServicePublic | ServiceDetailResponse,
        parent: AsyncClient,
    ) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        name = getattr(raw, "name", None)
        status = getattr(raw, "status", None)
        return f"<AsyncService id={raw.id!r} name={name!r} status={status!r}>"

    async def refresh(self) -> AsyncService:
        return await self._parent.services.get(self._raw.id)

    async def test_env(self) -> TestEnvResponse:
        return await self._parent.services.get_test_env(self._raw.id)

    async def update(self, body: dict[str, Any]) -> ServiceUpdateResponse:
        return await self._parent.services.update(self._raw.id, body)

    async def delete(self, *, dryrun: bool = False) -> ServiceDeleteResponse:
        return await self._parent.services.delete(self._raw.id, dryrun=dryrun)

    async def submit(self) -> ServiceUpdateResponse:
        """Submit for review — shortcut for ``update({"status": "pending"})``."""
        return await self.update({"status": "pending"})


class AsyncServiceList:
    """Async cursor-paginated wrapper.

    Iterable both synchronously over the current page (``for svc in
    services``) and asynchronously across all pages
    (``async for svc in services.iter_all()``). For one-page-at-a-time
    callers, ``services.next_cursor`` / ``services.has_more`` /
    :meth:`next_page` are still available.
    """

    __slots__ = ("data", "next_cursor", "has_more", "_parent", "_list_kwargs")

    def __init__(
        self,
        data: list[AsyncService],
        next_cursor: str | None,
        has_more: bool,
        *,
        parent: AsyncClient | None = None,
        list_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.data = data
        self.next_cursor = next_cursor
        self.has_more = has_more
        self._parent = parent
        self._list_kwargs = list_kwargs or {}

    def __iter__(self) -> Iterator[AsyncService]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> AsyncService:
        return self.data[idx]

    def __bool__(self) -> bool:
        return bool(self.data)

    def __repr__(self) -> str:
        return f"<AsyncServiceList n={len(self.data)} has_more={self.has_more}>"

    async def next_page(self) -> AsyncServiceList | None:
        if not self.has_more or self.next_cursor is None or self._parent is None:
            return None
        kwargs = dict(self._list_kwargs)
        kwargs["cursor"] = self.next_cursor
        return await self._parent.services.list(**kwargs)


class AsyncServices:
    """Async operations on the seller's service catalog."""

    def __init__(self, client: AuthenticatedClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: str | None = None,
        visibility: str | None = None,
        service_type: str | None = None,
        listing_type: str | None = None,
        name: str | None = None,
        provider: str | None = None,
        ids: list[str] | None = None,
    ) -> AsyncServiceList:
        from ._generated.api.seller_services import services_list
        from ._generated.types import UNSET

        raw = unwrap(
            await services_list.asyncio_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,
                visibility=visibility if visibility is not None else UNSET,
                service_type=service_type if service_type is not None else UNSET,
                listing_type=listing_type if listing_type is not None else UNSET,
                name=name if name is not None else UNSET,
                provider=provider if provider is not None else UNSET,
                ids=ids if ids is not None else UNSET,
            )
        )
        return AsyncServiceList(
            data=[AsyncService(item, parent=self._parent) for item in raw.data],
            next_cursor=raw.next_cursor if isinstance(raw.next_cursor, str) else None,
            has_more=bool(raw.has_more),
            parent=self._parent,
            list_kwargs={
                "limit": limit,
                "status": status,
                "visibility": visibility,
                "service_type": service_type,
                "listing_type": listing_type,
                "name": name,
                "provider": provider,
                "ids": ids,
            },
        )

    async def iter_all(
        self,
        *,
        limit: int = 50,
        status: str | None = None,
        visibility: str | None = None,
        service_type: str | None = None,
        listing_type: str | None = None,
        name: str | None = None,
        provider: str | None = None,
        ids: list[str] | None = None,
    ) -> AsyncIterator[AsyncService]:
        """Async-iterate over all services across pages."""
        kwargs: dict[str, Any] = {
            "limit": limit,
            "status": status,
            "visibility": visibility,
            "service_type": service_type,
            "listing_type": listing_type,
            "name": name,
            "provider": provider,
            "ids": ids,
        }
        page: AsyncServiceList | None = await self.list(**kwargs)
        while page is not None:
            for item in page:
                yield item
            page = await page.next_page()

    async def get(self, service_id: str | UUID) -> AsyncService:
        from ._generated.api.seller_services import services_get

        raw = unwrap(
            await services_get.asyncio_detailed(
                service_id=str(service_id),
                client=self._client,
            )
        )
        return AsyncService(raw, parent=self._parent)

    async def get_test_env(self, service_id: str | UUID) -> TestEnvResponse:
        from ._generated.api.seller_services import services_get_test_env

        return unwrap(
            await services_get_test_env.asyncio_detailed(
                service_id=str(service_id),
                client=self._client,
            )
        )

    async def upload(
        self,
        body: ServiceDataInput | dict[str, Any],
    ) -> TaskQueuedResponse:
        from ._generated.api.seller_services import services_upload
        from ._generated.models.service_data_input import ServiceDataInput

        if isinstance(body, dict):
            body = ServiceDataInput.from_dict(body)

        return unwrap(
            await services_upload.asyncio_detailed(
                client=self._client,
                body=body,
            )
        )

    async def update(
        self,
        service_id: str | UUID,
        body: dict[str, Any],
    ) -> ServiceUpdateResponse:
        """Update a service — status, visibility, routing vars, and/or list price."""
        from ._generated.api.seller_services import services_update
        from ._generated.models.service_update import ServiceUpdate

        return unwrap(
            await services_update.asyncio_detailed(
                service_id=str(service_id),
                client=self._client,
                body=ServiceUpdate.from_dict(body),
            )
        )

    async def delete(
        self,
        service_id: str | UUID,
        *,
        dryrun: bool = False,
    ) -> ServiceDeleteResponse:
        from ._generated.api.seller_services import services_delete

        return unwrap(
            await services_delete.asyncio_detailed(
                service_id=str(service_id),
                client=self._client,
                dryrun=dryrun,
            )
        )
