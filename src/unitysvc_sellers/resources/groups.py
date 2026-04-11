"""``client.groups`` — service group management.

Wraps the seller-tagged ``/v1/seller/service-groups/*`` operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from .._http import unwrap

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient
    from .._generated.models.cursor_page_service_group_public import (
        CursorPageServiceGroupPublic,
    )
    from .._generated.models.service_group_create import ServiceGroupCreate
    from .._generated.models.service_group_public import ServiceGroupPublic
    from .._generated.models.service_group_status_enum import ServiceGroupStatusEnum
    from .._generated.models.service_group_update import ServiceGroupUpdate


class GroupsResource:
    """Operations on the seller's service groups (``/v1/seller/service-groups``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: ServiceGroupStatusEnum | str | None = None,
    ) -> CursorPageServiceGroupPublic:
        """List the seller's service groups with cursor-based pagination.

        Pass ``cursor=response.next_cursor`` on subsequent calls until
        ``response.has_more`` is ``False``.
        """
        from .._generated.api.seller_service_groups import groups_list
        from .._generated.types import UNSET

        return unwrap(
            groups_list.sync_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,  # type: ignore[arg-type]
            )
        )

    def get(self, group_id: str | UUID) -> ServiceGroupPublic:
        """Get a single service group by id."""
        from .._generated.api.seller_service_groups import groups_get

        return unwrap(
            groups_get.sync_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
            )
        )

    def upsert(
        self,
        body: ServiceGroupCreate | dict[str, Any],
    ) -> ServiceGroupPublic:
        """Create or update a service group by name (idempotent)."""
        from .._generated.api.seller_service_groups import groups_upsert
        from .._generated.models.service_group_create import ServiceGroupCreate

        if isinstance(body, dict):
            body = ServiceGroupCreate.from_dict(body)

        return unwrap(
            groups_upsert.sync_detailed(
                client=self._client,
                body=body,
            )
        )

    def update(
        self,
        group_id: str | UUID,
        body: ServiceGroupUpdate | dict[str, Any],
    ) -> ServiceGroupPublic:
        """Patch a single service group by id."""
        from .._generated.api.seller_service_groups import groups_update
        from .._generated.models.service_group_update import ServiceGroupUpdate

        if isinstance(body, dict):
            body = ServiceGroupUpdate.from_dict(body)

        return unwrap(
            groups_update.sync_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
                body=body,
            )
        )

    def delete(self, group_id: str | UUID) -> None:
        """Delete a service group."""
        from .._generated.api.seller_service_groups import groups_delete

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
