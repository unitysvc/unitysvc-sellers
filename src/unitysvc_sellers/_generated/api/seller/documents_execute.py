from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.document_execute_response import DocumentExecuteResponse
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    document_id: UUID,
    *,
    force: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    params: dict[str, Any] = {}

    params["force"] = force


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/seller/documents/{document_id}/execute".format(document_id=quote(str(document_id), safe=""),),
        "params": params,
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> DocumentExecuteResponse | ErrorResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = DocumentExecuteResponse.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[DocumentExecuteResponse | ErrorResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[DocumentExecuteResponse | ErrorResponse | HTTPValidationError]:
    r""" Execute Document

     Execute a code example or connectivity test (seller pre-submission check).

    This is the seller's **pre-submission dry-run** tool: it queues a
    Celery task that runs the document's script against the platform's
    ops_customer API key and records the result in ``meta.test``. It does
    **not** touch service status or trigger admin review — contrast with
    the formal submission flow via
    ``PATCH /seller/services/{id}`` (status=pending), which queues an
    orchestrated test run as part of the review pipeline.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller
    - Not be marked ``test.status == \"skip\"`` in meta

    Test execution uses ``OPS_CUSTOMER_API_KEY`` for gateway access and
    injects the gateway URL + key as environment variables into the script.

    Results are stored on ``document.meta.test``:
    - ``status``: ``success|task_failed|script_failed|unexpected_output``
    - ``error``: error message when status != success
    - ``executed_at``: ISO timestamp of execution
    - ``exit_code``, ``stdout``, ``stderr`` (truncated to 10KB)
    - ``output_contains``: if set on the document, stdout must contain
      this substring for success

    Set ``force=true`` to re-run a document whose test already recorded a
    success.

    Args:
        document_id (UUID):
        force (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentExecuteResponse | ErrorResponse | HTTPValidationError]
     """


    kwargs = _get_kwargs(
        document_id=document_id,
force=force,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> DocumentExecuteResponse | ErrorResponse | HTTPValidationError | None:
    r""" Execute Document

     Execute a code example or connectivity test (seller pre-submission check).

    This is the seller's **pre-submission dry-run** tool: it queues a
    Celery task that runs the document's script against the platform's
    ops_customer API key and records the result in ``meta.test``. It does
    **not** touch service status or trigger admin review — contrast with
    the formal submission flow via
    ``PATCH /seller/services/{id}`` (status=pending), which queues an
    orchestrated test run as part of the review pipeline.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller
    - Not be marked ``test.status == \"skip\"`` in meta

    Test execution uses ``OPS_CUSTOMER_API_KEY`` for gateway access and
    injects the gateway URL + key as environment variables into the script.

    Results are stored on ``document.meta.test``:
    - ``status``: ``success|task_failed|script_failed|unexpected_output``
    - ``error``: error message when status != success
    - ``executed_at``: ISO timestamp of execution
    - ``exit_code``, ``stdout``, ``stderr`` (truncated to 10KB)
    - ``output_contains``: if set on the document, stdout must contain
      this substring for success

    Set ``force=true`` to re-run a document whose test already recorded a
    success.

    Args:
        document_id (UUID):
        force (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentExecuteResponse | ErrorResponse | HTTPValidationError
     """


    return sync_detailed(
        document_id=document_id,
client=client,
force=force,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[DocumentExecuteResponse | ErrorResponse | HTTPValidationError]:
    r""" Execute Document

     Execute a code example or connectivity test (seller pre-submission check).

    This is the seller's **pre-submission dry-run** tool: it queues a
    Celery task that runs the document's script against the platform's
    ops_customer API key and records the result in ``meta.test``. It does
    **not** touch service status or trigger admin review — contrast with
    the formal submission flow via
    ``PATCH /seller/services/{id}`` (status=pending), which queues an
    orchestrated test run as part of the review pipeline.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller
    - Not be marked ``test.status == \"skip\"`` in meta

    Test execution uses ``OPS_CUSTOMER_API_KEY`` for gateway access and
    injects the gateway URL + key as environment variables into the script.

    Results are stored on ``document.meta.test``:
    - ``status``: ``success|task_failed|script_failed|unexpected_output``
    - ``error``: error message when status != success
    - ``executed_at``: ISO timestamp of execution
    - ``exit_code``, ``stdout``, ``stderr`` (truncated to 10KB)
    - ``output_contains``: if set on the document, stdout must contain
      this substring for success

    Set ``force=true`` to re-run a document whose test already recorded a
    success.

    Args:
        document_id (UUID):
        force (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentExecuteResponse | ErrorResponse | HTTPValidationError]
     """


    kwargs = _get_kwargs(
        document_id=document_id,
force=force,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> DocumentExecuteResponse | ErrorResponse | HTTPValidationError | None:
    r""" Execute Document

     Execute a code example or connectivity test (seller pre-submission check).

    This is the seller's **pre-submission dry-run** tool: it queues a
    Celery task that runs the document's script against the platform's
    ops_customer API key and records the result in ``meta.test``. It does
    **not** touch service status or trigger admin review — contrast with
    the formal submission flow via
    ``PATCH /seller/services/{id}`` (status=pending), which queues an
    orchestrated test run as part of the review pipeline.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller
    - Not be marked ``test.status == \"skip\"`` in meta

    Test execution uses ``OPS_CUSTOMER_API_KEY`` for gateway access and
    injects the gateway URL + key as environment variables into the script.

    Results are stored on ``document.meta.test``:
    - ``status``: ``success|task_failed|script_failed|unexpected_output``
    - ``error``: error message when status != success
    - ``executed_at``: ISO timestamp of execution
    - ``exit_code``, ``stdout``, ``stderr`` (truncated to 10KB)
    - ``output_contains``: if set on the document, stdout must contain
      this substring for success

    Set ``force=true`` to re-run a document whose test already recorded a
    success.

    Args:
        document_id (UUID):
        force (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentExecuteResponse | ErrorResponse | HTTPValidationError
     """


    return (await asyncio_detailed(
        document_id=document_id,
client=client,
force=force,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
