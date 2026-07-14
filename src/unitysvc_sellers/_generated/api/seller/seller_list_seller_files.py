from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.seller_files_list_response import SellerFilesListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    path: str | Unset = "",
    max_keys: int | Unset = 100,
    continuation_token: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    params["path"] = path

    params["max_keys"] = max_keys

    json_continuation_token: None | str | Unset
    if isinstance(continuation_token, Unset):
        json_continuation_token = UNSET
    else:
        json_continuation_token = continuation_token
    params["continuation_token"] = json_continuation_token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/files/list",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SellerFilesListResponse | None:
    if response.status_code == 200:
        response_200 = SellerFilesListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | SellerFilesListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    path: str | Unset = "",
    max_keys: int | Unset = 100,
    continuation_token: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SellerFilesListResponse]:
    """List Seller Files

     List the seller's account files (one folder level per call).

    Returned keys and prefixes are relative to the seller root. A missing
    bucket reads as an empty listing (the bucket is provisioned out of
    band).

    Args:
        path (str | Unset): Folder path relative to the seller root Default: ''.
        max_keys (int | Unset):  Default: 100.
        continuation_token (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SellerFilesListResponse]
    """

    kwargs = _get_kwargs(
        path=path,
        max_keys=max_keys,
        continuation_token=continuation_token,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    path: str | Unset = "",
    max_keys: int | Unset = 100,
    continuation_token: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SellerFilesListResponse | None:
    """List Seller Files

     List the seller's account files (one folder level per call).

    Returned keys and prefixes are relative to the seller root. A missing
    bucket reads as an empty listing (the bucket is provisioned out of
    band).

    Args:
        path (str | Unset): Folder path relative to the seller root Default: ''.
        max_keys (int | Unset):  Default: 100.
        continuation_token (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SellerFilesListResponse
    """

    return sync_detailed(
        client=client,
        path=path,
        max_keys=max_keys,
        continuation_token=continuation_token,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    path: str | Unset = "",
    max_keys: int | Unset = 100,
    continuation_token: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SellerFilesListResponse]:
    """List Seller Files

     List the seller's account files (one folder level per call).

    Returned keys and prefixes are relative to the seller root. A missing
    bucket reads as an empty listing (the bucket is provisioned out of
    band).

    Args:
        path (str | Unset): Folder path relative to the seller root Default: ''.
        max_keys (int | Unset):  Default: 100.
        continuation_token (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SellerFilesListResponse]
    """

    kwargs = _get_kwargs(
        path=path,
        max_keys=max_keys,
        continuation_token=continuation_token,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    path: str | Unset = "",
    max_keys: int | Unset = 100,
    continuation_token: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SellerFilesListResponse | None:
    """List Seller Files

     List the seller's account files (one folder level per call).

    Returned keys and prefixes are relative to the seller root. A missing
    bucket reads as an empty listing (the bucket is provisioned out of
    band).

    Args:
        path (str | Unset): Folder path relative to the seller root Default: ''.
        max_keys (int | Unset):  Default: 100.
        continuation_token (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SellerFilesListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            path=path,
            max_keys=max_keys,
            continuation_token=continuation_token,
            x_role_id=x_role_id,
        )
    ).parsed
