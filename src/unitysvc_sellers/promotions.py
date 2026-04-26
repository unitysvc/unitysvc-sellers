"""``client.promotions`` — seller-funded promotion management.

Wraps the seller-tagged ``/v1/seller/promotions/*`` operations from the
generated low-level client. ``client.promotions.get(...)`` returns a
:class:`Promotion` active-record wrapper whose methods (``refresh``,
``update``, ``delete``) navigate without re-passing the promotion id;
``client.promotions.list(...)`` returns a :class:`PromotionList` that's
iterable directly so ``for promo in promotions`` works alongside
``promotions.next_cursor`` / ``promotions.has_more`` for pagination.

Field access on a :class:`Promotion` is forwarded to the underlying
generated record (:class:`PriceRulePublic`), so ``promo.id``,
``promo.code``, ``promo.status`` etc. all work transparently.

The same operations remain available on the manager directly
(``client.promotions.update(promotion_id, ...)``); :class:`Promotion`
is just sugar that pre-binds the id.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.price_rule_public import PriceRulePublic
    from ._generated.models.price_rule_status_enum import PriceRuleStatusEnum
    from ._generated.models.seller_promotion_create import SellerPromotionCreate
    from ._generated.models.seller_promotion_update import SellerPromotionUpdate
    from .client import Client


class Promotion:
    """Active-record wrapper around a seller promotion.

    Forwards field access (``promo.id``, ``promo.code``,
    ``promo.status``, …) to the underlying generated
    :class:`PriceRulePublic` record via ``__getattr__``. Adds methods
    that delegate to the parent :class:`Client`:

    - :meth:`refresh` — re-fetch the promotion via ``promotions_get``.
    - :meth:`update` — patch fields. Same body shape as
      :meth:`Promotions.update`.
    - :meth:`delete` — remove the promotion.

    Returned by :meth:`Promotions.get`, :meth:`Promotions.upsert`,
    :meth:`Promotions.update`, and as items inside
    :class:`PromotionList` from :meth:`Promotions.list`.
    """

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: PriceRulePublic, parent: Client) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        code = getattr(raw, "code", None)
        status = getattr(raw, "status", None)
        return f"<Promotion id={raw.id!r} code={code!r} status={status!r}>"

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def refresh(self) -> Promotion:
        """Re-fetch the promotion via ``promotions_get``."""
        return self._parent.promotions.get(self._raw.id)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def update(self, body: SellerPromotionUpdate | dict[str, Any]) -> Promotion:
        """Patch fields. See :meth:`Promotions.update` for the body shape."""
        return self._parent.promotions.update(self._raw.id, body)

    def delete(self) -> None:
        """Delete the promotion. See :meth:`Promotions.delete`."""
        self._parent.promotions.delete(self._raw.id)


class PromotionList:
    """Cursor-paginated wrapper around a promotion list response.

    Iterable directly, so callers can write::

        promos = client.promotions.list(limit=50)
        for promo in promos:
            print(promo.code, promo.status)

    Pagination metadata is still on the object — ``promos.data``,
    ``promos.next_cursor``, ``promos.has_more`` — for callers that
    need to advance manually. :meth:`next_page` returns the next page
    (or ``None`` if there are no more); for the common
    "iterate everything" case use :meth:`Promotions.iter_all`.
    """

    __slots__ = ("data", "next_cursor", "has_more", "_parent", "_list_kwargs")

    def __init__(
        self,
        data: list[Promotion],
        next_cursor: str | None,
        has_more: bool,
        *,
        parent: Client | None = None,
        list_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.data = data
        self.next_cursor = next_cursor
        self.has_more = has_more
        self._parent = parent
        self._list_kwargs = list_kwargs or {}

    def __iter__(self) -> Iterator[Promotion]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Promotion:
        return self.data[idx]

    def __bool__(self) -> bool:
        return bool(self.data)

    def __repr__(self) -> str:
        return f"<PromotionList n={len(self.data)} has_more={self.has_more}>"

    def next_page(self) -> PromotionList | None:
        """Fetch the next page using ``next_cursor``, or ``None`` if exhausted."""
        if not self.has_more or self.next_cursor is None or self._parent is None:
            return None
        kwargs = dict(self._list_kwargs)
        kwargs["cursor"] = self.next_cursor
        return self._parent.promotions.list(**kwargs)


class Promotions:
    """Operations on the seller's promotions (``/v1/seller/promotions``).

    Example::

        # Active-record style — preferred for chained calls
        for promo in client.promotions.list():
            print(promo.code, promo.status)
            if promo.status == "active":
                promo.update({"status": "paused"})

        # Or the equivalent manager-style — by id
        client.promotions.update(promotion_id, {"status": "paused"})
        client.promotions.delete(promotion_id)
    """

    def __init__(self, client: AuthenticatedClient, *, parent: Client) -> None:
        self._client = client
        self._parent = parent

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: PriceRuleStatusEnum | str | None = None,
    ) -> PromotionList:
        """List the seller's promotions.

        Cursor-paginated. Returns a :class:`PromotionList` that's
        iterable over :class:`Promotion` items and exposes
        ``next_cursor`` / ``has_more`` for manual pagination. For
        "iterate all pages" use :meth:`iter_all`.
        """
        from ._generated.api.seller_promotions import promotions_list
        from ._generated.types import UNSET

        raw = unwrap(
            promotions_list.sync_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,  # type: ignore[arg-type]
            )
        )
        return PromotionList(
            data=[Promotion(item, parent=self._parent) for item in raw.data],
            next_cursor=raw.next_cursor if isinstance(raw.next_cursor, str) else None,
            has_more=bool(raw.has_more),
            parent=self._parent,
            list_kwargs={"limit": limit, "status": status},
        )

    def iter_all(
        self,
        *,
        limit: int = 50,
        status: PriceRuleStatusEnum | str | None = None,
    ) -> Iterable[Promotion]:
        """Iterate over all promotions across pages, auto-advancing the cursor."""
        kwargs: dict[str, Any] = {"limit": limit, "status": status}
        page: PromotionList | None = self.list(**kwargs)
        while page is not None:
            yield from page
            page = page.next_page()

    def get(self, promotion_id: str | UUID) -> Promotion:
        """Get a single promotion by id."""
        from ._generated.api.seller_promotions import promotions_get

        raw = unwrap(
            promotions_get.sync_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
            )
        )
        return Promotion(raw, parent=self._parent)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def upsert(
        self,
        body: SellerPromotionCreate | dict[str, Any],
    ) -> Promotion:
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

        raw = unwrap(
            promotions_upsert.sync_detailed(
                client=self._client,
                body=body,
            )
        )
        return Promotion(raw, parent=self._parent)

    def update(
        self,
        promotion_id: str | UUID,
        body: SellerPromotionUpdate | dict[str, Any],
    ) -> Promotion:
        """Patch a single promotion by id (partial update)."""
        from ._generated.api.seller_promotions import promotions_update
        from ._generated.models.seller_promotion_update import SellerPromotionUpdate

        if isinstance(body, dict):
            body = SellerPromotionUpdate.from_dict(body)

        raw = unwrap(
            promotions_update.sync_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
                body=body,
            )
        )
        return Promotion(raw, parent=self._parent)

    def delete(self, promotion_id: str | UUID) -> None:
        """Delete a promotion. Returns nothing on success."""
        from ._generated.api.seller_promotions import promotions_delete

        unwrap(
            promotions_delete.sync_detailed(
                promotion_id=UUID(str(promotion_id)),
                client=self._client,
            )
        )
