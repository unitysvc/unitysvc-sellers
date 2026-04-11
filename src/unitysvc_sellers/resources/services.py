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

from .._http import unwrap

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient
    from .._generated.models.cursor_page_service_public import CursorPageServicePublic
    from .._generated.models.list_price_update import ListPriceUpdate
    from .._generated.models.list_price_update_response import ListPriceUpdateResponse
    from .._generated.models.routing_vars_update import RoutingVarsUpdate
    from .._generated.models.routing_vars_update_response import (
        RoutingVarsUpdateResponse,
    )
    from .._generated.models.service_data_input import ServiceDataInput
    from .._generated.models.service_delete_response import ServiceDeleteResponse
    from .._generated.models.service_detail_response import ServiceDetailResponse
    from .._generated.models.service_status_update import ServiceStatusUpdate
    from .._generated.models.service_status_update_response import (
        ServiceStatusUpdateResponse,
    )
    from .._generated.models.task_queued_response import TaskQueuedResponse
    from .._generated.models.test_env_response import TestEnvResponse


class ServicesResource:
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

        Args:
            cursor: Opaque continuation token returned by the previous
                page as ``next_cursor``. Omit for the first page.
            limit: Page size (backend default and max vary — typically
                50).
            status: Filter by service status (e.g. ``"draft"``, ``"active"``).
            service_type: Filter by service type (e.g. ``"llm"``).
            listing_type: Filter by listing type (e.g. ``"regular"``).
            name: Case-insensitive partial match on name / display_name /
                provider name.

        Returns:
            :class:`CursorPageServicePublic` with ``data``,
            ``next_cursor``, and ``has_more`` fields.
        """
        from .._generated.api.seller_services import services_list
        from .._generated.types import UNSET

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
        from .._generated.api.seller_services import services_get

        return unwrap(
            services_get.sync_detailed(
                service_id=str(service_id),
                client=self._client,
            )
        )

    def get_test_env(self, service_id: str | UUID) -> TestEnvResponse:
        """Return the rendered environment used to run code-example scripts for a service."""
        from .._generated.api.seller_services import services_get_test_env

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
        *,
        dryrun: bool = False,
    ) -> TaskQueuedResponse:
        """Submit a provider/offering/listing bundle for ingestion.

        Mirrors ``POST /v1/seller/services``. The server processes the
        upload asynchronously and returns a ``TaskQueuedResponse`` with a
        task id you can poll. Use :meth:`get` to check the resulting
        service once the task completes.

        Args:
            body: Either a typed :class:`ServiceDataInput` or a plain
                dict matching its shape (the high-level
                :func:`unitysvc_sellers.resources.upload.upload_directory`
                helper builds these from a seller's catalog directory).
            dryrun: If True, validate the payload without persisting it.
        """
        from .._generated.api.seller_services import services_upload
        from .._generated.models.service_data_input import ServiceDataInput

        if isinstance(body, dict):
            body = ServiceDataInput.from_dict(body)

        return unwrap(
            services_upload.sync_detailed(
                client=self._client,
                body=body,
                dryrun=dryrun,
            )
        )

    # ------------------------------------------------------------------
    # Write — single-service updates
    # ------------------------------------------------------------------
    def set_status(
        self,
        service_id: str | UUID,
        body: ServiceStatusUpdate | dict[str, Any],
    ) -> ServiceStatusUpdateResponse:
        """Update a service's seller-facing status (draft / ready / deprecated)."""
        from .._generated.api.seller_services import services_set_status
        from .._generated.models.service_status_update import ServiceStatusUpdate

        if isinstance(body, dict):
            body = ServiceStatusUpdate.from_dict(body)

        return unwrap(
            services_set_status.sync_detailed(
                service_id=str(service_id),
                client=self._client,
                body=body,
            )
        )

    def set_routing_vars(
        self,
        service_id: str | UUID,
        body: RoutingVarsUpdate | dict[str, Any],
    ) -> RoutingVarsUpdateResponse:
        """Update the seller-managed routing variables used for request templating."""
        from .._generated.api.seller_services import services_set_routing_vars
        from .._generated.models.routing_vars_update import RoutingVarsUpdate

        if isinstance(body, dict):
            body = RoutingVarsUpdate.from_dict(body)

        return unwrap(
            services_set_routing_vars.sync_detailed(
                service_id=str(service_id),
                client=self._client,
                body=body,
            )
        )

    def set_list_price(
        self,
        service_id: str | UUID,
        body: ListPriceUpdate | dict[str, Any],
    ) -> ListPriceUpdateResponse:
        """Update a service's customer-facing list price."""
        from .._generated.api.seller_services import services_set_list_price
        from .._generated.models.list_price_update import ListPriceUpdate

        if isinstance(body, dict):
            body = ListPriceUpdate.from_dict(body)

        return unwrap(
            services_set_list_price.sync_detailed(
                service_id=str(service_id),
                client=self._client,
                body=body,
            )
        )

    def delete(
        self,
        service_id: str | UUID,
        *,
        dryrun: bool = False,
    ) -> ServiceDeleteResponse:
        """Delete a service.

        Args:
            service_id: ID of the service to delete.
            dryrun: If True, return what would be deleted without
                actually deleting anything.
        """
        from .._generated.api.seller_services import services_delete

        return unwrap(
            services_delete.sync_detailed(
                service_id=str(service_id),
                client=self._client,
                dryrun=dryrun,
            )
        )
