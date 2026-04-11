from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.response_tasks_get_task_status import ResponseTasksGetTaskStatus
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    task_id: str,
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
        "url": "/tasks/{task_id}".format(task_id=quote(str(task_id), safe=""),),
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> HTTPValidationError | ResponseTasksGetTaskStatus | None:
    if response.status_code == 200:
        response_200 = ResponseTasksGetTaskStatus.from_dict(response.json())



        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())



        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[HTTPValidationError | ResponseTasksGetTaskStatus]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    task_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[HTTPValidationError | ResponseTasksGetTaskStatus]:
    """ Get Task Status

     Get the status of a single Celery task.

    Args:
        task_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseTasksGetTaskStatus]
     """


    kwargs = _get_kwargs(
        task_id=task_id,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    task_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> HTTPValidationError | ResponseTasksGetTaskStatus | None:
    """ Get Task Status

     Get the status of a single Celery task.

    Args:
        task_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseTasksGetTaskStatus
     """


    return sync_detailed(
        task_id=task_id,
client=client,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    task_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[HTTPValidationError | ResponseTasksGetTaskStatus]:
    """ Get Task Status

     Get the status of a single Celery task.

    Args:
        task_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseTasksGetTaskStatus]
     """


    kwargs = _get_kwargs(
        task_id=task_id,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    task_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> HTTPValidationError | ResponseTasksGetTaskStatus | None:
    """ Get Task Status

     Get the status of a single Celery task.

    Args:
        task_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseTasksGetTaskStatus
     """


    return (await asyncio_detailed(
        task_id=task_id,
client=client,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
