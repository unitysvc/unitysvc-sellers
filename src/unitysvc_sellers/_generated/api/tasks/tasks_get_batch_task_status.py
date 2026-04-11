from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.response_tasks_get_batch_task_status import ResponseTasksGetBatchTaskStatus
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    body: list[str],
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
        "url": "/tasks/batch-status",
    }

    _kwargs["json"] = body




    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> HTTPValidationError | ResponseTasksGetBatchTaskStatus | None:
    if response.status_code == 200:
        response_200 = ResponseTasksGetBatchTaskStatus.from_dict(response.json())



        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())



        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[HTTPValidationError | ResponseTasksGetBatchTaskStatus]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: list[str],
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[HTTPValidationError | ResponseTasksGetBatchTaskStatus]:
    """ Get Batch Task Status

     Get the status of multiple Celery tasks in a single request.

    Accepts up to 100 task IDs and returns a mapping of task_id -> status.
    This is more efficient than polling each task individually.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseTasksGetBatchTaskStatus]
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
    body: list[str],
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> HTTPValidationError | ResponseTasksGetBatchTaskStatus | None:
    """ Get Batch Task Status

     Get the status of multiple Celery tasks in a single request.

    Accepts up to 100 task IDs and returns a mapping of task_id -> status.
    This is more efficient than polling each task individually.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseTasksGetBatchTaskStatus
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
    body: list[str],
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[HTTPValidationError | ResponseTasksGetBatchTaskStatus]:
    """ Get Batch Task Status

     Get the status of multiple Celery tasks in a single request.

    Accepts up to 100 task IDs and returns a mapping of task_id -> status.
    This is more efficient than polling each task individually.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseTasksGetBatchTaskStatus]
     """


    kwargs = _get_kwargs(
        body=body,
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
    body: list[str],
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> HTTPValidationError | ResponseTasksGetBatchTaskStatus | None:
    """ Get Batch Task Status

     Get the status of multiple Celery tasks in a single request.

    Accepts up to 100 task IDs and returns a mapping of task_id -> status.
    This is more efficient than polling each task individually.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseTasksGetBatchTaskStatus
     """


    return (await asyncio_detailed(
        client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
