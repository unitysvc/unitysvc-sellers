from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.service_data_input import ServiceDataInput
from ...models.service_upload_response import ServiceUploadResponse
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union



def _get_kwargs(
    *,
    body: ServiceDataInput,
    dryrun: Union[Unset, bool] = False,
    idempotency_key: Union[None, Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(idempotency_key, Unset):
        headers["Idempotency-Key"] = idempotency_key

    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    params: dict[str, Any] = {}

    params["dryrun"] = dryrun


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/services",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ErrorResponse, HTTPValidationError, ServiceUploadResponse]]:
    if response.status_code == 202:
        response_202 = ServiceUploadResponse.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ErrorResponse, HTTPValidationError, ServiceUploadResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ServiceDataInput,
    dryrun: Union[Unset, bool] = False,
    idempotency_key: Union[None, Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, HTTPValidationError, ServiceUploadResponse]]:
    """ Upload My Service

     Upload a complete service (provider, offering, and listing) together.

    Accepts all three entity types in a single request and ingests them in
    the correct order: provider -> offering -> listing.

    The seller is identified by X-Role-Id header (JWT) or API key's role_id.

    Query Parameters:
    - dryrun: If True, the upload runs **synchronously** inside the request
      and returns the validation result directly (status 200 with
      ``dryrun_result`` populated). No Celery task is queued and no DB
      writes are made. Use this to validate a payload before committing.

    Headers:
    - Idempotency-Key: Optional client-supplied key for safe retries on
      real (non-dryrun) uploads. When set, the server uses it as the
      Celery task id and dedupes by it for 24 hours via a Redis SETNX
      gate, so replaying the same key returns the same task id without
      queueing the work twice. Ignored when ``dryrun=true`` because
      dryrun has no side effects to dedupe.

    For non-dryrun uploads the response is ``status=202`` with ``task_id``
    set; the task can be polled via the Celery result backend.

    Args:
        dryrun (Union[Unset, bool]):  Default: False.
        idempotency_key (Union[None, Unset, str]): Optional client-supplied key for safe retries.
            When set, the server guarantees the underlying work runs at most once for this key within
            a 24h window — replaying the same key returns the same task id without queueing the work
            twice. Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (ServiceDataInput): Complete service data input for publishing.

            Fields are typed against the shared ``unitysvc_core`` models so the
            OpenAPI spec carries the full provider/offering/listing schemas, and
            generated clients expose typed upload methods instead of ``dict[str, Any]``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, ServiceUploadResponse]]
     """


    kwargs = _get_kwargs(
        body=body,
dryrun=dryrun,
idempotency_key=idempotency_key,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ServiceDataInput,
    dryrun: Union[Unset, bool] = False,
    idempotency_key: Union[None, Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[ErrorResponse, HTTPValidationError, ServiceUploadResponse]]:
    """ Upload My Service

     Upload a complete service (provider, offering, and listing) together.

    Accepts all three entity types in a single request and ingests them in
    the correct order: provider -> offering -> listing.

    The seller is identified by X-Role-Id header (JWT) or API key's role_id.

    Query Parameters:
    - dryrun: If True, the upload runs **synchronously** inside the request
      and returns the validation result directly (status 200 with
      ``dryrun_result`` populated). No Celery task is queued and no DB
      writes are made. Use this to validate a payload before committing.

    Headers:
    - Idempotency-Key: Optional client-supplied key for safe retries on
      real (non-dryrun) uploads. When set, the server uses it as the
      Celery task id and dedupes by it for 24 hours via a Redis SETNX
      gate, so replaying the same key returns the same task id without
      queueing the work twice. Ignored when ``dryrun=true`` because
      dryrun has no side effects to dedupe.

    For non-dryrun uploads the response is ``status=202`` with ``task_id``
    set; the task can be polled via the Celery result backend.

    Args:
        dryrun (Union[Unset, bool]):  Default: False.
        idempotency_key (Union[None, Unset, str]): Optional client-supplied key for safe retries.
            When set, the server guarantees the underlying work runs at most once for this key within
            a 24h window — replaying the same key returns the same task id without queueing the work
            twice. Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (ServiceDataInput): Complete service data input for publishing.

            Fields are typed against the shared ``unitysvc_core`` models so the
            OpenAPI spec carries the full provider/offering/listing schemas, and
            generated clients expose typed upload methods instead of ``dict[str, Any]``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, ServiceUploadResponse]
     """


    return sync_detailed(
        client=client,
body=body,
dryrun=dryrun,
idempotency_key=idempotency_key,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ServiceDataInput,
    dryrun: Union[Unset, bool] = False,
    idempotency_key: Union[None, Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[ErrorResponse, HTTPValidationError, ServiceUploadResponse]]:
    """ Upload My Service

     Upload a complete service (provider, offering, and listing) together.

    Accepts all three entity types in a single request and ingests them in
    the correct order: provider -> offering -> listing.

    The seller is identified by X-Role-Id header (JWT) or API key's role_id.

    Query Parameters:
    - dryrun: If True, the upload runs **synchronously** inside the request
      and returns the validation result directly (status 200 with
      ``dryrun_result`` populated). No Celery task is queued and no DB
      writes are made. Use this to validate a payload before committing.

    Headers:
    - Idempotency-Key: Optional client-supplied key for safe retries on
      real (non-dryrun) uploads. When set, the server uses it as the
      Celery task id and dedupes by it for 24 hours via a Redis SETNX
      gate, so replaying the same key returns the same task id without
      queueing the work twice. Ignored when ``dryrun=true`` because
      dryrun has no side effects to dedupe.

    For non-dryrun uploads the response is ``status=202`` with ``task_id``
    set; the task can be polled via the Celery result backend.

    Args:
        dryrun (Union[Unset, bool]):  Default: False.
        idempotency_key (Union[None, Unset, str]): Optional client-supplied key for safe retries.
            When set, the server guarantees the underlying work runs at most once for this key within
            a 24h window — replaying the same key returns the same task id without queueing the work
            twice. Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (ServiceDataInput): Complete service data input for publishing.

            Fields are typed against the shared ``unitysvc_core`` models so the
            OpenAPI spec carries the full provider/offering/listing schemas, and
            generated clients expose typed upload methods instead of ``dict[str, Any]``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, ServiceUploadResponse]]
     """


    kwargs = _get_kwargs(
        body=body,
dryrun=dryrun,
idempotency_key=idempotency_key,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ServiceDataInput,
    dryrun: Union[Unset, bool] = False,
    idempotency_key: Union[None, Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[ErrorResponse, HTTPValidationError, ServiceUploadResponse]]:
    """ Upload My Service

     Upload a complete service (provider, offering, and listing) together.

    Accepts all three entity types in a single request and ingests them in
    the correct order: provider -> offering -> listing.

    The seller is identified by X-Role-Id header (JWT) or API key's role_id.

    Query Parameters:
    - dryrun: If True, the upload runs **synchronously** inside the request
      and returns the validation result directly (status 200 with
      ``dryrun_result`` populated). No Celery task is queued and no DB
      writes are made. Use this to validate a payload before committing.

    Headers:
    - Idempotency-Key: Optional client-supplied key for safe retries on
      real (non-dryrun) uploads. When set, the server uses it as the
      Celery task id and dedupes by it for 24 hours via a Redis SETNX
      gate, so replaying the same key returns the same task id without
      queueing the work twice. Ignored when ``dryrun=true`` because
      dryrun has no side effects to dedupe.

    For non-dryrun uploads the response is ``status=202`` with ``task_id``
    set; the task can be polled via the Celery result backend.

    Args:
        dryrun (Union[Unset, bool]):  Default: False.
        idempotency_key (Union[None, Unset, str]): Optional client-supplied key for safe retries.
            When set, the server guarantees the underlying work runs at most once for this key within
            a 24h window — replaying the same key returns the same task id without queueing the work
            twice. Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (ServiceDataInput): Complete service data input for publishing.

            Fields are typed against the shared ``unitysvc_core`` models so the
            OpenAPI spec carries the full provider/offering/listing schemas, and
            generated clients expose typed upload methods instead of ``dict[str, Any]``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, ServiceUploadResponse]
     """


    return (await asyncio_detailed(
        client=client,
body=body,
dryrun=dryrun,
idempotency_key=idempotency_key,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
