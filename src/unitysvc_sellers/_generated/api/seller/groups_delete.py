from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    group_id: UUID,
    *,
    x_role_id: None | str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/seller/service-groups/{group_id}".format(group_id=quote(str(group_id), safe=""),),
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ErrorResponse | HTTPValidationError | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ErrorResponse | HTTPValidationError]:
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
    x_role_id: None | str | Unset = UNSET,

) -> Response[Any | ErrorResponse | HTTPValidationError]:
    """ Delete Seller Group

     Delete a service group (draft/private only, must have no services).

    Args:
        group_id (UUID):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse | HTTPValidationError]
     """


    kwargs = _get_kwargs(
        group_id=group_id,
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
    x_role_id: None | str | Unset = UNSET,

) -> Any | ErrorResponse | HTTPValidationError | None:
    """ Delete Seller Group

     Delete a service group (draft/private only, must have no services).

    Args:
        group_id (UUID):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse | HTTPValidationError
     """


    return sync_detailed(
        group_id=group_id,
client=client,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    group_id: UUID,
    *,
    client: AuthenticatedClient,
    x_role_id: None | str | Unset = UNSET,

) -> Response[Any | ErrorResponse | HTTPValidationError]:
    """ Delete Seller Group

     Delete a service group (draft/private only, must have no services).

    Args:
        group_id (UUID):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse | HTTPValidationError]
     """


    kwargs = _get_kwargs(
        group_id=group_id,
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
    x_role_id: None | str | Unset = UNSET,

) -> Any | ErrorResponse | HTTPValidationError | None:
    """ Delete Seller Group

     Delete a service group (draft/private only, must have no services).

    Args:
        group_id (UUID):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse | HTTPValidationError
     """


    return (await asyncio_detailed(
        group_id=group_id,
client=client,
x_role_id=x_role_id,

    )).parsed
