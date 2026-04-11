from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.service_group_public import ServiceGroupPublic
from ...models.service_group_update import ServiceGroupUpdate
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    group_id: UUID,
    *,
    body: ServiceGroupUpdate,
    x_role_id: None | str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/service-groups/{group_id}".format(group_id=quote(str(group_id), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorResponse | HTTPValidationError | ServiceGroupPublic | None:
    if response.status_code == 200:
        response_200 = ServiceGroupPublic.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorResponse | HTTPValidationError | ServiceGroupPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    group_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ServiceGroupUpdate,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | ServiceGroupPublic]:
    """ Update Seller Group

     Update a service group.

    Args:
        group_id (UUID):
        x_role_id (None | str | Unset):
        body (ServiceGroupUpdate): Schema for updating a ServiceGroup.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceGroupPublic]
     """


    kwargs = _get_kwargs(
        group_id=group_id,
body=body,
x_role_id=x_role_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    group_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ServiceGroupUpdate,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | ServiceGroupPublic | None:
    """ Update Seller Group

     Update a service group.

    Args:
        group_id (UUID):
        x_role_id (None | str | Unset):
        body (ServiceGroupUpdate): Schema for updating a ServiceGroup.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceGroupPublic
     """


    return sync_detailed(
        group_id=group_id,
client=client,
body=body,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    group_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ServiceGroupUpdate,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | ServiceGroupPublic]:
    """ Update Seller Group

     Update a service group.

    Args:
        group_id (UUID):
        x_role_id (None | str | Unset):
        body (ServiceGroupUpdate): Schema for updating a ServiceGroup.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceGroupPublic]
     """


    kwargs = _get_kwargs(
        group_id=group_id,
body=body,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    group_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ServiceGroupUpdate,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | ServiceGroupPublic | None:
    """ Update Seller Group

     Update a service group.

    Args:
        group_id (UUID):
        x_role_id (None | str | Unset):
        body (ServiceGroupUpdate): Schema for updating a ServiceGroup.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceGroupPublic
     """


    return (await asyncio_detailed(
        group_id=group_id,
client=client,
body=body,
x_role_id=x_role_id,

    )).parsed
