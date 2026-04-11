"""Async mirror of :mod:`unitysvc_sellers.resources.promotions`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from .._http import unwrap

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient
    from .._generated.models.cursor_page_price_rule_public import (
        CursorPagePriceRulePublic,
    )
    from .._generated.models.price_rule_public import PriceRulePublic
    from .._generated.models.price_rule_status_enum import PriceRuleStatusEnum
    from .._generated.models.seller_promotion_create import SellerPromotionCreate
    from .._generated.models.seller_promotion_update import SellerPromotionUpdate


class AsyncPromotionsResource:
    """Async operations on the seller's promotions."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: PriceRuleStatusEnum | str | None = None,
    ) -> CursorPagePriceRulePublic:
        from .._generated.api.seller_promotions import promotions_list
        from .._generated.types import UNSET

        return unwrap(
            await promotions_list.asyncio_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,  # type: ignore[arg-type]
            )
        )

    async def get(self, promotion_id: str | UUID) -> PriceRulePublic:
        from .._generated.api.seller_promotions import promotions_get

        return unwrap(
            await promotions_get.asyncio_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
            )
        )

    async def upsert(
        self,
        body: SellerPromotionCreate | dict[str, Any],
    ) -> PriceRulePublic:
        from .._generated.api.seller_promotions import promotions_upsert
        from .._generated.models.seller_promotion_create import SellerPromotionCreate

        if isinstance(body, dict):
            body = SellerPromotionCreate.from_dict(body)

        return unwrap(
            await promotions_upsert.asyncio_detailed(
                client=self._client,
                body=body,
            )
        )

    async def update(
        self,
        promotion_id: str | UUID,
        body: SellerPromotionUpdate | dict[str, Any],
    ) -> PriceRulePublic:
        from .._generated.api.seller_promotions import promotions_update
        from .._generated.models.seller_promotion_update import SellerPromotionUpdate

        if isinstance(body, dict):
            body = SellerPromotionUpdate.from_dict(body)

        return unwrap(
            await promotions_update.asyncio_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
                body=body,
            )
        )

    async def delete(self, promotion_id: str | UUID) -> None:
        from .._generated.api.seller_promotions import promotions_delete

        unwrap(
            await promotions_delete.asyncio_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
            )
        )
