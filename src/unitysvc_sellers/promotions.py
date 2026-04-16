"""``client.promotions`` — seller-funded promotion management.

Wraps the seller-tagged ``/v1/seller/promotions/*`` operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.cursor_page_price_rule_public import (
        CursorPagePriceRulePublic,
    )
    from ._generated.models.price_rule_public import PriceRulePublic
    from ._generated.models.price_rule_status_enum import PriceRuleStatusEnum
    from ._generated.models.seller_promotion_create import SellerPromotionCreate
    from ._generated.models.seller_promotion_update import SellerPromotionUpdate


class Promotions:
    """Operations on the seller's promotions (``/v1/seller/promotions``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: PriceRuleStatusEnum | str | None = None,
    ) -> CursorPagePriceRulePublic:
        """List the seller's promotions with cursor-based pagination.

        Pass ``cursor=response.next_cursor`` on subsequent calls until
        ``response.has_more`` is ``False``.
        """
        from ._generated.api.seller_promotions import promotions_list
        from ._generated.types import UNSET

        return unwrap(
            promotions_list.sync_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,  # type: ignore[arg-type]
            )
        )

    def get(self, promotion_id: str | UUID) -> PriceRulePublic:
        """Get a single promotion by id."""
        from ._generated.api.seller_promotions import promotions_get

        return unwrap(
            promotions_get.sync_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
            )
        )

    def upsert(
        self,
        body: SellerPromotionCreate | dict[str, Any],
    ) -> PriceRulePublic:
        """Create or update a promotion by name (idempotent).

        If a promotion with the same ``name`` already exists for this
        seller it is updated in place; otherwise a new one is created.
        Use this for CLI-driven workflows where promotions are managed
        as files identified by name.
        """
        from ._generated.api.seller_promotions import promotions_upsert
        from ._generated.models.seller_promotion_create import SellerPromotionCreate

        if isinstance(body, dict):
            body = SellerPromotionCreate.from_dict(body)

        return unwrap(
            promotions_upsert.sync_detailed(
                client=self._client,
                body=body,
            )
        )

    def update(
        self,
        promotion_id: str | UUID,
        body: SellerPromotionUpdate | dict[str, Any],
    ) -> PriceRulePublic:
        """Patch a single promotion by id (partial update)."""
        from ._generated.api.seller_promotions import promotions_update
        from ._generated.models.seller_promotion_update import SellerPromotionUpdate

        if isinstance(body, dict):
            body = SellerPromotionUpdate.from_dict(body)

        return unwrap(
            promotions_update.sync_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
                body=body,
            )
        )

    def delete(self, promotion_id: str | UUID) -> None:
        """Delete a promotion. Returns nothing on success."""
        from ._generated.api.seller_promotions import promotions_delete

        unwrap(
            promotions_delete.sync_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
            )
        )
