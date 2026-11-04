from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.room_list import RoomList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    kind: None | str | Unset = UNSET,
    enrollment: None | Unset | UUID = UNSET,
    service: None | Unset | UUID = UNSET,
    q: None | str | Unset = UNSET,
    new_activity: bool | Unset = False,
    limit: int | None | Unset = UNSET,
    cursor: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_kind: None | str | Unset
    if isinstance(kind, Unset):
        json_kind = UNSET
    else:
        json_kind = kind
    params["kind"] = json_kind

    json_enrollment: None | str | Unset
    if isinstance(enrollment, Unset):
        json_enrollment = UNSET
    elif isinstance(enrollment, UUID):
        json_enrollment = str(enrollment)
    else:
        json_enrollment = enrollment
    params["enrollment"] = json_enrollment

    json_service: None | str | Unset
    if isinstance(service, Unset):
        json_service = UNSET
    elif isinstance(service, UUID):
        json_service = str(service)
    else:
        json_service = service
    params["service"] = json_service

    json_q: None | str | Unset
    if isinstance(q, Unset):
        json_q = UNSET
    else:
        json_q = q
    params["q"] = json_q

    params["new_activity"] = new_activity

    json_limit: int | None | Unset
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    json_cursor: None | str | Unset
    if isinstance(cursor, Unset):
        json_cursor = UNSET
    else:
        json_cursor = cursor
    params["cursor"] = json_cursor

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/rooms",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RoomList | None:
    if response.status_code == 200:
        response_200 = RoomList.from_dict(response.json())

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
) -> Response[HTTPValidationError | RoomList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    kind: None | str | Unset = UNSET,
    enrollment: None | Unset | UUID = UNSET,
    service: None | Unset | UUID = UNSET,
    q: None | str | Unset = UNSET,
    new_activity: bool | Unset = False,
    limit: int | None | Unset = UNSET,
    cursor: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomList]:
    """List Rooms

     The rooms the account can reach, with its role in each, most
    recently active first, optionally narrowed by kind, enrollment,
    service, name prefix (``q``) or unseen activity (``new_activity``).
    Paging is opt-in: with ``limit``, a page at a time via the opaque
    ``cursor``; without it, every room. A key limited by ``room=`` sees
    only its rooms.

    Args:
        kind (None | str | Unset): Only rooms of this kind
        enrollment (None | Unset | UUID): Only rooms of this enrollment
        service (None | Unset | UUID): Only rooms of this service (not its enrollments' rooms)
        q (None | str | Unset): Only rooms whose name starts with this (case-insensitive)
        new_activity (bool | Unset): Only rooms with conversation activity the account hasn't seen
            Default: False.
        limit (int | None | Unset): Rooms per page; omit for every room (after ``cursor``)
        cursor (None | str | Unset): Opaque cursor from a previous response's next_cursor; omit to
            start from the first page
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomList]
    """

    kwargs = _get_kwargs(
        kind=kind,
        enrollment=enrollment,
        service=service,
        q=q,
        new_activity=new_activity,
        limit=limit,
        cursor=cursor,
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
    kind: None | str | Unset = UNSET,
    enrollment: None | Unset | UUID = UNSET,
    service: None | Unset | UUID = UNSET,
    q: None | str | Unset = UNSET,
    new_activity: bool | Unset = False,
    limit: int | None | Unset = UNSET,
    cursor: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomList | None:
    """List Rooms

     The rooms the account can reach, with its role in each, most
    recently active first, optionally narrowed by kind, enrollment,
    service, name prefix (``q``) or unseen activity (``new_activity``).
    Paging is opt-in: with ``limit``, a page at a time via the opaque
    ``cursor``; without it, every room. A key limited by ``room=`` sees
    only its rooms.

    Args:
        kind (None | str | Unset): Only rooms of this kind
        enrollment (None | Unset | UUID): Only rooms of this enrollment
        service (None | Unset | UUID): Only rooms of this service (not its enrollments' rooms)
        q (None | str | Unset): Only rooms whose name starts with this (case-insensitive)
        new_activity (bool | Unset): Only rooms with conversation activity the account hasn't seen
            Default: False.
        limit (int | None | Unset): Rooms per page; omit for every room (after ``cursor``)
        cursor (None | str | Unset): Opaque cursor from a previous response's next_cursor; omit to
            start from the first page
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomList
    """

    return sync_detailed(
        client=client,
        kind=kind,
        enrollment=enrollment,
        service=service,
        q=q,
        new_activity=new_activity,
        limit=limit,
        cursor=cursor,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    kind: None | str | Unset = UNSET,
    enrollment: None | Unset | UUID = UNSET,
    service: None | Unset | UUID = UNSET,
    q: None | str | Unset = UNSET,
    new_activity: bool | Unset = False,
    limit: int | None | Unset = UNSET,
    cursor: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomList]:
    """List Rooms

     The rooms the account can reach, with its role in each, most
    recently active first, optionally narrowed by kind, enrollment,
    service, name prefix (``q``) or unseen activity (``new_activity``).
    Paging is opt-in: with ``limit``, a page at a time via the opaque
    ``cursor``; without it, every room. A key limited by ``room=`` sees
    only its rooms.

    Args:
        kind (None | str | Unset): Only rooms of this kind
        enrollment (None | Unset | UUID): Only rooms of this enrollment
        service (None | Unset | UUID): Only rooms of this service (not its enrollments' rooms)
        q (None | str | Unset): Only rooms whose name starts with this (case-insensitive)
        new_activity (bool | Unset): Only rooms with conversation activity the account hasn't seen
            Default: False.
        limit (int | None | Unset): Rooms per page; omit for every room (after ``cursor``)
        cursor (None | str | Unset): Opaque cursor from a previous response's next_cursor; omit to
            start from the first page
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomList]
    """

    kwargs = _get_kwargs(
        kind=kind,
        enrollment=enrollment,
        service=service,
        q=q,
        new_activity=new_activity,
        limit=limit,
        cursor=cursor,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    kind: None | str | Unset = UNSET,
    enrollment: None | Unset | UUID = UNSET,
    service: None | Unset | UUID = UNSET,
    q: None | str | Unset = UNSET,
    new_activity: bool | Unset = False,
    limit: int | None | Unset = UNSET,
    cursor: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomList | None:
    """List Rooms

     The rooms the account can reach, with its role in each, most
    recently active first, optionally narrowed by kind, enrollment,
    service, name prefix (``q``) or unseen activity (``new_activity``).
    Paging is opt-in: with ``limit``, a page at a time via the opaque
    ``cursor``; without it, every room. A key limited by ``room=`` sees
    only its rooms.

    Args:
        kind (None | str | Unset): Only rooms of this kind
        enrollment (None | Unset | UUID): Only rooms of this enrollment
        service (None | Unset | UUID): Only rooms of this service (not its enrollments' rooms)
        q (None | str | Unset): Only rooms whose name starts with this (case-insensitive)
        new_activity (bool | Unset): Only rooms with conversation activity the account hasn't seen
            Default: False.
        limit (int | None | Unset): Rooms per page; omit for every room (after ``cursor``)
        cursor (None | str | Unset): Opaque cursor from a previous response's next_cursor; omit to
            start from the first page
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomList
    """

    return (
        await asyncio_detailed(
            client=client,
            kind=kind,
            enrollment=enrollment,
            service=service,
            q=q,
            new_activity=new_activity,
            limit=limit,
            cursor=cursor,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
