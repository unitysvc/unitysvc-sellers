"""``async_client.templates`` — async platform service templates.

Async mirror of :mod:`unitysvc_sellers.templates`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient


class AsyncTemplates:
    """Async manager for platform service templates (read + instantiate)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        service_type: Any | None = None,
    ) -> Any:
        """List the active templates this seller can instantiate."""
        from ._generated.api.seller_templates import (
            seller_templates_list_seller_templates as op,
        )
        from ._generated.types import UNSET

        return unwrap(
            await op.asyncio_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                service_type=service_type if service_type is not None else UNSET,
            )
        )

    async def get(self, template_id: str | UUID) -> Any:
        """Fetch one template's metadata + parameter schema."""
        from ._generated.api.seller_templates import (
            seller_templates_get_seller_template as op,
        )

        return unwrap(await op.asyncio_detailed(str(template_id), client=self._client))

    async def instantiate(
        self,
        template_id: str | UUID,
        *,
        parameters: dict[str, Any] | None = None,
        name: str | None = None,
    ) -> Any:
        """Create a service from ``template_id`` + ``parameters`` in one call."""
        from ._generated.api.seller_forms import seller_forms_instantiate_form as op
        from ._generated.models.parameters import Parameters
        from ._generated.models.service_form_create import ServiceFormCreate
        from ._generated.types import UNSET

        body = ServiceFormCreate(
            template_id=UUID(str(template_id)),
            name=name if name is not None else UNSET,
            parameters=Parameters.from_dict(parameters or {}),
        )
        return unwrap(await op.asyncio_detailed(client=self._client, body=body))
