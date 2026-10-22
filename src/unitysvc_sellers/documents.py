"""``client.documents`` — execute and manage seller test documents.

Wraps the seller-tagged ``/v1/seller/documents/*`` operations: fetch a
document record, run a code-example or connectivity-test script, and
update its skip / unskip / pass / fail state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._generated.types import UNSET
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


class Documents:
    """Operations on seller test documents (``/v1/seller/documents``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def get(self, document_id: str | UUID) -> DocumentDetailResponse:
        """Get the full record for a single document."""
        from ._generated.api.seller_documents import documents_get

        return unwrap(
            documents_get.sync_detailed(
                document_id=str(document_id),
                client=self._client,
            )
        )

    def test_details(
        self,
        document_id: str | UUID,
        *,
        interface_id: str | None = None,
        channel: str | None = None,
        upstream: bool = False,
    ) -> TestDetailResponse:
        """Execution details (stdout/stderr/masked env/rendered script) of the
        latest recorded run of the document by one of the seller's services.

        Selectors narrow the run: none → the newest run; ``interface_id``
        (+ optional ``channel``) → that gateway run; ``upstream=True``
        (+ optional ``channel``) → the upstream probe. ``expired=True`` means
        the run's output aged out of retention — re-run the test to reproduce
        it. A service's full result set is :meth:`Services.test_results`.
        """
        from ._generated.api.seller_documents import documents_test_details

        return unwrap(
            documents_test_details.sync_detailed(
                document_id=str(document_id),
                client=self._client,
                interface_id=interface_id,
                channel=channel,
                upstream=upstream,
            )
        )

    def execute(
        self,
        document_id: str | UUID,
        *,
        force: bool = False,
        service_id: str | UUID | None = None,
    ) -> DocumentExecuteResponse:
        """Execute a code-example / connectivity-test document.

        Args:
            document_id: The document to execute.
            force: If True, execute even if the run has already passed.
            service_id: The service to run it for — documents are shared
                between a service and its revisions. Default: the newest of
                the seller's services carrying the document. The run is
                recorded for that service (see :meth:`Services.test_results`).
        """
        from ._generated.api.seller_documents import documents_execute

        return unwrap(
            documents_execute.sync_detailed(
                document_id=UUID(str(document_id)),
                client=self._client,
                force=force,
                service_id=UUID(str(service_id)) if service_id is not None else UNSET,
            )
        )

    def update_test(
        self,
        document_id: str | UUID,
        body: DocumentTestUpdate | dict[str, Any],
    ) -> DocumentTestStatusResponse:
        """Skip (``{"status": "skip"}``) or unskip (``{"status": "pending"}``) a
        document's test. Unskipping also forgets the document's recorded runs,
        so the next run re-proves it. Results are recorded only by the
        platform's own runners."""
        from ._generated.api.seller_documents import documents_update_test
        from ._generated.models.document_test_update import DocumentTestUpdate

        if isinstance(body, dict):
            body = DocumentTestUpdate.from_dict(body)

        return unwrap(
            documents_update_test.sync_detailed(
                document_id=UUID(str(document_id)),
                client=self._client,
                body=body,
            )
        )
