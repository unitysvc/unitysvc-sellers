"""Async mirror of :mod:`unitysvc_sellers.resources.documents`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from .._http import unwrap

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient
    from .._generated.models.document_detail_response import DocumentDetailResponse
    from .._generated.models.document_execute_response import DocumentExecuteResponse
    from .._generated.models.document_test_status_response import (
        DocumentTestStatusResponse,
    )
    from .._generated.models.document_test_update import DocumentTestUpdate


class AsyncDocumentsResource:
    """Async operations on seller test documents."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def get(self, document_id: str | UUID) -> DocumentDetailResponse:
        from .._generated.api.seller import documents_get

        return unwrap(
            await documents_get.asyncio_detailed(
                document_id=str(document_id),
                client=self._client,
            )
        )

    async def execute(
        self,
        document_id: str | UUID,
        *,
        force: bool = False,
    ) -> DocumentExecuteResponse:
        from .._generated.api.seller import documents_execute

        return unwrap(
            await documents_execute.asyncio_detailed(
                document_id=UUID(str(document_id)),
                client=self._client,
                force=force,
            )
        )

    async def update_test(
        self,
        document_id: str | UUID,
        body: DocumentTestUpdate | dict[str, Any],
    ) -> DocumentTestStatusResponse:
        from .._generated.api.seller import documents_update_test
        from .._generated.models.document_test_update import DocumentTestUpdate

        if isinstance(body, dict):
            body = DocumentTestUpdate.from_dict(body)

        return unwrap(
            await documents_update_test.asyncio_detailed(
                document_id=UUID(str(document_id)),
                client=self._client,
                body=body,
            )
        )
