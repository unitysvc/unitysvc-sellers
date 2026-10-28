from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.webhook_event_status import WebhookEventStatus, check_webhook_event_status
from ...models.webhook_events_public import WebhookEventsPublic
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    type_: None | str | Unset = UNSET,
    status: None | Unset | WebhookEventStatus = UNSET,
    skip: int | Unset = 0,
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

    json_type_: None | str | Unset
    if isinstance(type_, Unset):
        json_type_ = UNSET
    else:
        json_type_ = type_
    params["type"] = json_type_

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, str):
        json_status = status
    else:
        json_status = status
    params["status"] = json_status

    params["skip"] = skip

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/webhook-events",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | WebhookEventsPublic | None:
    if response.status_code == 200:
        response_200 = WebhookEventsPublic.from_dict(response.json())

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
) -> Response[HTTPValidationError | WebhookEventsPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    type_: None | str | Unset = UNSET,
    status: None | Unset | WebhookEventStatus = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | WebhookEventsPublic]:
    """List Webhook Events

     The current seller's events from the last 30 days, newest first.

    After an outage, list ``status=failed`` or ``status=expired`` and resend.

    Args:
        type_ (None | str | Unset):
        status (None | Unset | WebhookEventStatus):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | WebhookEventsPublic]
    """

    kwargs = _get_kwargs(
        type_=type_,
        status=status,
        skip=skip,
        limit=limit,
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
    type_: None | str | Unset = UNSET,
    status: None | Unset | WebhookEventStatus = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | WebhookEventsPublic | None:
    """List Webhook Events

     The current seller's events from the last 30 days, newest first.

    After an outage, list ``status=failed`` or ``status=expired`` and resend.

    Args:
        type_ (None | str | Unset):
        status (None | Unset | WebhookEventStatus):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | WebhookEventsPublic
    """

    return sync_detailed(
        client=client,
        type_=type_,
        status=status,
        skip=skip,
        limit=limit,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    type_: None | str | Unset = UNSET,
    status: None | Unset | WebhookEventStatus = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | WebhookEventsPublic]:
    """List Webhook Events

     The current seller's events from the last 30 days, newest first.

    After an outage, list ``status=failed`` or ``status=expired`` and resend.

    Args:
        type_ (None | str | Unset):
        status (None | Unset | WebhookEventStatus):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | WebhookEventsPublic]
    """

    kwargs = _get_kwargs(
        type_=type_,
        status=status,
        skip=skip,
        limit=limit,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    type_: None | str | Unset = UNSET,
    status: None | Unset | WebhookEventStatus = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | WebhookEventsPublic | None:
    """List Webhook Events

     The current seller's events from the last 30 days, newest first.

    After an outage, list ``status=failed`` or ``status=expired`` and resend.

    Args:
        type_ (None | str | Unset):
        status (None | Unset | WebhookEventStatus):
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | WebhookEventsPublic
    """

    return (
        await asyncio_detailed(
            client=client,
            type_=type_,
            status=status,
            skip=skip,
            limit=limit,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
