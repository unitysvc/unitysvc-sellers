from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.room_post_request import RoomPostRequest
from ...models.room_post_response import RoomPostResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    target: str,
    *,
    body: RoomPostRequest,
    fallback: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    params["fallback"] = fallback

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/rooms/{target}".format(
            target=quote(str(target), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RoomPostResponse | None:
    if response.status_code == 202:
        response_202 = RoomPostResponse.from_dict(response.json())

        return response_202

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | RoomPostResponse]:
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
    body: RoomPostRequest,
    fallback: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomPostResponse]:
    """Post Room Message To

     Post a message to the room named by ``target`` (a room id, or a
    handle such as ``me``); falls back to ``me`` if the account can't post
    there, unless ``fallback=false``.

    Args:
        target (str):
        fallback (bool | Unset): Post to your me room when this room can't take the post; false
            returns 404/403 instead (interactive clients) Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoomPostRequest): A message in the msg format.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomPostResponse]
    """

    kwargs = _get_kwargs(
        target=target,
        body=body,
        fallback=fallback,
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
    body: RoomPostRequest,
    fallback: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomPostResponse | None:
    """Post Room Message To

     Post a message to the room named by ``target`` (a room id, or a
    handle such as ``me``); falls back to ``me`` if the account can't post
    there, unless ``fallback=false``.

    Args:
        target (str):
        fallback (bool | Unset): Post to your me room when this room can't take the post; false
            returns 404/403 instead (interactive clients) Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoomPostRequest): A message in the msg format.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomPostResponse
    """

    return sync_detailed(
        target=target,
        client=client,
        body=body,
        fallback=fallback,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    target: str,
    *,
    client: AuthenticatedClient | Client,
    body: RoomPostRequest,
    fallback: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomPostResponse]:
    """Post Room Message To

     Post a message to the room named by ``target`` (a room id, or a
    handle such as ``me``); falls back to ``me`` if the account can't post
    there, unless ``fallback=false``.

    Args:
        target (str):
        fallback (bool | Unset): Post to your me room when this room can't take the post; false
            returns 404/403 instead (interactive clients) Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoomPostRequest): A message in the msg format.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomPostResponse]
    """

    kwargs = _get_kwargs(
        target=target,
        body=body,
        fallback=fallback,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    target: str,
    *,
    client: AuthenticatedClient | Client,
    body: RoomPostRequest,
    fallback: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomPostResponse | None:
    """Post Room Message To

     Post a message to the room named by ``target`` (a room id, or a
    handle such as ``me``); falls back to ``me`` if the account can't post
    there, unless ``fallback=false``.

    Args:
        target (str):
        fallback (bool | Unset): Post to your me room when this room can't take the post; false
            returns 404/403 instead (interactive clients) Default: True.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoomPostRequest): A message in the msg format.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomPostResponse
    """

    return (
        await asyncio_detailed(
            target=target,
            client=client,
            body=body,
            fallback=fallback,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
