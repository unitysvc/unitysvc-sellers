from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.test_env_response import TestEnvResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    service_id: str,
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
        "method": "get",
        "url": "/v1/seller/services/{service_id}/test-env".format(service_id=quote(str(service_id), safe=""),),
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorResponse | HTTPValidationError | TestEnvResponse | None:
    if response.status_code == 200:
        response_200 = TestEnvResponse.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorResponse | HTTPValidationError | TestEnvResponse]:
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
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | TestEnvResponse]:
    """ Get Service Test Env

     Get rendered service_options.enrollment_vars for the ops_customer test enrollment.

    Returns the enrollment_vars key-value pairs with Jinja2 templates resolved
    (e.g. enrollment_code() expanded to the actual ActionCode token).
    Used by ``usvc services run-tests`` to inject env vars into test scripts.

    This endpoint is specifically for testing — it looks up the ops_customer
    enrollment for the service. Different enrollments may have different
    rendered values.

    Supports partial ID matching (minimum 8 characters).

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | TestEnvResponse]
     """


    kwargs = _get_kwargs(
        service_id=service_id,
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
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | TestEnvResponse | None:
    """ Get Service Test Env

     Get rendered service_options.enrollment_vars for the ops_customer test enrollment.

    Returns the enrollment_vars key-value pairs with Jinja2 templates resolved
    (e.g. enrollment_code() expanded to the actual ActionCode token).
    Used by ``usvc services run-tests`` to inject env vars into test scripts.

    This endpoint is specifically for testing — it looks up the ops_customer
    enrollment for the service. Different enrollments may have different
    rendered values.

    Supports partial ID matching (minimum 8 characters).

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | TestEnvResponse
     """


    return sync_detailed(
        service_id=service_id,
client=client,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | TestEnvResponse]:
    """ Get Service Test Env

     Get rendered service_options.enrollment_vars for the ops_customer test enrollment.

    Returns the enrollment_vars key-value pairs with Jinja2 templates resolved
    (e.g. enrollment_code() expanded to the actual ActionCode token).
    Used by ``usvc services run-tests`` to inject env vars into test scripts.

    This endpoint is specifically for testing — it looks up the ops_customer
    enrollment for the service. Different enrollments may have different
    rendered values.

    Supports partial ID matching (minimum 8 characters).

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | TestEnvResponse]
     """


    kwargs = _get_kwargs(
        service_id=service_id,
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
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | TestEnvResponse | None:
    """ Get Service Test Env

     Get rendered service_options.enrollment_vars for the ops_customer test enrollment.

    Returns the enrollment_vars key-value pairs with Jinja2 templates resolved
    (e.g. enrollment_code() expanded to the actual ActionCode token).
    Used by ``usvc services run-tests`` to inject env vars into test scripts.

    This endpoint is specifically for testing — it looks up the ops_customer
    enrollment for the service. Different enrollments may have different
    rendered values.

    Supports partial ID matching (minimum 8 characters).

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | TestEnvResponse
     """


    return (await asyncio_detailed(
        service_id=service_id,
client=client,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
