from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deprecated_service_item import DeprecatedServiceItem
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
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
        "method": "get",
        "url": "/services/deprecated",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | list[DeprecatedServiceItem] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = DeprecatedServiceItem.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | HTTPValidationError | list[DeprecatedServiceItem]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | list[DeprecatedServiceItem]]:
    """List Deprecated Services

     List services owned by the current seller that are deprecated.

    Deprecated services are excluded from ``GET /seller/services`` and
    from every other browse surface (see #1027). This endpoint exists
    only to support the recovery workflow: a seller can find a
    deprecated service id and email it to platform support, who has
    admin access to flip ``deprecated → active``.

    The response is read-only and intentionally minimal — id, names,
    provider, and a deprecation timestamp. No filtering or pagination:
    a seller's deprecated set is small in practice.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | list[DeprecatedServiceItem]]
    """

    kwargs = _get_kwargs(
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
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | list[DeprecatedServiceItem] | None:
    """List Deprecated Services

     List services owned by the current seller that are deprecated.

    Deprecated services are excluded from ``GET /seller/services`` and
    from every other browse surface (see #1027). This endpoint exists
    only to support the recovery workflow: a seller can find a
    deprecated service id and email it to platform support, who has
    admin access to flip ``deprecated → active``.

    The response is read-only and intentionally minimal — id, names,
    provider, and a deprecation timestamp. No filtering or pagination:
    a seller's deprecated set is small in practice.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | list[DeprecatedServiceItem]
    """

    return sync_detailed(
        client=client,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | list[DeprecatedServiceItem]]:
    """List Deprecated Services

     List services owned by the current seller that are deprecated.

    Deprecated services are excluded from ``GET /seller/services`` and
    from every other browse surface (see #1027). This endpoint exists
    only to support the recovery workflow: a seller can find a
    deprecated service id and email it to platform support, who has
    admin access to flip ``deprecated → active``.

    The response is read-only and intentionally minimal — id, names,
    provider, and a deprecation timestamp. No filtering or pagination:
    a seller's deprecated set is small in practice.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | list[DeprecatedServiceItem]]
    """

    kwargs = _get_kwargs(
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | list[DeprecatedServiceItem] | None:
    """List Deprecated Services

     List services owned by the current seller that are deprecated.

    Deprecated services are excluded from ``GET /seller/services`` and
    from every other browse surface (see #1027). This endpoint exists
    only to support the recovery workflow: a seller can find a
    deprecated service id and email it to platform support, who has
    admin access to flip ``deprecated → active``.

    The response is read-only and intentionally minimal — id, names,
    provider, and a deprecation timestamp. No filtering or pagination:
    a seller's deprecated set is small in practice.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | list[DeprecatedServiceItem]
    """

    return (
        await asyncio_detailed(
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
