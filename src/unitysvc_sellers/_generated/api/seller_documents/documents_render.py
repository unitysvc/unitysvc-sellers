from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_render_response import DocumentRenderResponse
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response


def _get_kwargs(
    document_id: str,
    *,
    interface: UUID,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_interface = str(interface)
    params["interface"] = json_interface

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/documents/{document_id}/render".format(
            document_id=quote(str(document_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DocumentRenderResponse | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = DocumentRenderResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if response.status_code == 422:
        response_422 = ErrorResponse.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DocumentRenderResponse | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    document_id: str,
    *,
    client: AuthenticatedClient | Client,
    interface: UUID,
) -> Response[DocumentRenderResponse | ErrorResponse]:
    """Render Document

     Render a code-example or connectivity-test document for a specific interface.

    **Public, unauthenticated, gateway mode only.**  Render context is the
    named :class:`AccessInterface`'s gateway URL + ``routing_key``, plus
    the listing's ``enrollment_vars`` / ``ops_testing_parameters``
    (``params``) / ``routing_vars``.  No upstream credentials are ever
    inlined — ``UNITYSVC_API_KEY`` is read from the runtime environment —
    so the rendered output is by construction the same script a customer
    would copy off the marketplace service-detail page. Anonymous access
    is therefore safe and intentional: ``usvc_seller services run-tests``
    (seller-owned drafts), the marketplace preview, and any third-party
    integration that wants the canonical client snippet all hit the same
    URL with no auth.

    Upstream-mode rendering (which would expand ``${ secrets.X }`` against
    the seller's secret store and inline the resolved values into the
    rendered script) is intentionally not exposed over HTTP.  Internal
    callers — the upstream-connectivity Celery sweep and worker-side
    document execution — invoke :func:`render_document_upstream` directly.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the
    input was a template.

    Args:
        document_id (str):
        interface (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentRenderResponse | ErrorResponse]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        interface=interface,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    document_id: str,
    *,
    client: AuthenticatedClient | Client,
    interface: UUID,
) -> DocumentRenderResponse | ErrorResponse | None:
    """Render Document

     Render a code-example or connectivity-test document for a specific interface.

    **Public, unauthenticated, gateway mode only.**  Render context is the
    named :class:`AccessInterface`'s gateway URL + ``routing_key``, plus
    the listing's ``enrollment_vars`` / ``ops_testing_parameters``
    (``params``) / ``routing_vars``.  No upstream credentials are ever
    inlined — ``UNITYSVC_API_KEY`` is read from the runtime environment —
    so the rendered output is by construction the same script a customer
    would copy off the marketplace service-detail page. Anonymous access
    is therefore safe and intentional: ``usvc_seller services run-tests``
    (seller-owned drafts), the marketplace preview, and any third-party
    integration that wants the canonical client snippet all hit the same
    URL with no auth.

    Upstream-mode rendering (which would expand ``${ secrets.X }`` against
    the seller's secret store and inline the resolved values into the
    rendered script) is intentionally not exposed over HTTP.  Internal
    callers — the upstream-connectivity Celery sweep and worker-side
    document execution — invoke :func:`render_document_upstream` directly.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the
    input was a template.

    Args:
        document_id (str):
        interface (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentRenderResponse | ErrorResponse
    """

    return sync_detailed(
        document_id=document_id,
        client=client,
        interface=interface,
    ).parsed


async def asyncio_detailed(
    document_id: str,
    *,
    client: AuthenticatedClient | Client,
    interface: UUID,
) -> Response[DocumentRenderResponse | ErrorResponse]:
    """Render Document

     Render a code-example or connectivity-test document for a specific interface.

    **Public, unauthenticated, gateway mode only.**  Render context is the
    named :class:`AccessInterface`'s gateway URL + ``routing_key``, plus
    the listing's ``enrollment_vars`` / ``ops_testing_parameters``
    (``params``) / ``routing_vars``.  No upstream credentials are ever
    inlined — ``UNITYSVC_API_KEY`` is read from the runtime environment —
    so the rendered output is by construction the same script a customer
    would copy off the marketplace service-detail page. Anonymous access
    is therefore safe and intentional: ``usvc_seller services run-tests``
    (seller-owned drafts), the marketplace preview, and any third-party
    integration that wants the canonical client snippet all hit the same
    URL with no auth.

    Upstream-mode rendering (which would expand ``${ secrets.X }`` against
    the seller's secret store and inline the resolved values into the
    rendered script) is intentionally not exposed over HTTP.  Internal
    callers — the upstream-connectivity Celery sweep and worker-side
    document execution — invoke :func:`render_document_upstream` directly.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the
    input was a template.

    Args:
        document_id (str):
        interface (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentRenderResponse | ErrorResponse]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        interface=interface,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    document_id: str,
    *,
    client: AuthenticatedClient | Client,
    interface: UUID,
) -> DocumentRenderResponse | ErrorResponse | None:
    """Render Document

     Render a code-example or connectivity-test document for a specific interface.

    **Public, unauthenticated, gateway mode only.**  Render context is the
    named :class:`AccessInterface`'s gateway URL + ``routing_key``, plus
    the listing's ``enrollment_vars`` / ``ops_testing_parameters``
    (``params``) / ``routing_vars``.  No upstream credentials are ever
    inlined — ``UNITYSVC_API_KEY`` is read from the runtime environment —
    so the rendered output is by construction the same script a customer
    would copy off the marketplace service-detail page. Anonymous access
    is therefore safe and intentional: ``usvc_seller services run-tests``
    (seller-owned drafts), the marketplace preview, and any third-party
    integration that wants the canonical client snippet all hit the same
    URL with no auth.

    Upstream-mode rendering (which would expand ``${ secrets.X }`` against
    the seller's secret store and inline the resolved values into the
    rendered script) is intentionally not exposed over HTTP.  Internal
    callers — the upstream-connectivity Celery sweep and worker-side
    document execution — invoke :func:`render_document_upstream` directly.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the
    input was a template.

    Args:
        document_id (str):
        interface (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentRenderResponse | ErrorResponse
    """

    return (
        await asyncio_detailed(
            document_id=document_id,
            client=client,
            interface=interface,
        )
    ).parsed
