from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.test_detail_response import TestDetailResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    document_id: str,
    *,
    interface_id: None | str | Unset = UNSET,
    channel: None | str | Unset = UNSET,
    upstream: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_interface_id: None | str | Unset
    if isinstance(interface_id, Unset):
        json_interface_id = UNSET
    else:
        json_interface_id = interface_id
    params["interface_id"] = json_interface_id

    json_channel: None | str | Unset
    if isinstance(channel, Unset):
        json_channel = UNSET
    else:
        json_channel = channel
    params["channel"] = json_channel

    params["upstream"] = upstream

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/documents/{document_id}/test-details".format(
            document_id=quote(str(document_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | TestDetailResponse | None:
    if response.status_code == 200:
        response_200 = TestDetailResponse.from_dict(response.json())

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


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | HTTPValidationError | TestDetailResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    document_id: str,
    *,
    client: AuthenticatedClient | Client,
    interface_id: None | str | Unset = UNSET,
    channel: None | str | Unset = UNSET,
    upstream: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | TestDetailResponse]:
    """Get Document Test Details

     Full execution details (stdout/stderr/masked env/rendered script) for
    one test-result cell of a document (#1901).

    Selectors mirror how results are recorded: none → the single-document
    block; ``interface_id`` (+ optional ``channel``) → that gateway cell;
    ``upstream=true`` (+ optional ``channel``) → the upstream probe record.
    404 means no such cell was ever recorded; ``expired=true`` means the
    cell exists but its detail blob aged out of retention — re-run the test
    to reproduce the details.

    Supports partial document ID matching (minimum 8 characters).

    Args:
        document_id (str):
        interface_id (None | str | Unset):
        channel (None | str | Unset):
        upstream (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | TestDetailResponse]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        interface_id=interface_id,
        channel=channel,
        upstream=upstream,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    document_id: str,
    *,
    client: AuthenticatedClient | Client,
    interface_id: None | str | Unset = UNSET,
    channel: None | str | Unset = UNSET,
    upstream: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | TestDetailResponse | None:
    """Get Document Test Details

     Full execution details (stdout/stderr/masked env/rendered script) for
    one test-result cell of a document (#1901).

    Selectors mirror how results are recorded: none → the single-document
    block; ``interface_id`` (+ optional ``channel``) → that gateway cell;
    ``upstream=true`` (+ optional ``channel``) → the upstream probe record.
    404 means no such cell was ever recorded; ``expired=true`` means the
    cell exists but its detail blob aged out of retention — re-run the test
    to reproduce the details.

    Supports partial document ID matching (minimum 8 characters).

    Args:
        document_id (str):
        interface_id (None | str | Unset):
        channel (None | str | Unset):
        upstream (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | TestDetailResponse
    """

    return sync_detailed(
        document_id=document_id,
        client=client,
        interface_id=interface_id,
        channel=channel,
        upstream=upstream,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    document_id: str,
    *,
    client: AuthenticatedClient | Client,
    interface_id: None | str | Unset = UNSET,
    channel: None | str | Unset = UNSET,
    upstream: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | TestDetailResponse]:
    """Get Document Test Details

     Full execution details (stdout/stderr/masked env/rendered script) for
    one test-result cell of a document (#1901).

    Selectors mirror how results are recorded: none → the single-document
    block; ``interface_id`` (+ optional ``channel``) → that gateway cell;
    ``upstream=true`` (+ optional ``channel``) → the upstream probe record.
    404 means no such cell was ever recorded; ``expired=true`` means the
    cell exists but its detail blob aged out of retention — re-run the test
    to reproduce the details.

    Supports partial document ID matching (minimum 8 characters).

    Args:
        document_id (str):
        interface_id (None | str | Unset):
        channel (None | str | Unset):
        upstream (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | TestDetailResponse]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        interface_id=interface_id,
        channel=channel,
        upstream=upstream,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    document_id: str,
    *,
    client: AuthenticatedClient | Client,
    interface_id: None | str | Unset = UNSET,
    channel: None | str | Unset = UNSET,
    upstream: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | TestDetailResponse | None:
    """Get Document Test Details

     Full execution details (stdout/stderr/masked env/rendered script) for
    one test-result cell of a document (#1901).

    Selectors mirror how results are recorded: none → the single-document
    block; ``interface_id`` (+ optional ``channel``) → that gateway cell;
    ``upstream=true`` (+ optional ``channel``) → the upstream probe record.
    404 means no such cell was ever recorded; ``expired=true`` means the
    cell exists but its detail blob aged out of retention — re-run the test
    to reproduce the details.

    Supports partial document ID matching (minimum 8 characters).

    Args:
        document_id (str):
        interface_id (None | str | Unset):
        channel (None | str | Unset):
        upstream (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | TestDetailResponse
    """

    return (
        await asyncio_detailed(
            document_id=document_id,
            client=client,
            interface_id=interface_id,
            channel=channel,
            upstream=upstream,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
