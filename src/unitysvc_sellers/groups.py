"""``client.groups`` — service group management.

Wraps the seller-tagged ``/v1/seller/service-groups/*`` operations from
the generated low-level client. ``client.groups.get(...)`` returns a
:class:`Group` active-record wrapper whose methods (``refresh``,
``update``, ``delete``) navigate without re-passing the group id;
``client.groups.list(...)`` returns a :class:`GroupList` that's iterable
directly so ``for grp in groups`` works alongside ``groups.next_cursor``
/ ``groups.has_more`` for pagination.

Field access on a :class:`Group` is forwarded to the underlying
generated record (:class:`ServiceGroupPublic`), so ``grp.id``,
``grp.name``, ``grp.display_name``, ``grp.status`` etc. all work
transparently.

The same operations remain available on the manager directly
(``client.groups.update(group_id, ...)``); :class:`Group` is just sugar
that pre-binds the id.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.service_group_create import ServiceGroupCreate
    from ._generated.models.service_group_public import ServiceGroupPublic
    from ._generated.models.service_group_status_enum import ServiceGroupStatusEnum
    from ._generated.models.service_group_update import ServiceGroupUpdate
    from .client import Client


class Group:
    """Active-record wrapper around a seller service group.

    Forwards field access (``grp.id``, ``grp.name``,
    ``grp.display_name``, ``grp.status``, …) to the underlying
    generated :class:`ServiceGroupPublic` record via ``__getattr__``.
    Adds methods that delegate to the parent :class:`Client`:

    - :meth:`refresh` — re-fetch the group via ``groups_get``.
    - :meth:`update` — patch fields. Same body shape as
      :meth:`Groups.update`.
    - :meth:`delete` — remove the group.

    Returned by :meth:`Groups.get`, :meth:`Groups.upsert`,
    :meth:`Groups.update`, and as items inside :class:`GroupList`
    from :meth:`Groups.list`.
    """

    __slots__ = ("_raw", "_parent")

    def __init__(self, raw: ServiceGroupPublic, parent: Client) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        name = getattr(raw, "name", None)
        status = getattr(raw, "status", None)
        return f"<Group id={raw.id!r} name={name!r} status={status!r}>"

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def refresh(self) -> Group:
        """Re-fetch the group via ``groups_get``.

        Returns a new :class:`Group` wrapping the fresh record.
        """
        return self._parent.groups.get(self._raw.id)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def update(self, body: ServiceGroupUpdate | dict[str, Any]) -> Group:
        """Patch fields. See :meth:`Groups.update` for the body shape."""
        return self._parent.groups.update(self._raw.id, body)

    def delete(self) -> None:
        """Delete the group. See :meth:`Groups.delete`."""
        self._parent.groups.delete(self._raw.id)


class GroupList:
    """Cursor-paginated wrapper around a service-group list response.

    Iterable directly, so callers can write::

        groups = client.groups.list(limit=50)
        for grp in groups:
            print(grp.name, grp.display_name)

    Pagination metadata is still on the object — ``groups.data``,
    ``groups.next_cursor``, ``groups.has_more`` — for callers that
    need to advance manually. :meth:`next_page` returns the next page
    (or ``None`` if there are no more); for the common
    "iterate everything" case use :meth:`Groups.iter_all`.
    """

    __slots__ = ("data", "next_cursor", "has_more", "_parent", "_list_kwargs")

    def __init__(
        self,
        data: list[Group],
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

    def __iter__(self) -> Iterator[Group]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Group:
        return self.data[idx]

    def __bool__(self) -> bool:
        return bool(self.data)

    def __repr__(self) -> str:
        return f"<GroupList n={len(self.data)} has_more={self.has_more}>"

    def next_page(self) -> GroupList | None:
        """Fetch the next page using ``next_cursor``, or ``None`` if exhausted."""
        if not self.has_more or self.next_cursor is None or self._parent is None:
            return None
        kwargs = dict(self._list_kwargs)
        kwargs["cursor"] = self.next_cursor
        return self._parent.groups.list(**kwargs)


class Groups:
    """Operations on the seller's service groups (``/v1/seller/service-groups``).

    Example::

        # Active-record style — preferred for chained calls
        for grp in client.groups.list():
            print(grp.name, grp.display_name)
            if grp.status == "draft":
                grp.update({"status": "active"})

        # Or the equivalent manager-style — by id
        client.groups.update(group_id, {"status": "active"})
        client.groups.delete(group_id)
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
        status: ServiceGroupStatusEnum | str | None = None,
    ) -> GroupList:
        """List the seller's service groups.

        Cursor-paginated. Returns a :class:`GroupList` that's iterable
        over :class:`Group` items and exposes ``next_cursor`` /
        ``has_more`` for manual pagination. For "iterate all pages"
        use :meth:`iter_all`.
        """
        from ._generated.api.seller_service_groups import groups_list
        from ._generated.types import UNSET

        raw = unwrap(
            groups_list.sync_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,  # type: ignore[arg-type]
            )
        )
        return GroupList(
            data=[Group(item, parent=self._parent) for item in raw.data],
            next_cursor=raw.next_cursor if isinstance(raw.next_cursor, str) else None,
            has_more=bool(raw.has_more),
            parent=self._parent,
            list_kwargs={"limit": limit, "status": status},
        )

    def iter_all(
        self,
        *,
        limit: int = 50,
        status: ServiceGroupStatusEnum | str | None = None,
    ) -> Iterable[Group]:
        """Iterate over all groups across pages, auto-advancing the cursor."""
        kwargs: dict[str, Any] = {"limit": limit, "status": status}
        page: GroupList | None = self.list(**kwargs)
        while page is not None:
            yield from page
            page = page.next_page()

    def get(self, group_id: str | UUID) -> Group:
        """Get a single service group by id."""
        from ._generated.api.seller_service_groups import groups_get

        raw = unwrap(
            groups_get.sync_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
            )
        )
        return Group(raw, parent=self._parent)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def upsert(
        self,
        body: ServiceGroupCreate | dict[str, Any],
    ) -> Group:
        """Create or update a service group by name (idempotent)."""
        from ._generated.api.seller_service_groups import groups_upsert
        from ._generated.models.service_group_create import ServiceGroupCreate

        if isinstance(body, dict):
            body = ServiceGroupCreate.from_dict(body)

        raw = unwrap(
            groups_upsert.sync_detailed(
                client=self._client,
                body=body,
            )
        )
        return Group(raw, parent=self._parent)

    def update(
        self,
        group_id: str | UUID,
        body: ServiceGroupUpdate | dict[str, Any],
    ) -> Group:
        """Patch a single service group by id."""
        from ._generated.api.seller_service_groups import groups_update
        from ._generated.models.service_group_update import ServiceGroupUpdate

        if isinstance(body, dict):
            body = ServiceGroupUpdate.from_dict(body)

        raw = unwrap(
            groups_update.sync_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
                body=body,
            )
        )
        return Group(raw, parent=self._parent)

    def delete(self, group_id: str | UUID) -> None:
        """Delete a service group."""
        from ._generated.api.seller_service_groups import groups_delete

        unwrap(
            groups_delete.sync_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
            )
        )

    # NOTE: ``refresh()`` was removed. The backend no longer exposes
    # ``POST /v1/seller/service-groups/{id}/refresh`` — dynamic
    # membership refresh is now handled automatically by a background
    # worker (``schedule_group_membership_refresh``). Mutating a group
    # via ``upsert`` / ``update`` already triggers it.
