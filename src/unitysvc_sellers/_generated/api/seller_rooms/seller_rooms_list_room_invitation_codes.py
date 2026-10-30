from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.room_invitation_codes import RoomInvitationCodes
from ...types import UNSET, Response, Unset


def _get_kwargs(
    target: str,
    *,
    include_inactive: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    params["include_inactive"] = include_inactive

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/rooms/{target}/codes".format(
            target=quote(str(target), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RoomInvitationCodes | None:
    if response.status_code == 200:
        response_200 = RoomInvitationCodes.from_dict(response.json())

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
) -> Response[HTTPValidationError | RoomInvitationCodes]:
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
    include_inactive: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomInvitationCodes]:
    """List Room Invitation Codes

     The room's invitation codes; by default only usable ones. Needs
    ``write``, since a code admits whoever holds it.

    Args:
        target (str):
        include_inactive (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomInvitationCodes]
    """

    kwargs = _get_kwargs(
        target=target,
        include_inactive=include_inactive,
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
    include_inactive: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomInvitationCodes | None:
    """List Room Invitation Codes

     The room's invitation codes; by default only usable ones. Needs
    ``write``, since a code admits whoever holds it.

    Args:
        target (str):
        include_inactive (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomInvitationCodes
    """

    return sync_detailed(
        target=target,
        client=client,
        include_inactive=include_inactive,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    target: str,
    *,
    client: AuthenticatedClient | Client,
    include_inactive: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomInvitationCodes]:
    """List Room Invitation Codes

     The room's invitation codes; by default only usable ones. Needs
    ``write``, since a code admits whoever holds it.

    Args:
        target (str):
        include_inactive (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomInvitationCodes]
    """

    kwargs = _get_kwargs(
        target=target,
        include_inactive=include_inactive,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    target: str,
    *,
    client: AuthenticatedClient | Client,
    include_inactive: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomInvitationCodes | None:
    """List Room Invitation Codes

     The room's invitation codes; by default only usable ones. Needs
    ``write``, since a code admits whoever holds it.

    Args:
        target (str):
        include_inactive (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomInvitationCodes
    """

    return (
        await asyncio_detailed(
            target=target,
            client=client,
            include_inactive=include_inactive,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
