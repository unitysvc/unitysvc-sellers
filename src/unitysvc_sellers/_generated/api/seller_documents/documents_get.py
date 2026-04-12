from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.document_detail_response import DocumentDetailResponse
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union



def _get_kwargs(
    document_id: str,
    *,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/documents/{document_id}".format(document_id=document_id,),
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[DocumentDetailResponse, ErrorResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = DocumentDetailResponse.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())



        return response_400

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())



        return response_403

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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[DocumentDetailResponse, ErrorResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    document_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[DocumentDetailResponse, ErrorResponse, HTTPValidationError]]:
    """ Get Document

     Get full document details including file content and test metadata.

    Returns the full document record for a document attached to a service
    owned by the current seller. File content is always included — callers
    decide whether to display it, save to disk, or ignore it.

    Supports partial document ID matching (minimum 8 characters).

    Args:
        document_id (str):
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DocumentDetailResponse, ErrorResponse, HTTPValidationError]]
     """


    kwargs = _get_kwargs(
        document_id=document_id,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    document_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[DocumentDetailResponse, ErrorResponse, HTTPValidationError]]:
    """ Get Document

     Get full document details including file content and test metadata.

    Returns the full document record for a document attached to a service
    owned by the current seller. File content is always included — callers
    decide whether to display it, save to disk, or ignore it.

    Supports partial document ID matching (minimum 8 characters).

    Args:
        document_id (str):
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DocumentDetailResponse, ErrorResponse, HTTPValidationError]
     """


    return sync_detailed(
        document_id=document_id,
client=client,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    document_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[DocumentDetailResponse, ErrorResponse, HTTPValidationError]]:
    """ Get Document

     Get full document details including file content and test metadata.

    Returns the full document record for a document attached to a service
    owned by the current seller. File content is always included — callers
    decide whether to display it, save to disk, or ignore it.

    Supports partial document ID matching (minimum 8 characters).

    Args:
        document_id (str):
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DocumentDetailResponse, ErrorResponse, HTTPValidationError]]
     """


    kwargs = _get_kwargs(
        document_id=document_id,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    document_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[DocumentDetailResponse, ErrorResponse, HTTPValidationError]]:
    """ Get Document

     Get full document details including file content and test metadata.

    Returns the full document record for a document attached to a service
    owned by the current seller. File content is always included — callers
    decide whether to display it, save to disk, or ignore it.

    Supports partial document ID matching (minimum 8 characters).

    Args:
        document_id (str):
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DocumentDetailResponse, ErrorResponse, HTTPValidationError]
     """


    return (await asyncio_detailed(
        document_id=document_id,
client=client,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
