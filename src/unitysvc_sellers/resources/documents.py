"""``client.documents`` — execute and manage seller test documents.

Wraps the seller-tagged ``/v1/seller/documents/*`` operations: fetch a
document record, run a code-example or connectivity-test script, and
update its skip / unskip / pass / fail state.
"""

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


class DocumentsResource:
    """Operations on seller test documents (``/v1/seller/documents``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def get(self, document_id: str | UUID) -> DocumentDetailResponse:
        """Get the full record for a single document."""
        from .._generated.api.seller import documents_get

        return unwrap(
            documents_get.sync_detailed(
                document_id=str(document_id),
                client=self._client,
            )
        )

    def execute(
        self,
        document_id: str | UUID,
        *,
        force: bool = False,
    ) -> DocumentExecuteResponse:
        """Execute a code-example / connectivity-test document.

        Args:
            document_id: The document to execute.
            force: If True, execute even if the document was previously
                marked skipped or has a recent successful run.
        """
        from .._generated.api.seller import documents_execute

        return unwrap(
            documents_execute.sync_detailed(
                document_id=UUID(str(document_id)),
                client=self._client,
                force=force,
            )
        )

    def update_test(
        self,
        document_id: str | UUID,
        body: DocumentTestUpdate | dict[str, Any],
    ) -> DocumentTestStatusResponse:
        """Update a document's test state (skip / unskip / mark pass-fail)."""
        from .._generated.api.seller import documents_update_test
        from .._generated.models.document_test_update import DocumentTestUpdate

        if isinstance(body, dict):
            body = DocumentTestUpdate.from_dict(body)

        return unwrap(
            documents_update_test.sync_detailed(
                document_id=UUID(str(document_id)),
                client=self._client,
                body=body,
            )
        )
