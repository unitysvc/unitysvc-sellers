"""Async mirror of :mod:`promotions`.

Same active-record contract as the sync :class:`Promotion` /
:class:`PromotionList`, with ``async def`` methods that delegate to the
parent :class:`AsyncClient`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.price_rule_public import PriceRulePublic
    from ._generated.models.price_rule_status_enum import PriceRuleStatusEnum
    from ._generated.models.seller_promotion_create import SellerPromotionCreate
    from ._generated.models.seller_promotion_update import SellerPromotionUpdate
    from .aclient import AsyncClient


class AsyncPromotion:
    """Async active-record wrapper. See :class:`unitysvc_sellers.promotions.Promotion`."""

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: PriceRulePublic, parent: AsyncClient) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        code = getattr(raw, "code", None)
        status = getattr(raw, "status", None)
        return f"<AsyncPromotion id={raw.id!r} code={code!r} status={status!r}>"

    async def refresh(self) -> AsyncPromotion:
        return await self._parent.promotions.get(self._raw.id)

    async def update(self, body: SellerPromotionUpdate | dict[str, Any]) -> AsyncPromotion:
        return await self._parent.promotions.update(self._raw.id, body)

    async def delete(self) -> None:
        await self._parent.promotions.delete(self._raw.id)


class AsyncPromotionList:
    """Async cursor-paginated wrapper.

    Iterable synchronously over the current page (``for promo in
    promos``) and asynchronously across all pages (``async for promo
    in promos.iter_all()``). For one-page-at-a-time callers,
    ``promos.next_cursor`` / ``promos.has_more`` / :meth:`next_page`
    are still available.
    """

    __slots__ = ("data", "next_cursor", "has_more", "_parent", "_list_kwargs")

    def __init__(
        self,
        data: list[AsyncPromotion],
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

    def __iter__(self) -> Iterator[AsyncPromotion]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> AsyncPromotion:
        return self.data[idx]

    def __bool__(self) -> bool:
        return bool(self.data)

    def __repr__(self) -> str:
        return f"<AsyncPromotionList n={len(self.data)} has_more={self.has_more}>"

    async def next_page(self) -> AsyncPromotionList | None:
        if not self.has_more or self.next_cursor is None or self._parent is None:
            return None
        kwargs = dict(self._list_kwargs)
        kwargs["cursor"] = self.next_cursor
        return await self._parent.promotions.list(**kwargs)


class AsyncPromotions:
    """Async operations on the seller's promotions."""

    def __init__(self, client: AuthenticatedClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: PriceRuleStatusEnum | str | None = None,
    ) -> AsyncPromotionList:
        from ._generated.api.seller_promotions import promotions_list
        from ._generated.types import UNSET

        raw = unwrap(
            await promotions_list.asyncio_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,  # type: ignore[arg-type]
            )
        )
        return AsyncPromotionList(
            data=[AsyncPromotion(item, parent=self._parent) for item in raw.data],
            next_cursor=raw.next_cursor if isinstance(raw.next_cursor, str) else None,
            has_more=bool(raw.has_more),
            parent=self._parent,
            list_kwargs={"limit": limit, "status": status},
        )

    async def iter_all(
        self,
        *,
        limit: int = 50,
        status: PriceRuleStatusEnum | str | None = None,
    ) -> AsyncIterator[AsyncPromotion]:
        """Async-iterate over all promotions across pages."""
        kwargs: dict[str, Any] = {"limit": limit, "status": status}
        page: AsyncPromotionList | None = await self.list(**kwargs)
        while page is not None:
            for item in page:
                yield item
            page = await page.next_page()

    async def get(self, promotion_id: str | UUID) -> AsyncPromotion:
        from ._generated.api.seller_promotions import promotions_get

        raw = unwrap(
            await promotions_get.asyncio_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
            )
        )
        return AsyncPromotion(raw, parent=self._parent)

    async def upsert(
        self,
        body: SellerPromotionCreate | dict[str, Any],
    ) -> AsyncPromotion:
        from ._generated.api.seller_promotions import promotions_upsert
        from ._generated.models.seller_promotion_create import SellerPromotionCreate

        if isinstance(body, dict):
            body = SellerPromotionCreate.from_dict(body)

        raw = unwrap(
            await promotions_upsert.asyncio_detailed(
                client=self._client,
                body=body,
            )
        )
        return AsyncPromotion(raw, parent=self._parent)

    async def update(
        self,
        promotion_id: str | UUID,
        body: SellerPromotionUpdate | dict[str, Any],
    ) -> AsyncPromotion:
        from ._generated.api.seller_promotions import promotions_update
        from ._generated.models.seller_promotion_update import SellerPromotionUpdate

        if isinstance(body, dict):
            body = SellerPromotionUpdate.from_dict(body)

        raw = unwrap(
            await promotions_update.asyncio_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
                body=body,
            )
        )
        return AsyncPromotion(raw, parent=self._parent)

    async def delete(self, promotion_id: str | UUID) -> None:
        from ._generated.api.seller_promotions import promotions_delete

        unwrap(
            await promotions_delete.asyncio_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
            )
        )
