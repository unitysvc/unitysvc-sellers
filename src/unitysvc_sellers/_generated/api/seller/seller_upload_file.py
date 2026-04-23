from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_seller_upload_file import BodySellerUploadFile
from ...models.file_upload_response import FileUploadResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BodySellerUploadFile,
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
        "url": "/upload",
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> FileUploadResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = FileUploadResponse.from_dict(response.json())

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
) -> Response[FileUploadResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: BodySellerUploadFile,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[FileUploadResponse | HTTPValidationError]:
    """Upload File

     Upload a file to content-addressed storage.

    Accepts multipart/form-data and stores the file in S3 under a SHA-256-based
    object_key. Returns the object_key for use in service listing documents,
    markdown image references, or any other resource that references stored files.

    Deduplicates automatically: if the same content was already uploaded, the S3
    write is skipped and ``uploaded`` will be False.

    Args:
        file: The file to upload.
        is_public: Whether the object should be publicly readable (default: True).

    Authentication: Requires API key with seller context.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (BodySellerUploadFile):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FileUploadResponse | HTTPValidationError]
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
    body: BodySellerUploadFile,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> FileUploadResponse | HTTPValidationError | None:
    """Upload File

     Upload a file to content-addressed storage.

    Accepts multipart/form-data and stores the file in S3 under a SHA-256-based
    object_key. Returns the object_key for use in service listing documents,
    markdown image references, or any other resource that references stored files.

    Deduplicates automatically: if the same content was already uploaded, the S3
    write is skipped and ``uploaded`` will be False.

    Args:
        file: The file to upload.
        is_public: Whether the object should be publicly readable (default: True).

    Authentication: Requires API key with seller context.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (BodySellerUploadFile):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FileUploadResponse | HTTPValidationError
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
    body: BodySellerUploadFile,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[FileUploadResponse | HTTPValidationError]:
    """Upload File

     Upload a file to content-addressed storage.

    Accepts multipart/form-data and stores the file in S3 under a SHA-256-based
    object_key. Returns the object_key for use in service listing documents,
    markdown image references, or any other resource that references stored files.

    Deduplicates automatically: if the same content was already uploaded, the S3
    write is skipped and ``uploaded`` will be False.

    Args:
        file: The file to upload.
        is_public: Whether the object should be publicly readable (default: True).

    Authentication: Requires API key with seller context.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (BodySellerUploadFile):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FileUploadResponse | HTTPValidationError]
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
    body: BodySellerUploadFile,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> FileUploadResponse | HTTPValidationError | None:
    """Upload File

     Upload a file to content-addressed storage.

    Accepts multipart/form-data and stores the file in S3 under a SHA-256-based
    object_key. Returns the object_key for use in service listing documents,
    markdown image references, or any other resource that references stored files.

    Deduplicates automatically: if the same content was already uploaded, the S3
    write is skipped and ``uploaded`` will be False.

    Args:
        file: The file to upload.
        is_public: Whether the object should be publicly readable (default: True).

    Authentication: Requires API key with seller context.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (BodySellerUploadFile):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FileUploadResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
