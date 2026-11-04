from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.room_feed import RoomFeed
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    since: None | str | Unset = UNSET,
    wait: float | Unset = 0.0,
    limit: int | Unset = 100,
    room: list[UUID] | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_since: None | str | Unset
    if isinstance(since, Unset):
        json_since = UNSET
    else:
        json_since = since
    params["since"] = json_since

    params["wait"] = wait

    params["limit"] = limit

    json_room: list[str] | None | Unset
    if isinstance(room, Unset):
        json_room = UNSET
    elif isinstance(room, list):
        json_room = []
        for room_type_0_item_data in room:
            room_type_0_item = str(room_type_0_item_data)
            json_room.append(room_type_0_item)

    else:
        json_room = room
    params["room"] = json_room

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/rooms/feed",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RoomFeed | None:
    if response.status_code == 200:
        response_200 = RoomFeed.from_dict(response.json())

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
) -> Response[HTTPValidationError | RoomFeed]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    since: None | str | Unset = UNSET,
    wait: float | Unset = 0.0,
    limit: int | Unset = 100,
    room: list[UUID] | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomFeed]:
    """Room Feed

     New messages across every room the account can reach, for a client
    watching many rooms over one connection (#2885).

    ``since`` carries the per-room read position; omit it to start at the
    current tail (no backlog). With ``wait`` the request long-polls until a
    message is stored or the wait elapses. Messages are oldest-first within
    each room and tagged with ``room_id``; the returned ``cursor`` advances
    past them. A key limited by ``room=`` only ever sees its rooms.

    Args:
        since (None | str | Unset): Opaque cursor from a previous response's cursor; omit to start
            at the current tail with no backlog
        wait (float | Unset): Seconds to long-poll for a new message before returning an empty
            page (kept under the proxy read timeout) Default: 0.0.
        limit (int | Unset): Max messages across all rooms Default: 100.
        room (list[UUID] | None | Unset): Limit the feed to these room ids
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomFeed]
    """

    kwargs = _get_kwargs(
        since=since,
        wait=wait,
        limit=limit,
        room=room,
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
    since: None | str | Unset = UNSET,
    wait: float | Unset = 0.0,
    limit: int | Unset = 100,
    room: list[UUID] | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomFeed | None:
    """Room Feed

     New messages across every room the account can reach, for a client
    watching many rooms over one connection (#2885).

    ``since`` carries the per-room read position; omit it to start at the
    current tail (no backlog). With ``wait`` the request long-polls until a
    message is stored or the wait elapses. Messages are oldest-first within
    each room and tagged with ``room_id``; the returned ``cursor`` advances
    past them. A key limited by ``room=`` only ever sees its rooms.

    Args:
        since (None | str | Unset): Opaque cursor from a previous response's cursor; omit to start
            at the current tail with no backlog
        wait (float | Unset): Seconds to long-poll for a new message before returning an empty
            page (kept under the proxy read timeout) Default: 0.0.
        limit (int | Unset): Max messages across all rooms Default: 100.
        room (list[UUID] | None | Unset): Limit the feed to these room ids
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomFeed
    """

    return sync_detailed(
        client=client,
        since=since,
        wait=wait,
        limit=limit,
        room=room,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    since: None | str | Unset = UNSET,
    wait: float | Unset = 0.0,
    limit: int | Unset = 100,
    room: list[UUID] | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomFeed]:
    """Room Feed

     New messages across every room the account can reach, for a client
    watching many rooms over one connection (#2885).

    ``since`` carries the per-room read position; omit it to start at the
    current tail (no backlog). With ``wait`` the request long-polls until a
    message is stored or the wait elapses. Messages are oldest-first within
    each room and tagged with ``room_id``; the returned ``cursor`` advances
    past them. A key limited by ``room=`` only ever sees its rooms.

    Args:
        since (None | str | Unset): Opaque cursor from a previous response's cursor; omit to start
            at the current tail with no backlog
        wait (float | Unset): Seconds to long-poll for a new message before returning an empty
            page (kept under the proxy read timeout) Default: 0.0.
        limit (int | Unset): Max messages across all rooms Default: 100.
        room (list[UUID] | None | Unset): Limit the feed to these room ids
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomFeed]
    """

    kwargs = _get_kwargs(
        since=since,
        wait=wait,
        limit=limit,
        room=room,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    since: None | str | Unset = UNSET,
    wait: float | Unset = 0.0,
    limit: int | Unset = 100,
    room: list[UUID] | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomFeed | None:
    """Room Feed

     New messages across every room the account can reach, for a client
    watching many rooms over one connection (#2885).

    ``since`` carries the per-room read position; omit it to start at the
    current tail (no backlog). With ``wait`` the request long-polls until a
    message is stored or the wait elapses. Messages are oldest-first within
    each room and tagged with ``room_id``; the returned ``cursor`` advances
    past them. A key limited by ``room=`` only ever sees its rooms.

    Args:
        since (None | str | Unset): Opaque cursor from a previous response's cursor; omit to start
            at the current tail with no backlog
        wait (float | Unset): Seconds to long-poll for a new message before returning an empty
            page (kept under the proxy read timeout) Default: 0.0.
        limit (int | Unset): Max messages across all rooms Default: 100.
        room (list[UUID] | None | Unset): Limit the feed to these room ids
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomFeed
    """

    return (
        await asyncio_detailed(
            client=client,
            since=since,
            wait=wait,
            limit=limit,
            room=room,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
