from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.enrollment_key_return import EnrollmentKeyReturn
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    enrollment_id: UUID,
    *,
    body: EnrollmentKeyReturn,
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
        "url": "/enrollments/{enrollment_id}/lease/return".format(
            enrollment_id=quote(str(enrollment_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ErrorResponse | HTTPValidationError | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

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
) -> Response[Any | ErrorResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    enrollment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: EnrollmentKeyReturn,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[Any | ErrorResponse | HTTPValidationError]:
    """Return Enrollment Key

     Return a leased key: it expires now. Returning a key twice, or one that
    was since leased again, does nothing.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (EnrollmentKeyReturn): The leased key being returned.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        enrollment_id=enrollment_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    enrollment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: EnrollmentKeyReturn,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Any | ErrorResponse | HTTPValidationError | None:
    """Return Enrollment Key

     Return a leased key: it expires now. Returning a key twice, or one that
    was since leased again, does nothing.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (EnrollmentKeyReturn): The leased key being returned.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse | HTTPValidationError
    """

    return sync_detailed(
        enrollment_id=enrollment_id,
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    enrollment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: EnrollmentKeyReturn,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[Any | ErrorResponse | HTTPValidationError]:
    """Return Enrollment Key

     Return a leased key: it expires now. Returning a key twice, or one that
    was since leased again, does nothing.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (EnrollmentKeyReturn): The leased key being returned.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        enrollment_id=enrollment_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    enrollment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: EnrollmentKeyReturn,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Any | ErrorResponse | HTTPValidationError | None:
    """Return Enrollment Key

     Return a leased key: it expires now. Returning a key twice, or one that
    was since leased again, does nothing.

    Args:
        enrollment_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (EnrollmentKeyReturn): The leased key being returned.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            enrollment_id=enrollment_id,
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
