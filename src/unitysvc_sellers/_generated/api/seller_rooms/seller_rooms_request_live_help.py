from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.live_request_lease import LiveRequestLease
from ...models.live_request_start import LiveRequestStart
from ...types import UNSET, Response, Unset


def _get_kwargs(
    target: str,
    *,
    body: LiveRequestStart,
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
        "url": "/rooms/{target}/live/request".format(
            target=quote(str(target), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | LiveRequestLease | None:
    if response.status_code == 200:
        response_200 = LiveRequestLease.from_dict(response.json())

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
) -> Response[HTTPValidationError | LiveRequestLease]:
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
    body: LiveRequestStart,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | LiveRequestLease]:
    """Request Live Help

     Ask another member of the room for live help, or renew that ask
    (#2926). The request lives while any of its requesters keeps renewing;
    it may start while nobody is accepting (``available`` says so), but
    not while the party is only finishing its queue (``draining``: 409),
    though joining a request already waiting still works. 409 when
    ``generation`` was resolved: ask again without it.

    Args:
        target (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (LiveRequestStart):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | LiveRequestLease]
    """

    kwargs = _get_kwargs(
        target=target,
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
    *,
    client: AuthenticatedClient | Client,
    body: LiveRequestStart,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | LiveRequestLease | None:
    """Request Live Help

     Ask another member of the room for live help, or renew that ask
    (#2926). The request lives while any of its requesters keeps renewing;
    it may start while nobody is accepting (``available`` says so), but
    not while the party is only finishing its queue (``draining``: 409),
    though joining a request already waiting still works. 409 when
    ``generation`` was resolved: ask again without it.

    Args:
        target (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (LiveRequestStart):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | LiveRequestLease
    """

    return sync_detailed(
        target=target,
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    target: str,
    *,
    client: AuthenticatedClient | Client,
    body: LiveRequestStart,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | LiveRequestLease]:
    """Request Live Help

     Ask another member of the room for live help, or renew that ask
    (#2926). The request lives while any of its requesters keeps renewing;
    it may start while nobody is accepting (``available`` says so), but
    not while the party is only finishing its queue (``draining``: 409),
    though joining a request already waiting still works. 409 when
    ``generation`` was resolved: ask again without it.

    Args:
        target (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (LiveRequestStart):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | LiveRequestLease]
    """

    kwargs = _get_kwargs(
        target=target,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    target: str,
    *,
    client: AuthenticatedClient | Client,
    body: LiveRequestStart,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | LiveRequestLease | None:
    """Request Live Help

     Ask another member of the room for live help, or renew that ask
    (#2926). The request lives while any of its requesters keeps renewing;
    it may start while nobody is accepting (``available`` says so), but
    not while the party is only finishing its queue (``draining``: 409),
    though joining a request already waiting still works. 409 when
    ``generation`` was resolved: ask again without it.

    Args:
        target (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (LiveRequestStart):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | LiveRequestLease
    """

    return (
        await asyncio_detailed(
            target=target,
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
