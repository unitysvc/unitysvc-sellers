from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_file_upload_ticket import AccountFileUploadTicket
from ...models.http_validation_error import HTTPValidationError
from ...models.seller_file_upload_request import SellerFileUploadRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: SellerFileUploadRequest,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/files/upload",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountFileUploadTicket | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AccountFileUploadTicket.from_dict(response.json())

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
) -> Response[AccountFileUploadTicket | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: SellerFileUploadRequest,
    x_role_id: None | str | Unset = UNSET,
) -> Response[AccountFileUploadTicket | HTTPValidationError]:
    """Upload Seller File

     Mint a presigned-POST ticket for one direct-to-storage upload.

    Bytes never transit this API: POST the returned ``fields`` plus the
    file (last, field name ``file``) as multipart form data to ``url``.
    The key lands under the seller root at ``{path}{filename}`` (existing
    objects with the same key are overwritten, like a home directory);
    the size ceiling is enforced by the signed policy, not the declared
    ``size``.

    Args:
        x_role_id (None | str | Unset):
        body (SellerFileUploadRequest): Mint request for one direct-to-storage upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountFileUploadTicket | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: SellerFileUploadRequest,
    x_role_id: None | str | Unset = UNSET,
) -> AccountFileUploadTicket | HTTPValidationError | None:
    """Upload Seller File

     Mint a presigned-POST ticket for one direct-to-storage upload.

    Bytes never transit this API: POST the returned ``fields`` plus the
    file (last, field name ``file``) as multipart form data to ``url``.
    The key lands under the seller root at ``{path}{filename}`` (existing
    objects with the same key are overwritten, like a home directory);
    the size ceiling is enforced by the signed policy, not the declared
    ``size``.

    Args:
        x_role_id (None | str | Unset):
        body (SellerFileUploadRequest): Mint request for one direct-to-storage upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountFileUploadTicket | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: SellerFileUploadRequest,
    x_role_id: None | str | Unset = UNSET,
) -> Response[AccountFileUploadTicket | HTTPValidationError]:
    """Upload Seller File

     Mint a presigned-POST ticket for one direct-to-storage upload.

    Bytes never transit this API: POST the returned ``fields`` plus the
    file (last, field name ``file``) as multipart form data to ``url``.
    The key lands under the seller root at ``{path}{filename}`` (existing
    objects with the same key are overwritten, like a home directory);
    the size ceiling is enforced by the signed policy, not the declared
    ``size``.

    Args:
        x_role_id (None | str | Unset):
        body (SellerFileUploadRequest): Mint request for one direct-to-storage upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountFileUploadTicket | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: SellerFileUploadRequest,
    x_role_id: None | str | Unset = UNSET,
) -> AccountFileUploadTicket | HTTPValidationError | None:
    """Upload Seller File

     Mint a presigned-POST ticket for one direct-to-storage upload.

    Bytes never transit this API: POST the returned ``fields`` plus the
    file (last, field name ``file``) as multipart form data to ``url``.
    The key lands under the seller root at ``{path}{filename}`` (existing
    objects with the same key are overwritten, like a home directory);
    the size ceiling is enforced by the signed policy, not the declared
    ``size``.

    Args:
        x_role_id (None | str | Unset):
        body (SellerFileUploadRequest): Mint request for one direct-to-storage upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountFileUploadTicket | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            x_role_id=x_role_id,
        )
    ).parsed
