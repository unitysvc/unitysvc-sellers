from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.seller_instances_delete_instance_response_seller_instances_delete_instance import (
    SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    instance_id: str,
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
        "method": "delete",
        "url": "/instances/{instance_id}".format(
            instance_id=quote(str(instance_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance | None:
    if response.status_code == 200:
        response_200 = SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance.from_dict(response.json())

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
) -> Response[HTTPValidationError | SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    instance_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance]:
    """Delete Instance

     Delete a form. The linked service (if any) is not unpublished.

    Args:
        instance_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance]
    """

    kwargs = _get_kwargs(
        instance_id=instance_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    instance_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance | None:
    """Delete Instance

     Delete a form. The linked service (if any) is not unpublished.

    Args:
        instance_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance
    """

    return sync_detailed(
        instance_id=instance_id,
        client=client,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    instance_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance]:
    """Delete Instance

     Delete a form. The linked service (if any) is not unpublished.

    Args:
        instance_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance]
    """

    kwargs = _get_kwargs(
        instance_id=instance_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    instance_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance | None:
    """Delete Instance

     Delete a form. The linked service (if any) is not unpublished.

    Args:
        instance_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SellerInstancesDeleteInstanceResponseSellerInstancesDeleteInstance
    """

    return (
        await asyncio_detailed(
            instance_id=instance_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
