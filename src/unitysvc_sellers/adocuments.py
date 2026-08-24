"""Async mirror of :mod:`documents`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.document_detail_response import DocumentDetailResponse
    from ._generated.models.document_execute_response import DocumentExecuteResponse
    from ._generated.models.document_test_status_response import (
        DocumentTestStatusResponse,
    )
    from ._generated.models.document_test_update import DocumentTestUpdate
    from ._generated.models.test_detail_response import TestDetailResponse


class AsyncDocuments:
    """Async operations on seller test documents."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def get(self, document_id: str | UUID) -> DocumentDetailResponse:
        from ._generated.api.seller_documents import documents_get

        return unwrap(
            await documents_get.asyncio_detailed(
                document_id=str(document_id),
                client=self._client,
            )
        )

    async def test_details(
        self,
        document_id: str | UUID,
        *,
        interface_id: str | None = None,
        channel: str | None = None,
        upstream: bool = False,
    ) -> TestDetailResponse:
        """Execution details (stdout/stderr/masked env/rendered script) for
        one test-result cell (unitysvc#1901).

        Selectors mirror how results are recorded: none → the flat
        single-document block; ``interface_id`` (+ optional ``channel``) →
        that gateway cell; ``upstream=True`` (+ optional ``channel``) → the
        upstream probe record. ``expired=True`` on the response means the
        cell's detail blob aged out of retention — re-run the test to
        reproduce the details.
        """
        from ._generated.api.seller_documents import documents_test_details

        return unwrap(
            await documents_test_details.asyncio_detailed(
                document_id=str(document_id),
                client=self._client,
                interface_id=interface_id,
                channel=channel,
                upstream=upstream,
            )
        )

    async def execute(
        self,
        document_id: str | UUID,
        *,
        force: bool = False,
    ) -> DocumentExecuteResponse:
        from ._generated.api.seller_documents import documents_execute

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
        from ._generated.api.seller_documents import documents_update_test
        from ._generated.models.document_test_update import DocumentTestUpdate

        if isinstance(body, dict):
            body = DocumentTestUpdate.from_dict(body)

        return unwrap(
            await documents_update_test.asyncio_detailed(
                document_id=UUID(str(document_id)),
                client=self._client,
                body=body,
            )
        )
