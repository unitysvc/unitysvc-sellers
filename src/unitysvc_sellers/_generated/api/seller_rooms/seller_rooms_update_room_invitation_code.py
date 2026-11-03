from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.room_invitation_code import RoomInvitationCode
from ...models.room_invitation_update import RoomInvitationUpdate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    target: str,
    code_id: UUID,
    *,
    body: RoomInvitationUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/rooms/{target}/codes/{code_id}".format(
            target=quote(str(target), safe=""),
            code_id=quote(str(code_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RoomInvitationCode | None:
    if response.status_code == 200:
        response_200 = RoomInvitationCode.from_dict(response.json())

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
) -> Response[HTTPValidationError | RoomInvitationCode]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    target: str,
    code_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RoomInvitationUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomInvitationCode]:
    """Update Room Invitation Code

     Change a code in place, so its link keeps working: reset its expiry
    from now, its use limit, or the role it grants.

    Args:
        target (str):
        code_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoomInvitationUpdate): Change a code in place; its link keeps working.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomInvitationCode]
    """

    kwargs = _get_kwargs(
        target=target,
        code_id=code_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    target: str,
    code_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RoomInvitationUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomInvitationCode | None:
    """Update Room Invitation Code

     Change a code in place, so its link keeps working: reset its expiry
    from now, its use limit, or the role it grants.

    Args:
        target (str):
        code_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoomInvitationUpdate): Change a code in place; its link keeps working.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomInvitationCode
    """

    return sync_detailed(
        target=target,
        code_id=code_id,
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    target: str,
    code_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RoomInvitationUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomInvitationCode]:
    """Update Room Invitation Code

     Change a code in place, so its link keeps working: reset its expiry
    from now, its use limit, or the role it grants.

    Args:
        target (str):
        code_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoomInvitationUpdate): Change a code in place; its link keeps working.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomInvitationCode]
    """

    kwargs = _get_kwargs(
        target=target,
        code_id=code_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    target: str,
    code_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: RoomInvitationUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomInvitationCode | None:
    """Update Room Invitation Code

     Change a code in place, so its link keeps working: reset its expiry
    from now, its use limit, or the role it grants.

    Args:
        target (str):
        code_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoomInvitationUpdate): Change a code in place; its link keeps working.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RoomInvitationCode
    """

    return (
        await asyncio_detailed(
            target=target,
            code_id=code_id,
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
