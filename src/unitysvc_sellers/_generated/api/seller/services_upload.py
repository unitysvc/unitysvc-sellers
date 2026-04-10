from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.service_data_input import ServiceDataInput
from ...models.task_queued_response import TaskQueuedResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    body: ServiceDataInput,
    dryrun: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    params: dict[str, Any] = {}

    params["dryrun"] = dryrun


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/seller/services",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorResponse | HTTPValidationError | TaskQueuedResponse | None:
    if response.status_code == 202:
        response_202 = TaskQueuedResponse.from_dict(response.json())



        return response_202

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorResponse | HTTPValidationError | TaskQueuedResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceDataInput,
    dryrun: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | TaskQueuedResponse]:
    """ Upload My Service

     Upload a complete service (provider, offering, and listing) together.

    Accepts all three entity types in a single request and ingests them in
    the correct order: provider -> offering -> listing.

    The seller is identified by X-Role-Id header (JWT) or API key's role_id.

    Query Parameters:
    - dryrun: If True, only checks what would be done without making changes.

    The returned task_id can be polled via the Celery result backend; when
    the task completes, its result includes document IDs for each entity.

    Args:
        dryrun (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceDataInput): Complete service data input for publishing.

            Fields are typed against the shared ``unitysvc_core`` models so the
            OpenAPI spec carries the full provider/offering/listing schemas, and
            generated clients expose typed upload methods instead of ``dict[str, Any]``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | TaskQueuedResponse]
     """


    kwargs = _get_kwargs(
        body=body,
dryrun=dryrun,
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
    body: ServiceDataInput,
    dryrun: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | TaskQueuedResponse | None:
    """ Upload My Service

     Upload a complete service (provider, offering, and listing) together.

    Accepts all three entity types in a single request and ingests them in
    the correct order: provider -> offering -> listing.

    The seller is identified by X-Role-Id header (JWT) or API key's role_id.

    Query Parameters:
    - dryrun: If True, only checks what would be done without making changes.

    The returned task_id can be polled via the Celery result backend; when
    the task completes, its result includes document IDs for each entity.

    Args:
        dryrun (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceDataInput): Complete service data input for publishing.

            Fields are typed against the shared ``unitysvc_core`` models so the
            OpenAPI spec carries the full provider/offering/listing schemas, and
            generated clients expose typed upload methods instead of ``dict[str, Any]``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | TaskQueuedResponse
     """


    return sync_detailed(
        client=client,
body=body,
dryrun=dryrun,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceDataInput,
    dryrun: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | TaskQueuedResponse]:
    """ Upload My Service

     Upload a complete service (provider, offering, and listing) together.

    Accepts all three entity types in a single request and ingests them in
    the correct order: provider -> offering -> listing.

    The seller is identified by X-Role-Id header (JWT) or API key's role_id.

    Query Parameters:
    - dryrun: If True, only checks what would be done without making changes.

    The returned task_id can be polled via the Celery result backend; when
    the task completes, its result includes document IDs for each entity.

    Args:
        dryrun (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceDataInput): Complete service data input for publishing.

            Fields are typed against the shared ``unitysvc_core`` models so the
            OpenAPI spec carries the full provider/offering/listing schemas, and
            generated clients expose typed upload methods instead of ``dict[str, Any]``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | TaskQueuedResponse]
     """


    kwargs = _get_kwargs(
        body=body,
dryrun=dryrun,
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
    body: ServiceDataInput,
    dryrun: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | TaskQueuedResponse | None:
    """ Upload My Service

     Upload a complete service (provider, offering, and listing) together.

    Accepts all three entity types in a single request and ingests them in
    the correct order: provider -> offering -> listing.

    The seller is identified by X-Role-Id header (JWT) or API key's role_id.

    Query Parameters:
    - dryrun: If True, only checks what would be done without making changes.

    The returned task_id can be polled via the Celery result backend; when
    the task completes, its result includes document IDs for each entity.

    Args:
        dryrun (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceDataInput): Complete service data input for publishing.

            Fields are typed against the shared ``unitysvc_core`` models so the
            OpenAPI spec carries the full provider/offering/listing schemas, and
            generated clients expose typed upload methods instead of ``dict[str, Any]``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | TaskQueuedResponse
     """


    return (await asyncio_detailed(
        client=client,
body=body,
dryrun=dryrun,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
