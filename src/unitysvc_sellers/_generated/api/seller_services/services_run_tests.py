from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.run_tests_response import RunTestsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    service_id: str,
    *,
    document_id: None | str | Unset = UNSET,
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

    json_document_id: None | str | Unset
    if isinstance(document_id, Unset):
        json_document_id = UNSET
    else:
        json_document_id = document_id
    params["document_id"] = json_document_id

    params["force"] = force

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/services/{service_id}/run-tests".format(
            service_id=quote(str(service_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | RunTestsResponse | None:
    if response.status_code == 202:
        response_202 = RunTestsResponse.from_dict(response.json())

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


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | HTTPValidationError | RunTestsResponse]:
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
    document_id: None | str | Unset = UNSET,
    force: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | RunTestsResponse]:
    """Run Service Tests Endpoint

     Queue a server-side diagnostic test run on one of the caller's services.

    Replaces the local-execution ``usvc_seller services run-tests`` path
    (#1105).  Runs every executable document (``connectivity_test`` and
    ``code_example``) against every active access interface and upstream
    channel inside the cluster — the same network environment customers
    hit — and falls back to an upstream-mode probe on any channel-level
    gateway failure
    so the result attributes the fault as ``platform_fault`` vs
    ``upstream_fault``.

    The service's status is snapshotted and temporarily elevated to
    ``pending`` if it isn't already in a routable state
    (``pending`` / ``review`` / ``active``); the original status is
    restored in a ``finally`` block so a worker crash mid-run can't
    leave the service permanently elevated.

    Per-(doc × iface × channel) results land on
    ``Document.meta.test.tests[<iface_id>].channels[<channel>]``.  The
    interface row remains a rollup for legacy ``services show-test``
    readers.  The task return payload duplicates a summary with
    stdout/stderr truncated to 16 KB per stream; full streams remain
    available via ``show-test``.

    Poll via ``GET /v1/seller/tasks/{task_id}``.

    Supports partial service ID matching (minimum 8 characters).

    Args:
        service_id (str):
        document_id (None | str | Unset): Restrict to a single document on the service.
        force (bool | Unset): Re-execute documents whose per-iface result on
            ``meta.test.tests[iface_id].status`` was previously ``success``. Default skips them,
            matching the CLI's behaviour. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | RunTestsResponse]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
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
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    document_id: None | str | Unset = UNSET,
    force: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | RunTestsResponse | None:
    """Run Service Tests Endpoint

     Queue a server-side diagnostic test run on one of the caller's services.

    Replaces the local-execution ``usvc_seller services run-tests`` path
    (#1105).  Runs every executable document (``connectivity_test`` and
    ``code_example``) against every active access interface and upstream
    channel inside the cluster — the same network environment customers
    hit — and falls back to an upstream-mode probe on any channel-level
    gateway failure
    so the result attributes the fault as ``platform_fault`` vs
    ``upstream_fault``.

    The service's status is snapshotted and temporarily elevated to
    ``pending`` if it isn't already in a routable state
    (``pending`` / ``review`` / ``active``); the original status is
    restored in a ``finally`` block so a worker crash mid-run can't
    leave the service permanently elevated.

    Per-(doc × iface × channel) results land on
    ``Document.meta.test.tests[<iface_id>].channels[<channel>]``.  The
    interface row remains a rollup for legacy ``services show-test``
    readers.  The task return payload duplicates a summary with
    stdout/stderr truncated to 16 KB per stream; full streams remain
    available via ``show-test``.

    Poll via ``GET /v1/seller/tasks/{task_id}``.

    Supports partial service ID matching (minimum 8 characters).

    Args:
        service_id (str):
        document_id (None | str | Unset): Restrict to a single document on the service.
        force (bool | Unset): Re-execute documents whose per-iface result on
            ``meta.test.tests[iface_id].status`` was previously ``success``. Default skips them,
            matching the CLI's behaviour. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | RunTestsResponse
    """

    return sync_detailed(
        service_id=service_id,
        client=client,
        document_id=document_id,
        force=force,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    document_id: None | str | Unset = UNSET,
    force: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | RunTestsResponse]:
    """Run Service Tests Endpoint

     Queue a server-side diagnostic test run on one of the caller's services.

    Replaces the local-execution ``usvc_seller services run-tests`` path
    (#1105).  Runs every executable document (``connectivity_test`` and
    ``code_example``) against every active access interface and upstream
    channel inside the cluster — the same network environment customers
    hit — and falls back to an upstream-mode probe on any channel-level
    gateway failure
    so the result attributes the fault as ``platform_fault`` vs
    ``upstream_fault``.

    The service's status is snapshotted and temporarily elevated to
    ``pending`` if it isn't already in a routable state
    (``pending`` / ``review`` / ``active``); the original status is
    restored in a ``finally`` block so a worker crash mid-run can't
    leave the service permanently elevated.

    Per-(doc × iface × channel) results land on
    ``Document.meta.test.tests[<iface_id>].channels[<channel>]``.  The
    interface row remains a rollup for legacy ``services show-test``
    readers.  The task return payload duplicates a summary with
    stdout/stderr truncated to 16 KB per stream; full streams remain
    available via ``show-test``.

    Poll via ``GET /v1/seller/tasks/{task_id}``.

    Supports partial service ID matching (minimum 8 characters).

    Args:
        service_id (str):
        document_id (None | str | Unset): Restrict to a single document on the service.
        force (bool | Unset): Re-execute documents whose per-iface result on
            ``meta.test.tests[iface_id].status`` was previously ``success``. Default skips them,
            matching the CLI's behaviour. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | RunTestsResponse]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        document_id=document_id,
        force=force,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    document_id: None | str | Unset = UNSET,
    force: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | RunTestsResponse | None:
    """Run Service Tests Endpoint

     Queue a server-side diagnostic test run on one of the caller's services.

    Replaces the local-execution ``usvc_seller services run-tests`` path
    (#1105).  Runs every executable document (``connectivity_test`` and
    ``code_example``) against every active access interface and upstream
    channel inside the cluster — the same network environment customers
    hit — and falls back to an upstream-mode probe on any channel-level
    gateway failure
    so the result attributes the fault as ``platform_fault`` vs
    ``upstream_fault``.

    The service's status is snapshotted and temporarily elevated to
    ``pending`` if it isn't already in a routable state
    (``pending`` / ``review`` / ``active``); the original status is
    restored in a ``finally`` block so a worker crash mid-run can't
    leave the service permanently elevated.

    Per-(doc × iface × channel) results land on
    ``Document.meta.test.tests[<iface_id>].channels[<channel>]``.  The
    interface row remains a rollup for legacy ``services show-test``
    readers.  The task return payload duplicates a summary with
    stdout/stderr truncated to 16 KB per stream; full streams remain
    available via ``show-test``.

    Poll via ``GET /v1/seller/tasks/{task_id}``.

    Supports partial service ID matching (minimum 8 characters).

    Args:
        service_id (str):
        document_id (None | str | Unset): Restrict to a single document on the service.
        force (bool | Unset): Re-execute documents whose per-iface result on
            ``meta.test.tests[iface_id].status`` was previously ``success``. Default skips them,
            matching the CLI's behaviour. Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | RunTestsResponse
    """

    return (
        await asyncio_detailed(
            service_id=service_id,
            client=client,
            document_id=document_id,
            force=force,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
