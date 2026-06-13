"""``client.templates`` — the platform service-template catalog (read-only).

Wraps the seller-tagged ``/v1/seller/templates`` listing operations: ``list``
and ``get`` expose the active platform templates and their parameter schemas so
you can discover what you can instantiate. Creating a service from a template
lives on :class:`unitysvc_sellers.instances.Instances` (``client.instances``),
which posts to ``/v1/seller/instances``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient


class Templates:
    """Read-only manager for the platform service-template catalog."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list(
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
            op.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                service_type=service_type if service_type is not None else UNSET,
            )
        )

    def get(self, template_id: str | UUID) -> Any:
        """Fetch one template's metadata + parameter schema."""
        from ._generated.api.seller_templates import (
            seller_templates_get_seller_template as op,
        )

        return unwrap(op.sync_detailed(str(template_id), client=self._client))
