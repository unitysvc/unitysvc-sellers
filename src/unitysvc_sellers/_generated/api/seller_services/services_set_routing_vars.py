from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.routing_vars_update import RoutingVarsUpdate
from ...models.routing_vars_update_response import RoutingVarsUpdateResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    service_id: str,
    *,
    body: RoutingVarsUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/services/{service_id}/routing-vars".format(service_id=quote(str(service_id), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorResponse | HTTPValidationError | RoutingVarsUpdateResponse | None:
    if response.status_code == 200:
        response_200 = RoutingVarsUpdateResponse.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorResponse | HTTPValidationError | RoutingVarsUpdateResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RoutingVarsUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | RoutingVarsUpdateResponse]:
    r""" Update Routing Vars

     Update routing_vars on an active service without approval.

    The template is the security boundary — sellers can only change values
    within the boundaries the admin-approved template defines.

    Supports:
    - set: dict of key-value pairs to add/update
    - remove: list of keys to remove (supports dot-paths for nested keys, e.g. \"users.alice\")

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoutingVarsUpdate): Request body for updating routing_vars on an active service.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | RoutingVarsUpdateResponse]
     """


    kwargs = _get_kwargs(
        service_id=service_id,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RoutingVarsUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | RoutingVarsUpdateResponse | None:
    r""" Update Routing Vars

     Update routing_vars on an active service without approval.

    The template is the security boundary — sellers can only change values
    within the boundaries the admin-approved template defines.

    Supports:
    - set: dict of key-value pairs to add/update
    - remove: list of keys to remove (supports dot-paths for nested keys, e.g. \"users.alice\")

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoutingVarsUpdate): Request body for updating routing_vars on an active service.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | RoutingVarsUpdateResponse
     """


    return sync_detailed(
        service_id=service_id,
client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RoutingVarsUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | RoutingVarsUpdateResponse]:
    r""" Update Routing Vars

     Update routing_vars on an active service without approval.

    The template is the security boundary — sellers can only change values
    within the boundaries the admin-approved template defines.

    Supports:
    - set: dict of key-value pairs to add/update
    - remove: list of keys to remove (supports dot-paths for nested keys, e.g. \"users.alice\")

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoutingVarsUpdate): Request body for updating routing_vars on an active service.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | RoutingVarsUpdateResponse]
     """


    kwargs = _get_kwargs(
        service_id=service_id,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RoutingVarsUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | RoutingVarsUpdateResponse | None:
    r""" Update Routing Vars

     Update routing_vars on an active service without approval.

    The template is the security boundary — sellers can only change values
    within the boundaries the admin-approved template defines.

    Supports:
    - set: dict of key-value pairs to add/update
    - remove: list of keys to remove (supports dot-paths for nested keys, e.g. \"users.alice\")

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (RoutingVarsUpdate): Request body for updating routing_vars on an active service.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | RoutingVarsUpdateResponse
     """


    return (await asyncio_detailed(
        service_id=service_id,
client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
