from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.live_accepting import LiveAccepting
from ...models.live_lease import LiveLease
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: LiveAccepting,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/rooms/live/accepting",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | LiveLease | None:
    if response.status_code == 200:
        response_200 = LiveLease.from_dict(response.json())

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
) -> Response[HTTPValidationError | LiveLease]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: LiveAccepting,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | LiveLease]:
    """Accept Live Requests

     Accept live requests for this account, from this client, until
    the lease lapses or is stopped (#2926); ``mode=draining`` finishes the
    queue instead, taking no new requests. Only an explicit call (or a
    CLI long-poll loop started with ``--mark-accepting-requests``)
    accepts; reading and posting never do.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (LiveAccepting):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | LiveLease]
    """

    kwargs = _get_kwargs(
        body=body,
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
    body: LiveAccepting,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | LiveLease | None:
    """Accept Live Requests

     Accept live requests for this account, from this client, until
    the lease lapses or is stopped (#2926); ``mode=draining`` finishes the
    queue instead, taking no new requests. Only an explicit call (or a
    CLI long-poll loop started with ``--mark-accepting-requests``)
    accepts; reading and posting never do.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (LiveAccepting):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | LiveLease
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: LiveAccepting,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | LiveLease]:
    """Accept Live Requests

     Accept live requests for this account, from this client, until
    the lease lapses or is stopped (#2926); ``mode=draining`` finishes the
    queue instead, taking no new requests. Only an explicit call (or a
    CLI long-poll loop started with ``--mark-accepting-requests``)
    accepts; reading and posting never do.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (LiveAccepting):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | LiveLease]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: LiveAccepting,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | LiveLease | None:
    """Accept Live Requests

     Accept live requests for this account, from this client, until
    the lease lapses or is stopped (#2926); ``mode=draining`` finishes the
    queue instead, taking no new requests. Only an explicit call (or a
    CLI long-poll loop started with ``--mark-accepting-requests``)
    accepts; reading and posting never do.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (LiveAccepting):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | LiveLease
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
