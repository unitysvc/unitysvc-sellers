"""Async mirror of :mod:`groups`.

Same active-record contract as the sync :class:`Group` /
:class:`GroupList`, with ``async def`` methods that delegate to the
parent :class:`AsyncClient`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.service_group_create import ServiceGroupCreate
    from ._generated.models.service_group_public import ServiceGroupPublic
    from ._generated.models.service_group_status_enum import ServiceGroupStatusEnum
    from ._generated.models.service_group_update import ServiceGroupUpdate
    from .aclient import AsyncClient


class AsyncGroup:
    """Async active-record wrapper. See :class:`unitysvc_sellers.groups.Group`."""

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: ServiceGroupPublic, parent: AsyncClient) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        name = getattr(raw, "name", None)
        status = getattr(raw, "status", None)
        return f"<AsyncGroup id={raw.id!r} name={name!r} status={status!r}>"

    async def refresh(self) -> AsyncGroup:
        return await self._parent.groups.get(self._raw.id)

    async def update(self, body: ServiceGroupUpdate | dict[str, Any]) -> AsyncGroup:
        return await self._parent.groups.update(self._raw.id, body)

    async def delete(self) -> None:
        await self._parent.groups.delete(self._raw.id)


class AsyncGroupList:
    """Async cursor-paginated wrapper.

    Iterable synchronously over the current page (``for grp in groups``)
    and asynchronously across all pages (``async for grp in
    groups.iter_all()``). For one-page-at-a-time callers,
    ``groups.next_cursor`` / ``groups.has_more`` / :meth:`next_page`
    are still available.
    """

    __slots__ = ("data", "next_cursor", "has_more", "_parent", "_list_kwargs")

    def __init__(
        self,
        data: list[AsyncGroup],
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

    def __iter__(self) -> Iterator[AsyncGroup]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> AsyncGroup:
        return self.data[idx]

    def __bool__(self) -> bool:
        return bool(self.data)

    def __repr__(self) -> str:
        return f"<AsyncGroupList n={len(self.data)} has_more={self.has_more}>"

    async def next_page(self) -> AsyncGroupList | None:
        if not self.has_more or self.next_cursor is None or self._parent is None:
            return None
        kwargs = dict(self._list_kwargs)
        kwargs["cursor"] = self.next_cursor
        return await self._parent.groups.list(**kwargs)


class AsyncGroups:
    """Async operations on the seller's service groups."""

    def __init__(self, client: AuthenticatedClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: ServiceGroupStatusEnum | str | None = None,
    ) -> AsyncGroupList:
        from ._generated.api.seller_service_groups import groups_list
        from ._generated.types import UNSET

        raw = unwrap(
            await groups_list.asyncio_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,  # type: ignore[arg-type]
            )
        )
        return AsyncGroupList(
            data=[AsyncGroup(item, parent=self._parent) for item in raw.data],
            next_cursor=raw.next_cursor if isinstance(raw.next_cursor, str) else None,
            has_more=bool(raw.has_more),
            parent=self._parent,
            list_kwargs={"limit": limit, "status": status},
        )

    async def iter_all(
        self,
        *,
        limit: int = 50,
        status: ServiceGroupStatusEnum | str | None = None,
    ) -> AsyncIterator[AsyncGroup]:
        """Async-iterate over all groups across pages."""
        kwargs: dict[str, Any] = {"limit": limit, "status": status}
        page: AsyncGroupList | None = await self.list(**kwargs)
        while page is not None:
            for item in page:
                yield item
            page = await page.next_page()

    async def get(self, group_id: str | UUID) -> AsyncGroup:
        from ._generated.api.seller_service_groups import groups_get

        raw = unwrap(
            await groups_get.asyncio_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
            )
        )
        return AsyncGroup(raw, parent=self._parent)

    async def upsert(
        self,
        body: ServiceGroupCreate | dict[str, Any],
    ) -> AsyncGroup:
        from ._generated.api.seller_service_groups import groups_upsert
        from ._generated.models.service_group_create import ServiceGroupCreate

        if isinstance(body, dict):
            body = ServiceGroupCreate.from_dict(body)

        raw = unwrap(
            await groups_upsert.asyncio_detailed(
                client=self._client,
                body=body,
            )
        )
        return AsyncGroup(raw, parent=self._parent)

    async def update(
        self,
        group_id: str | UUID,
        body: ServiceGroupUpdate | dict[str, Any],
    ) -> AsyncGroup:
        from ._generated.api.seller_service_groups import groups_update
        from ._generated.models.service_group_update import ServiceGroupUpdate

        if isinstance(body, dict):
            body = ServiceGroupUpdate.from_dict(body)

        raw = unwrap(
            await groups_update.asyncio_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
                body=body,
            )
        )
        return AsyncGroup(raw, parent=self._parent)

    async def delete(self, group_id: str | UUID) -> None:
        from ._generated.api.seller_service_groups import groups_delete

        unwrap(
            await groups_delete.asyncio_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
            )
        )
