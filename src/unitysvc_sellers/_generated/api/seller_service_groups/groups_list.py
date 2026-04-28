from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cursor_page_service_group_public import CursorPageServiceGroupPublic
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.service_group_status_enum import ServiceGroupStatusEnum, check_service_group_status_enum
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    status: None | ServiceGroupStatusEnum | Unset = UNSET,
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
    elif isinstance(status, str):
        json_status = status
    else:
        json_status = status
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/service-groups",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CursorPageServiceGroupPublic | ErrorResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CursorPageServiceGroupPublic.from_dict(response.json())

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
) -> Response[CursorPageServiceGroupPublic | ErrorResponse | HTTPValidationError]:
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
    status: None | ServiceGroupStatusEnum | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CursorPageServiceGroupPublic | ErrorResponse | HTTPValidationError]:
    """List Seller Groups

     List seller's own service groups.

    Returns groups owned by the current seller, paginated using cursor-based
    (keyset) pagination ordered newest-first.

    Args:
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        status (None | ServiceGroupStatusEnum | Unset): Filter by status
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CursorPageServiceGroupPublic | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        cursor=cursor,
        limit=limit,
        status=status,
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
    status: None | ServiceGroupStatusEnum | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CursorPageServiceGroupPublic | ErrorResponse | HTTPValidationError | None:
    """List Seller Groups

     List seller's own service groups.

    Returns groups owned by the current seller, paginated using cursor-based
    (keyset) pagination ordered newest-first.

    Args:
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        status (None | ServiceGroupStatusEnum | Unset): Filter by status
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CursorPageServiceGroupPublic | ErrorResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        cursor=cursor,
        limit=limit,
        status=status,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    cursor: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    status: None | ServiceGroupStatusEnum | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[CursorPageServiceGroupPublic | ErrorResponse | HTTPValidationError]:
    """List Seller Groups

     List seller's own service groups.

    Returns groups owned by the current seller, paginated using cursor-based
    (keyset) pagination ordered newest-first.

    Args:
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        status (None | ServiceGroupStatusEnum | Unset): Filter by status
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CursorPageServiceGroupPublic | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        cursor=cursor,
        limit=limit,
        status=status,
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
    status: None | ServiceGroupStatusEnum | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> CursorPageServiceGroupPublic | ErrorResponse | HTTPValidationError | None:
    """List Seller Groups

     List seller's own service groups.

    Returns groups owned by the current seller, paginated using cursor-based
    (keyset) pagination ordered newest-first.

    Args:
        cursor (None | str | Unset): Opaque pagination cursor from a previous response's
            `next_cursor`. Omit to start from the first page.
        limit (int | Unset): Page size (default 50, max 200). Default: 50.
        status (None | ServiceGroupStatusEnum | Unset): Filter by status
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CursorPageServiceGroupPublic | ErrorResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            cursor=cursor,
            limit=limit,
            status=status,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
