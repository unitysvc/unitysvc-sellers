from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.webhook_event_public import WebhookEventPublic
from ...types import UNSET, Response, Unset


def _get_kwargs(
    endpoint_id: UUID,
    *,
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
        "url": "/webhooks/{endpoint_id}/test".format(
            endpoint_id=quote(str(endpoint_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | WebhookEventPublic | None:
    if response.status_code == 202:
        response_202 = WebhookEventPublic.from_dict(response.json())

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
) -> Response[HTTPValidationError | WebhookEventPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    endpoint_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | WebhookEventPublic]:
    """Send Test Webhook

     Send a ``webhook_endpoint.test`` event to this endpoint only.

    Delivery is asynchronous; read the returned event to see how it went.

    Args:
        endpoint_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | WebhookEventPublic]
    """

    kwargs = _get_kwargs(
        endpoint_id=endpoint_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    endpoint_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | WebhookEventPublic | None:
    """Send Test Webhook

     Send a ``webhook_endpoint.test`` event to this endpoint only.

    Delivery is asynchronous; read the returned event to see how it went.

    Args:
        endpoint_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | WebhookEventPublic
    """

    return sync_detailed(
        endpoint_id=endpoint_id,
        client=client,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    endpoint_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | WebhookEventPublic]:
    """Send Test Webhook

     Send a ``webhook_endpoint.test`` event to this endpoint only.

    Delivery is asynchronous; read the returned event to see how it went.

    Args:
        endpoint_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | WebhookEventPublic]
    """

    kwargs = _get_kwargs(
        endpoint_id=endpoint_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    endpoint_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | WebhookEventPublic | None:
    """Send Test Webhook

     Send a ``webhook_endpoint.test`` event to this endpoint only.

    Delivery is asynchronous; read the returned event to see how it went.

    Args:
        endpoint_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | WebhookEventPublic
    """

    return (
        await asyncio_detailed(
            endpoint_id=endpoint_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
