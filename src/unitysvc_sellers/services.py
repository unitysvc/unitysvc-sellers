"""``client.services`` — service catalog management.

Wraps the seller-tagged ``/v1/seller/services/*`` operations from the
generated low-level client. Each method calls ``sync_detailed`` and
passes the result through :func:`unitysvc_sellers._http.unwrap`, so
callers always get a populated typed model or a
:class:`~unitysvc_sellers.exceptions.SellerSDKError`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.cursor_page_service_public import CursorPageServicePublic
    from ._generated.models.service_data_input import ServiceDataInput
    from ._generated.models.service_delete_response import ServiceDeleteResponse
    from ._generated.models.service_detail_response import ServiceDetailResponse
    from ._generated.models.service_update_response import ServiceUpdateResponse
    from ._generated.models.task_queued_response import TaskQueuedResponse
    from ._generated.models.test_env_response import TestEnvResponse


class Services:
    """Operations on the seller's service catalog (``/v1/seller/services``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: str | None = None,
        service_type: str | None = None,
        listing_type: str | None = None,
        name: str | None = None,
    ) -> CursorPageServicePublic:
        """List services owned by the authenticated seller.

        Uses **cursor-based pagination**. The first call omits
        ``cursor``. Subsequent calls pass ``cursor=response.next_cursor``
        until ``response.has_more`` is ``False``.
        """
        from ._generated.api.seller_services import services_list
        from ._generated.types import UNSET

        return unwrap(
            services_list.sync_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,
                service_type=service_type if service_type is not None else UNSET,
                listing_type=listing_type if listing_type is not None else UNSET,
                name=name if name is not None else UNSET,
            )
        )

    def get(self, service_id: str | UUID) -> ServiceDetailResponse:
        """Get the full record for a single service, including documents and interfaces."""
        from ._generated.api.seller_services import services_get

        return unwrap(
            services_get.sync_detailed(
                service_id=str(service_id),
                client=self._client,
            )
        )

    def get_test_env(self, service_id: str | UUID) -> TestEnvResponse:
        """Return the rendered environment used to run code-example scripts for a service."""
        from ._generated.api.seller_services import services_get_test_env

        return unwrap(
            services_get_test_env.sync_detailed(
                service_id=str(service_id),
                client=self._client,
            )
        )

    # ------------------------------------------------------------------
    # Write — bulk upload
    # ------------------------------------------------------------------
    def upload(
        self,
        body: ServiceDataInput | dict[str, Any],
    ) -> TaskQueuedResponse:
        """Submit a provider/offering/listing bundle for ingestion."""
        from ._generated.api.seller_services import services_upload
        from ._generated.models.service_data_input import ServiceDataInput

        if isinstance(body, dict):
            body = ServiceDataInput.from_dict(body)

        return unwrap(
            services_upload.sync_detailed(
                client=self._client,
                body=body,
            )
        )

    # ------------------------------------------------------------------
    # Write — update
    # ------------------------------------------------------------------
    def update(
        self,
        service_id: str | UUID,
        body: dict[str, Any],
    ) -> ServiceUpdateResponse:
        """Update a service — status, visibility, routing vars, and/or list price.

        All fields are optional. Include only the fields you want to change.
        Multiple fields can be updated in a single request.

        Args:
            service_id: Service to update.
            body: Dict with any combination of::

                {"status": "pending"}
                {"visibility": "public"}
                {"routing_vars": {"region": "us-east"}}              # full replacement
                {"routing_vars": {"set": {"count": 1}}}              # partial update
                {"list_price": {"type": "constant", "price": "1"}}   # full replacement
                {"list_price": {"set": {"price": "2"}}}              # partial update

        Example::

            # Set visibility and update price in one call
            client.services.update(service_id, {
                "visibility": "public",
                "list_price": {"type": "constant", "price": "1.00"},
            })
        """
        from ._generated.api.seller_services import services_update
        from ._generated.models.service_update import ServiceUpdate

        return unwrap(
            services_update.sync_detailed(
                service_id=str(service_id),
                client=self._client,
                body=ServiceUpdate.from_dict(body),
            )
        )

    # ------------------------------------------------------------------
    # Write — delete
    # ------------------------------------------------------------------
    def delete(
        self,
        service_id: str | UUID,
        *,
        dryrun: bool = False,
    ) -> ServiceDeleteResponse:
        """Delete a service."""
        from ._generated.api.seller_services import services_delete

        return unwrap(
            services_delete.sync_detailed(
                service_id=str(service_id),
                client=self._client,
                dryrun=dryrun,
            )
        )
