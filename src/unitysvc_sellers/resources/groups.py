"""``client.groups`` — service group management.

Wraps the seller-tagged ``/v1/seller/service-groups/*`` operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from .._http import unwrap

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient
    from .._generated.models.service_group_create import ServiceGroupCreate
    from .._generated.models.service_group_public import ServiceGroupPublic
    from .._generated.models.service_group_status_enum import ServiceGroupStatusEnum
    from .._generated.models.service_group_update import ServiceGroupUpdate
    from .._generated.models.service_groups_public import ServiceGroupsPublic


class GroupsResource:
    """Operations on the seller's service groups (``/v1/seller/service-groups``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        status: ServiceGroupStatusEnum | str | None = None,
    ) -> ServiceGroupsPublic:
        """List the seller's service groups."""
        from .._generated.api.seller import groups_list
        from .._generated.types import UNSET

        return unwrap(
            groups_list.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                status=status if status is not None else UNSET,  # type: ignore[arg-type]
            )
        )

    def get(self, group_id: str | UUID) -> ServiceGroupPublic:
        """Get a single service group by id."""
        from .._generated.api.seller import groups_get

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
        from .._generated.api.seller import groups_upsert
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
        from .._generated.api.seller import groups_update
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
        from .._generated.api.seller import groups_delete

        unwrap(
            groups_delete.sync_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
            )
        )

    def refresh(self, group_id: str | UUID) -> ServiceGroupPublic:
        """Re-evaluate dynamic membership for a service group."""
        from .._generated.api.seller import groups_refresh

        return unwrap(
            groups_refresh.sync_detailed(
                group_id=UUID(str(group_id)),
                client=self._client,
            )
        )
