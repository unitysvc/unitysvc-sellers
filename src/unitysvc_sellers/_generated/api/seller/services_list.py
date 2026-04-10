from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.services_public import ServicesPublic
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    status: None | str | Unset = UNSET,
    service_type: None | str | Unset = UNSET,
    listing_type: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    params: dict[str, Any] = {}

    params["skip"] = skip

    params["limit"] = limit

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    json_service_type: None | str | Unset
    if isinstance(service_type, Unset):
        json_service_type = UNSET
    else:
        json_service_type = service_type
    params["service_type"] = json_service_type

    json_listing_type: None | str | Unset
    if isinstance(listing_type, Unset):
        json_listing_type = UNSET
    else:
        json_listing_type = listing_type
    params["listing_type"] = json_listing_type

    json_name: None | str | Unset
    if isinstance(name, Unset):
        json_name = UNSET
    else:
        json_name = name
    params["name"] = json_name


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/seller/services",
        "params": params,
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorResponse | HTTPValidationError | ServicesPublic | None:
    if response.status_code == 200:
        response_200 = ServicesPublic.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorResponse | HTTPValidationError | ServicesPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    status: None | str | Unset = UNSET,
    service_type: None | str | Unset = UNSET,
    listing_type: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | ServicesPublic]:
    """ List My Services

     List all services for the current seller.

    Services are the identity layer connecting sellers to content versions
    (Provider, ServiceOffering, ServiceListing).

    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - status: Filter by service status (draft, pending, review, active, rejected, suspended)
    - service_type: Filter by service type (e.g., llm, vectordb, embedding)
    - listing_type: Filter by listing type (regular, byok, self_hosted)
    - name: Search by name, display name, or provider name (case-insensitive partial match)

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        status (None | str | Unset):
        service_type (None | str | Unset): Filter by service type
        listing_type (None | str | Unset): Filter by listing type
        name (None | str | Unset): Search by name, display name, or provider name (case-
            insensitive partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServicesPublic]
     """


    kwargs = _get_kwargs(
        skip=skip,
limit=limit,
status=status,
service_type=service_type,
listing_type=listing_type,
name=name,
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
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    status: None | str | Unset = UNSET,
    service_type: None | str | Unset = UNSET,
    listing_type: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | ServicesPublic | None:
    """ List My Services

     List all services for the current seller.

    Services are the identity layer connecting sellers to content versions
    (Provider, ServiceOffering, ServiceListing).

    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - status: Filter by service status (draft, pending, review, active, rejected, suspended)
    - service_type: Filter by service type (e.g., llm, vectordb, embedding)
    - listing_type: Filter by listing type (regular, byok, self_hosted)
    - name: Search by name, display name, or provider name (case-insensitive partial match)

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        status (None | str | Unset):
        service_type (None | str | Unset): Filter by service type
        listing_type (None | str | Unset): Filter by listing type
        name (None | str | Unset): Search by name, display name, or provider name (case-
            insensitive partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServicesPublic
     """


    return sync_detailed(
        client=client,
skip=skip,
limit=limit,
status=status,
service_type=service_type,
listing_type=listing_type,
name=name,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    status: None | str | Unset = UNSET,
    service_type: None | str | Unset = UNSET,
    listing_type: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | ServicesPublic]:
    """ List My Services

     List all services for the current seller.

    Services are the identity layer connecting sellers to content versions
    (Provider, ServiceOffering, ServiceListing).

    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - status: Filter by service status (draft, pending, review, active, rejected, suspended)
    - service_type: Filter by service type (e.g., llm, vectordb, embedding)
    - listing_type: Filter by listing type (regular, byok, self_hosted)
    - name: Search by name, display name, or provider name (case-insensitive partial match)

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        status (None | str | Unset):
        service_type (None | str | Unset): Filter by service type
        listing_type (None | str | Unset): Filter by listing type
        name (None | str | Unset): Search by name, display name, or provider name (case-
            insensitive partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServicesPublic]
     """


    kwargs = _get_kwargs(
        skip=skip,
limit=limit,
status=status,
service_type=service_type,
listing_type=listing_type,
name=name,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    status: None | str | Unset = UNSET,
    service_type: None | str | Unset = UNSET,
    listing_type: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | ServicesPublic | None:
    """ List My Services

     List all services for the current seller.

    Services are the identity layer connecting sellers to content versions
    (Provider, ServiceOffering, ServiceListing).

    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - status: Filter by service status (draft, pending, review, active, rejected, suspended)
    - service_type: Filter by service type (e.g., llm, vectordb, embedding)
    - listing_type: Filter by listing type (regular, byok, self_hosted)
    - name: Search by name, display name, or provider name (case-insensitive partial match)

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        status (None | str | Unset):
        service_type (None | str | Unset): Filter by service type
        listing_type (None | str | Unset): Filter by listing type
        name (None | str | Unset): Search by name, display name, or provider name (case-
            insensitive partial match)
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServicesPublic
     """


    return (await asyncio_detailed(
        client=client,
skip=skip,
limit=limit,
status=status,
service_type=service_type,
listing_type=listing_type,
name=name,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
