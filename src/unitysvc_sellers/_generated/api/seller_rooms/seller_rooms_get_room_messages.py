from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.room_view import RoomView
from ...types import UNSET, Response, Unset


def _get_kwargs(
    target: str,
    *,
    after: int | None | Unset = UNSET,
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_after: int | None | Unset
    if isinstance(after, Unset):
        json_after = UNSET
    else:
        json_after = after
    params["after"] = json_after

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/rooms/{target}".format(
            target=quote(str(target), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RoomView | None:
    if response.status_code == 200:
        response_200 = RoomView.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | RoomView]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    target: str,
    *,
    client: AuthenticatedClient | Client,
    after: int | None | Unset = UNSET,
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomView]:
    """Get Room Messages

     The room named by ``target`` (id or handle) and its stored messages
    after ``after``, oldest first.

    Args:
        target (str):
        after (int | None | Unset): The previous page's next
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomView]
    """

    kwargs = _get_kwargs(
        target=target,
        after=after,
        limit=limit,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    target: str,
    *,
    client: AuthenticatedClient | Client,
    after: int | None | Unset = UNSET,
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomView | None:
    """Get Room Messages

     The room named by ``target`` (id or handle) and its stored messages
    after ``after``, oldest first.

    Args:
        target (str):
        after (int | None | Unset): The previous page's next
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomView
    """

    return sync_detailed(
        target=target,
        client=client,
        after=after,
        limit=limit,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    target: str,
    *,
    client: AuthenticatedClient | Client,
    after: int | None | Unset = UNSET,
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomView]:
    """Get Room Messages

     The room named by ``target`` (id or handle) and its stored messages
    after ``after``, oldest first.

    Args:
        target (str):
        after (int | None | Unset): The previous page's next
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomView]
    """

    kwargs = _get_kwargs(
        target=target,
        after=after,
        limit=limit,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    target: str,
    *,
    client: AuthenticatedClient | Client,
    after: int | None | Unset = UNSET,
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomView | None:
    """Get Room Messages

     The room named by ``target`` (id or handle) and its stored messages
    after ``after``, oldest first.

    Args:
        target (str):
        after (int | None | Unset): The previous page's next
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomView
    """

    return (
        await asyncio_detailed(
            target=target,
            client=client,
            after=after,
            limit=limit,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
