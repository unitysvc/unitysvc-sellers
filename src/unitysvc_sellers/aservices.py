"""Async mirror of :mod:`services`.

Each method has the same signature as the corresponding sync method on
:class:`~services.Services` but is
declared ``async def`` and calls the generated ``asyncio_detailed``
entry point.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.cursor_page_service_public import (
        CursorPageServicePublic,
    )
    from ._generated.models.service_data_input import ServiceDataInput
    from ._generated.models.service_delete_response import ServiceDeleteResponse
    from ._generated.models.service_detail_response import ServiceDetailResponse
    from ._generated.models.service_update_response import ServiceUpdateResponse
    from ._generated.models.task_queued_response import TaskQueuedResponse
    from ._generated.models.test_env_response import TestEnvResponse


class AsyncServices:
    """Async operations on the seller's service catalog."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: str | None = None,
        service_type: str | None = None,
        listing_type: str | None = None,
        name: str | None = None,
    ) -> CursorPageServicePublic:
        from ._generated.api.seller_services import services_list
        from ._generated.types import UNSET

        return unwrap(
            await services_list.asyncio_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,
                service_type=service_type if service_type is not None else UNSET,
                listing_type=listing_type if listing_type is not None else UNSET,
                name=name if name is not None else UNSET,
            )
        )

    async def get(self, service_id: str | UUID) -> ServiceDetailResponse:
        from ._generated.api.seller_services import services_get

        return unwrap(
            await services_get.asyncio_detailed(
                service_id=str(service_id),
                client=self._client,
            )
        )

    async def get_test_env(self, service_id: str | UUID) -> TestEnvResponse:
        from ._generated.api.seller_services import services_get_test_env

        return unwrap(
            await services_get_test_env.asyncio_detailed(
                service_id=str(service_id),
                client=self._client,
            )
        )

    async def upload(
        self,
        body: ServiceDataInput | dict[str, Any],
        *,
        dryrun: bool = False,
    ) -> TaskQueuedResponse:
        from ._generated.api.seller_services import services_upload
        from ._generated.models.service_data_input import ServiceDataInput

        if isinstance(body, dict):
            body = ServiceDataInput.from_dict(body)

        return unwrap(
            await services_upload.asyncio_detailed(
                client=self._client,
                body=body,
                dryrun=dryrun,
            )
        )

    async def update(
        self,
        service_id: str | UUID,
        body: dict[str, Any],
    ) -> ServiceUpdateResponse:
        """Update a service — status, visibility, routing vars, and/or list price."""
        from ._generated.api.seller_services import services_update
        from ._generated.models.service_update import ServiceUpdate

        return unwrap(
            await services_update.asyncio_detailed(
                service_id=str(service_id),
                client=self._client,
                body=ServiceUpdate.from_dict(body),
            )
        )

    async def delete(
        self,
        service_id: str | UUID,
        *,
        dryrun: bool = False,
    ) -> ServiceDeleteResponse:
        from ._generated.api.seller_services import services_delete

        return unwrap(
            await services_delete.asyncio_detailed(
                service_id=str(service_id),
                client=self._client,
                dryrun=dryrun,
            )
        )
