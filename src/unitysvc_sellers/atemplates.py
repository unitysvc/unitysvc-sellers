"""``async_client.templates`` — async platform service-template catalog.

Async mirror of :mod:`unitysvc_sellers.templates` (read-only). Creating a
service from a template lives on ``async_client.instances`` (see
:mod:`unitysvc_sellers.ainstances`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient


class AsyncTemplates:
    """Async read-only manager for the platform service-template catalog."""

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
