"""Async mirror of :mod:`groups`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.cursor_page_service_group_public import (
        CursorPageServiceGroupPublic,
    )
    from ._generated.models.service_group_create import ServiceGroupCreate
    from ._generated.models.service_group_public import ServiceGroupPublic
    from ._generated.models.service_group_status_enum import ServiceGroupStatusEnum
    from ._generated.models.service_group_update import ServiceGroupUpdate


class AsyncGroups:
    """Async operations on the seller's service groups."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: ServiceGroupStatusEnum | str | None = None,
    ) -> CursorPageServiceGroupPublic:
        from ._generated.api.seller_service_groups import groups_list
        from ._generated.types import UNSET

        return unwrap(
            await groups_list.asyncio_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,  # type: ignore[arg-type]
            )
        )

    async def get(self, group_id: str | UUID) -> ServiceGroupPublic:
        from ._generated.api.seller_service_groups import groups_get

        return unwrap(
            await groups_get.asyncio_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
            )
        )

    async def upsert(
        self,
        body: ServiceGroupCreate | dict[str, Any],
    ) -> ServiceGroupPublic:
        from ._generated.api.seller_service_groups import groups_upsert
        from ._generated.models.service_group_create import ServiceGroupCreate

        if isinstance(body, dict):
            body = ServiceGroupCreate.from_dict(body)

        return unwrap(
            await groups_upsert.asyncio_detailed(
                client=self._client,
                body=body,
            )
        )

    async def update(
        self,
        group_id: str | UUID,
        body: ServiceGroupUpdate | dict[str, Any],
    ) -> ServiceGroupPublic:
        from ._generated.api.seller_service_groups import groups_update
        from ._generated.models.service_group_update import ServiceGroupUpdate

        if isinstance(body, dict):
            body = ServiceGroupUpdate.from_dict(body)

        return unwrap(
            await groups_update.asyncio_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
                body=body,
            )
        )

    async def delete(self, group_id: str | UUID) -> None:
        from ._generated.api.seller_service_groups import groups_delete

        unwrap(
            await groups_delete.asyncio_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
            )
        )

    # NOTE: ``refresh()`` was removed. The backend no longer exposes
    # ``POST /v1/seller/service-groups/{id}/refresh`` — dynamic
    # membership refresh is now handled automatically by a background
    # worker. Mutating a group via ``upsert`` / ``update`` already
    # triggers it.
