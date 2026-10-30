from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.webhook_endpoint_with_secret import WebhookEndpointWithSecret
from ...models.webhook_roll_secret import WebhookRollSecret
from ...types import UNSET, Response, Unset


def _get_kwargs(
    endpoint_id: UUID,
    *,
    body: WebhookRollSecret,
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
        "url": "/webhooks/{endpoint_id}/roll-secret".format(
            endpoint_id=quote(str(endpoint_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | WebhookEndpointWithSecret | None:
    if response.status_code == 200:
        response_200 = WebhookEndpointWithSecret.from_dict(response.json())

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
) -> Response[HTTPValidationError | WebhookEndpointWithSecret]:
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
    body: WebhookRollSecret,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | WebhookEndpointWithSecret]:
    """Roll Webhook Secret

     Replace the signing secret. The response carries the new one, shown once.

    For ``expires_in_hours`` (at most 24) deliveries carry a second ``v1``
    signature made with the old secret, so receivers can switch without
    rejecting anything. ``0`` retires the old secret at once.

    Args:
        endpoint_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (WebhookRollSecret):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | WebhookEndpointWithSecret]
    """

    kwargs = _get_kwargs(
        endpoint_id=endpoint_id,
        body=body,
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
    body: WebhookRollSecret,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | WebhookEndpointWithSecret | None:
    """Roll Webhook Secret

     Replace the signing secret. The response carries the new one, shown once.

    For ``expires_in_hours`` (at most 24) deliveries carry a second ``v1``
    signature made with the old secret, so receivers can switch without
    rejecting anything. ``0`` retires the old secret at once.

    Args:
        endpoint_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (WebhookRollSecret):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | WebhookEndpointWithSecret
    """

    return sync_detailed(
        endpoint_id=endpoint_id,
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    endpoint_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: WebhookRollSecret,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | WebhookEndpointWithSecret]:
    """Roll Webhook Secret

     Replace the signing secret. The response carries the new one, shown once.

    For ``expires_in_hours`` (at most 24) deliveries carry a second ``v1``
    signature made with the old secret, so receivers can switch without
    rejecting anything. ``0`` retires the old secret at once.

    Args:
        endpoint_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (WebhookRollSecret):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | WebhookEndpointWithSecret]
    """

    kwargs = _get_kwargs(
        endpoint_id=endpoint_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    endpoint_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: WebhookRollSecret,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | WebhookEndpointWithSecret | None:
    """Roll Webhook Secret

     Replace the signing secret. The response carries the new one, shown once.

    For ``expires_in_hours`` (at most 24) deliveries carry a second ``v1``
    signature made with the old secret, so receivers can switch without
    rejecting anything. ``0`` retires the old secret at once.

    Args:
        endpoint_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (WebhookRollSecret):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | WebhookEndpointWithSecret
    """

    return (
        await asyncio_detailed(
            endpoint_id=endpoint_id,
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
