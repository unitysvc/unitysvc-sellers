from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.seller_file_download_response import SellerFileDownloadResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    key: str,
    expires_in: int | Unset = 900,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    params["key"] = key

    params["expires_in"] = expires_in

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/files/download",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SellerFileDownloadResponse | None:
    if response.status_code == 200:
        response_200 = SellerFileDownloadResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | SellerFileDownloadResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    key: str,
    expires_in: int | Unset = 900,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SellerFileDownloadResponse]:
    """Download Seller File

     Generate a short-TTL presigned download URL for one seller file.

    The object must exist (404 otherwise) and always resolves under the
    seller's own root — ``key`` is relative, so other tenants' folders
    cannot be addressed.

    Args:
        key (str): Object key relative to the seller root
        expires_in (int | Unset):  Default: 900.
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SellerFileDownloadResponse]
    """

    kwargs = _get_kwargs(
        key=key,
        expires_in=expires_in,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    key: str,
    expires_in: int | Unset = 900,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SellerFileDownloadResponse | None:
    """Download Seller File

     Generate a short-TTL presigned download URL for one seller file.

    The object must exist (404 otherwise) and always resolves under the
    seller's own root — ``key`` is relative, so other tenants' folders
    cannot be addressed.

    Args:
        key (str): Object key relative to the seller root
        expires_in (int | Unset):  Default: 900.
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SellerFileDownloadResponse
    """

    return sync_detailed(
        client=client,
        key=key,
        expires_in=expires_in,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    key: str,
    expires_in: int | Unset = 900,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SellerFileDownloadResponse]:
    """Download Seller File

     Generate a short-TTL presigned download URL for one seller file.

    The object must exist (404 otherwise) and always resolves under the
    seller's own root — ``key`` is relative, so other tenants' folders
    cannot be addressed.

    Args:
        key (str): Object key relative to the seller root
        expires_in (int | Unset):  Default: 900.
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SellerFileDownloadResponse]
    """

    kwargs = _get_kwargs(
        key=key,
        expires_in=expires_in,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    key: str,
    expires_in: int | Unset = 900,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SellerFileDownloadResponse | None:
    """Download Seller File

     Generate a short-TTL presigned download URL for one seller file.

    The object must exist (404 otherwise) and always resolves under the
    seller's own root — ``key`` is relative, so other tenants' folders
    cannot be addressed.

    Args:
        key (str): Object key relative to the seller root
        expires_in (int | Unset):  Default: 900.
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SellerFileDownloadResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            key=key,
            expires_in=expires_in,
            x_role_id=x_role_id,
        )
    ).parsed
