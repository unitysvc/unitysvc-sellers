"""Async mirror of :mod:`documents`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._generated.types import UNSET
from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.document_detail_response import DocumentDetailResponse
    from ._generated.models.document_execute_response import DocumentExecuteResponse
    from ._generated.models.document_render_response import DocumentRenderResponse
    from ._generated.models.document_test_status_response import (
        DocumentTestStatusResponse,
    )
    from ._generated.models.document_test_update import DocumentTestUpdate


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

    async def render(
        self,
        document_id: str | UUID,
        *,
        interface: str | UUID | None = None,
    ) -> DocumentRenderResponse:
        """Render a code-example / connectivity-test on demand (server-side).

        Calls ``GET /seller/documents/{id}/render?interface=<uuid>`` and
        returns the parsed body as a typed
        :class:`DocumentRenderResponse`.  Two modes selected by ``interface``:

        - ``interface=<uuid>`` → gateway / e2e mode.  Render context is built
          from that user :class:`AccessInterface` (gateway URL, routing_key)
          plus the listing's ``enrollment_vars`` / ``params`` /
          ``routing_vars``.  Each rendered script is interface-specific —
          ``service_base_url``, ``routing_key.*``, listing-level vars are all
          inlined into the returned ``content``.
        - ``interface`` omitted → upstream mode.  Render context is built from
          the offering's ``upstream_access_config``.  Output matches
          ``usvc_seller data run-tests`` byte-for-byte.

        ``filename`` has the ``.j2`` suffix stripped when the input was a
        template (e.g. ``connectivity-v1.sh.j2`` → ``connectivity-v1.sh``).
        """
        from ._generated.api.seller_documents import documents_render

        iface_arg: Any = UNSET if interface is None else UUID(str(interface))
        return unwrap(
            await documents_render.asyncio_detailed(
                document_id=str(document_id),
                client=self._client,
                interface=iface_arg,
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
