from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.room_invitation_code import RoomInvitationCode
from ...types import UNSET, Response, Unset


def _get_kwargs(
    target: str,
    code_id: UUID,
    *,
    email: str,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    params["email"] = email

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/rooms/{target}/codes/{code_id}/invitations".format(
            target=quote(str(target), safe=""),
            code_id=quote(str(code_id), safe=""),
        ),
        "params": params,
    }

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
    email: str,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomInvitationCode]:
    """Remove Room Email Invitation

     Stop showing an emailed invitation as pending. The link it carried
    works until the code is rotated or revoked.

    Args:
        target (str):
        code_id (UUID):
        email (str): The pending address to remove
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomInvitationCode]
    """

    kwargs = _get_kwargs(
        target=target,
        code_id=code_id,
        email=email,
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
    email: str,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomInvitationCode | None:
    """Remove Room Email Invitation

     Stop showing an emailed invitation as pending. The link it carried
    works until the code is rotated or revoked.

    Args:
        target (str):
        code_id (UUID):
        email (str): The pending address to remove
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

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
        email=email,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    target: str,
    code_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    email: str,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | RoomInvitationCode]:
    """Remove Room Email Invitation

     Stop showing an emailed invitation as pending. The link it carried
    works until the code is rotated or revoked.

    Args:
        target (str):
        code_id (UUID):
        email (str): The pending address to remove
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RoomInvitationCode]
    """

    kwargs = _get_kwargs(
        target=target,
        code_id=code_id,
        email=email,
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
    email: str,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | RoomInvitationCode | None:
    """Remove Room Email Invitation

     Stop showing an emailed invitation as pending. The link it carried
    works until the code is rotated or revoked.

    Args:
        target (str):
        code_id (UUID):
        email (str): The pending address to remove
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

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
            email=email,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
