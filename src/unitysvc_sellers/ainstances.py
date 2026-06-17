"""``async_client.instances`` — async template instances.

Async mirror of :mod:`unitysvc_sellers.instances`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient


class AsyncInstances:
    """Async manager for the seller's template instances (create + manage)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def create(
        self,
        template_id: str | UUID,
        *,
        parameters: dict[str, Any] | None = None,
        name: str | None = None,
        auto_submit: bool = False,
    ) -> Any:
        """Create a service from ``template_id`` + ``parameters``.

        Renders the template into a **draft** service (the default, matching the
        backend's ``auto_submit=false``). Pass ``auto_submit=True`` to also submit
        that draft for review in the same call. Returns a record with
        ``instance_id`` and the ingest ``task_id``.
        """
        from ._generated.api.seller_instances import (
            seller_instances_create_instance as op,
        )
        from ._generated.models.template_instance_create import TemplateInstanceCreate
        from ._generated.models.template_instance_create_parameters import (
            TemplateInstanceCreateParameters,
        )
        from ._generated.types import UNSET

        body = TemplateInstanceCreate(
            template_id=UUID(str(template_id)),
            name=name if name is not None else UNSET,
            parameters=TemplateInstanceCreateParameters.from_dict(parameters or {}),
            auto_submit=auto_submit,
        )
        return unwrap(await op.asyncio_detailed(client=self._client, body=body))

    async def list(self, *, skip: int = 0, limit: int = 100) -> Any:
        """List my template instances (with derived service status)."""
        from ._generated.api.seller_instances import (
            seller_instances_list_instances as op,
        )

        return unwrap(
            await op.asyncio_detailed(client=self._client, skip=skip, limit=limit)
        )

    async def get(self, instance_id: str | UUID) -> Any:
        """Fetch one instance: parameters, template metadata, linked service."""
        from ._generated.api.seller_instances import (
            seller_instances_get_instance as op,
        )

        return unwrap(
            await op.asyncio_detailed(str(instance_id), client=self._client)
        )

    async def delete(self, instance_id: str | UUID) -> Any:
        """Delete an instance record (the linked service is not unpublished)."""
        from ._generated.api.seller_instances import (
            seller_instances_delete_instance as op,
        )

        return unwrap(
            await op.asyncio_detailed(str(instance_id), client=self._client)
        )
