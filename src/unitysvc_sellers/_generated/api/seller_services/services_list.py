from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cursor_page_service_public import CursorPageServicePublic
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    status: None | str | Unset = UNSET,
    service_type: None | str | Unset = UNSET,
    listing_type: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_cursor: None | str | Unset
    if isinstance(cursor, Unset):
        json_cursor = UNSET
    else:
        json_cursor = cursor
    params["cursor"] = json_cursor

    params["limit"] = limit

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    json_service_type: None | str | Unset
    if isinstance(service_type, Unset):
        json_service_type = UNSET
    else:
        json_service_type = service_type
    params["service_type"] = json_service_type

    json_listing_type: None | str | Unset
    if isinstance(listing_type, Unset):
        json_listing_type = UNSET
    else:
        json_listing_type = listing_type
    params["listing_type"] = json_listing_type

    json_name: None | str | Unset
    if isinstance(name, Unset):
        json_name = UNSET
    else:
        json_name = name
    params["name"] = json_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/services",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CursorPageServicePublic | ErrorResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CursorPageServicePublic.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CursorPageServicePublic | ErrorResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    status: None | str | Unset = UNSET,
    service_type: None | str | Unset = UNSET,
    listing_type: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CursorPageServicePublic | ErrorResponse | HTTPValidationError]:
    """List My Services

     List all services for the current seller.

    Services are the identity layer connecting sellers to content versions
    (Provider, ServiceOffering, ServiceListing). Results are paginated using
    cursor-based (keyset) pagination, ordered newest-first by `created_at`.

    Query Parameters:
    - cursor: Opaque pagination cursor from a previous response's
      ``next_cursor``. Omit to start from the first page.
    - limit: Page size (default: 50, max: 200)
    - status: Filter by service status (draft, pending, review, active, rejected, suspended)
    - service_type: Filter by service type (e.g., llm, vectordb, embedding)
    - listing_type: Filter by listing type (regular, byok, self_hosted)
    - name: Search by name, display name, or provider name (case-insensitive partial match)

    Args:
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        status (None | str | Unset):
        service_type (None | str | Unset): Filter by service type
        listing_type (None | str | Unset): Filter by listing type
        name (None | str | Unset): Search by name, display name, or provider name (case-
            insensitive partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CursorPageServicePublic | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        cursor=cursor,
        limit=limit,
        status=status,
        service_type=service_type,
        listing_type=listing_type,
        name=name,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    status: None | str | Unset = UNSET,
    service_type: None | str | Unset = UNSET,
    listing_type: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CursorPageServicePublic | ErrorResponse | HTTPValidationError | None:
    """List My Services

     List all services for the current seller.

    Services are the identity layer connecting sellers to content versions
    (Provider, ServiceOffering, ServiceListing). Results are paginated using
    cursor-based (keyset) pagination, ordered newest-first by `created_at`.

    Query Parameters:
    - cursor: Opaque pagination cursor from a previous response's
      ``next_cursor``. Omit to start from the first page.
    - limit: Page size (default: 50, max: 200)
    - status: Filter by service status (draft, pending, review, active, rejected, suspended)
    - service_type: Filter by service type (e.g., llm, vectordb, embedding)
    - listing_type: Filter by listing type (regular, byok, self_hosted)
    - name: Search by name, display name, or provider name (case-insensitive partial match)

    Args:
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        status (None | str | Unset):
        service_type (None | str | Unset): Filter by service type
        listing_type (None | str | Unset): Filter by listing type
        name (None | str | Unset): Search by name, display name, or provider name (case-
            insensitive partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CursorPageServicePublic | ErrorResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        cursor=cursor,
        limit=limit,
        status=status,
        service_type=service_type,
        listing_type=listing_type,
        name=name,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    status: None | str | Unset = UNSET,
    service_type: None | str | Unset = UNSET,
    listing_type: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CursorPageServicePublic | ErrorResponse | HTTPValidationError]:
    """List My Services

     List all services for the current seller.

    Services are the identity layer connecting sellers to content versions
    (Provider, ServiceOffering, ServiceListing). Results are paginated using
    cursor-based (keyset) pagination, ordered newest-first by `created_at`.

    Query Parameters:
    - cursor: Opaque pagination cursor from a previous response's
      ``next_cursor``. Omit to start from the first page.
    - limit: Page size (default: 50, max: 200)
    - status: Filter by service status (draft, pending, review, active, rejected, suspended)
    - service_type: Filter by service type (e.g., llm, vectordb, embedding)
    - listing_type: Filter by listing type (regular, byok, self_hosted)
    - name: Search by name, display name, or provider name (case-insensitive partial match)

    Args:
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        status (None | str | Unset):
        service_type (None | str | Unset): Filter by service type
        listing_type (None | str | Unset): Filter by listing type
        name (None | str | Unset): Search by name, display name, or provider name (case-
            insensitive partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CursorPageServicePublic | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        cursor=cursor,
        limit=limit,
        status=status,
        service_type=service_type,
        listing_type=listing_type,
        name=name,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    status: None | str | Unset = UNSET,
    service_type: None | str | Unset = UNSET,
    listing_type: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CursorPageServicePublic | ErrorResponse | HTTPValidationError | None:
    """List My Services

     List all services for the current seller.

    Services are the identity layer connecting sellers to content versions
    (Provider, ServiceOffering, ServiceListing). Results are paginated using
    cursor-based (keyset) pagination, ordered newest-first by `created_at`.

    Query Parameters:
    - cursor: Opaque pagination cursor from a previous response's
      ``next_cursor``. Omit to start from the first page.
    - limit: Page size (default: 50, max: 200)
    - status: Filter by service status (draft, pending, review, active, rejected, suspended)
    - service_type: Filter by service type (e.g., llm, vectordb, embedding)
    - listing_type: Filter by listing type (regular, byok, self_hosted)
    - name: Search by name, display name, or provider name (case-insensitive partial match)

    Args:
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        status (None | str | Unset):
        service_type (None | str | Unset): Filter by service type
        listing_type (None | str | Unset): Filter by listing type
        name (None | str | Unset): Search by name, display name, or provider name (case-
            insensitive partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CursorPageServicePublic | ErrorResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            cursor=cursor,
            limit=limit,
            status=status,
            service_type=service_type,
            listing_type=listing_type,
            name=name,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
