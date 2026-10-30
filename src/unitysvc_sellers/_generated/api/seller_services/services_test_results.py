from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.service_test_results_response import ServiceTestResultsResponse
from ...types import UNSET, Response, Unset


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
        "url": "/services/{service_id}/test-results".format(
            service_id=quote(str(service_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | ServiceTestResultsResponse | None:
    if response.status_code == 200:
        response_200 = ServiceTestResultsResponse.from_dict(response.json())

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


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | HTTPValidationError | ServiceTestResultsResponse]:
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
) -> Response[ErrorResponse | HTTPValidationError | ServiceTestResultsResponse]:
    """Get Service Test Results

     A service's test results: the admission verdict, the recorded runs
    that decide it, and the required runs that are missing or stale.

    A platform member's are its runs of its platform service's documents
    through ``/p`` pinned to it (#2622) — those documents belong to the
    platform service, the RUNS to the member. Each run's output is at
    ``…/test-results/{run_id}/output``. Supports partial service IDs.

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceTestResultsResponse]
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
) -> ErrorResponse | HTTPValidationError | ServiceTestResultsResponse | None:
    """Get Service Test Results

     A service's test results: the admission verdict, the recorded runs
    that decide it, and the required runs that are missing or stale.

    A platform member's are its runs of its platform service's documents
    through ``/p`` pinned to it (#2622) — those documents belong to the
    platform service, the RUNS to the member. Each run's output is at
    ``…/test-results/{run_id}/output``. Supports partial service IDs.

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceTestResultsResponse
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
) -> Response[ErrorResponse | HTTPValidationError | ServiceTestResultsResponse]:
    """Get Service Test Results

     A service's test results: the admission verdict, the recorded runs
    that decide it, and the required runs that are missing or stale.

    A platform member's are its runs of its platform service's documents
    through ``/p`` pinned to it (#2622) — those documents belong to the
    platform service, the RUNS to the member. Each run's output is at
    ``…/test-results/{run_id}/output``. Supports partial service IDs.

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceTestResultsResponse]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | ServiceTestResultsResponse | None:
    """Get Service Test Results

     A service's test results: the admission verdict, the recorded runs
    that decide it, and the required runs that are missing or stale.

    A platform member's are its runs of its platform service's documents
    through ``/p`` pinned to it (#2622) — those documents belong to the
    platform service, the RUNS to the member. Each run's output is at
    ``…/test-results/{run_id}/output``. Supports partial service IDs.

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceTestResultsResponse
    """

    return (
        await asyncio_detailed(
            service_id=service_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
