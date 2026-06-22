from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.service_update_response import ServiceUpdateResponse
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
        "method": "post",
        "url": "/services/{service_id}/submit".format(
            service_id=quote(str(service_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | ServiceUpdateResponse | None:
    if response.status_code == 200:
        response_200 = ServiceUpdateResponse.from_dict(response.json())

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
) -> Response[ErrorResponse | HTTPValidationError | ServiceUpdateResponse]:
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
) -> Response[ErrorResponse | HTTPValidationError | ServiceUpdateResponse]:
    r"""Submit Service For Review Endpoint

     Submit a service for review (``draft`` / ``rejected`` / ``suspended`` →
    ``pending``) **and** run the activation test pipeline.

    This is the testing counterpart to ``PATCH /services/{id}`` with
    ``status=pending``: the PATCH is a pure status change (\"mark pending\") with
    no side effects, whereas *this* endpoint additionally validates the content
    and dispatches the gateway test job that drives the service to
    ``review`` / ``active`` / ``rejected`` based on the result.

    - **Duplicate content** ⇒ ``200`` no-op (idempotent re-submit, so the
      upload-then-submit CI loop in ``unitysvc-services-*`` repos doesn't flap
      red on a \"no real changes\" merge).
    - **Invalid content** ⇒ ``400`` (status set to ``rejected``).
    - Otherwise ⇒ status set to ``pending`` and the test pipeline dispatched.

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceUpdateResponse]
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
) -> ErrorResponse | HTTPValidationError | ServiceUpdateResponse | None:
    r"""Submit Service For Review Endpoint

     Submit a service for review (``draft`` / ``rejected`` / ``suspended`` →
    ``pending``) **and** run the activation test pipeline.

    This is the testing counterpart to ``PATCH /services/{id}`` with
    ``status=pending``: the PATCH is a pure status change (\"mark pending\") with
    no side effects, whereas *this* endpoint additionally validates the content
    and dispatches the gateway test job that drives the service to
    ``review`` / ``active`` / ``rejected`` based on the result.

    - **Duplicate content** ⇒ ``200`` no-op (idempotent re-submit, so the
      upload-then-submit CI loop in ``unitysvc-services-*`` repos doesn't flap
      red on a \"no real changes\" merge).
    - **Invalid content** ⇒ ``400`` (status set to ``rejected``).
    - Otherwise ⇒ status set to ``pending`` and the test pipeline dispatched.

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceUpdateResponse
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
) -> Response[ErrorResponse | HTTPValidationError | ServiceUpdateResponse]:
    r"""Submit Service For Review Endpoint

     Submit a service for review (``draft`` / ``rejected`` / ``suspended`` →
    ``pending``) **and** run the activation test pipeline.

    This is the testing counterpart to ``PATCH /services/{id}`` with
    ``status=pending``: the PATCH is a pure status change (\"mark pending\") with
    no side effects, whereas *this* endpoint additionally validates the content
    and dispatches the gateway test job that drives the service to
    ``review`` / ``active`` / ``rejected`` based on the result.

    - **Duplicate content** ⇒ ``200`` no-op (idempotent re-submit, so the
      upload-then-submit CI loop in ``unitysvc-services-*`` repos doesn't flap
      red on a \"no real changes\" merge).
    - **Invalid content** ⇒ ``400`` (status set to ``rejected``).
    - Otherwise ⇒ status set to ``pending`` and the test pipeline dispatched.

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceUpdateResponse]
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
) -> ErrorResponse | HTTPValidationError | ServiceUpdateResponse | None:
    r"""Submit Service For Review Endpoint

     Submit a service for review (``draft`` / ``rejected`` / ``suspended`` →
    ``pending``) **and** run the activation test pipeline.

    This is the testing counterpart to ``PATCH /services/{id}`` with
    ``status=pending``: the PATCH is a pure status change (\"mark pending\") with
    no side effects, whereas *this* endpoint additionally validates the content
    and dispatches the gateway test job that drives the service to
    ``review`` / ``active`` / ``rejected`` based on the result.

    - **Duplicate content** ⇒ ``200`` no-op (idempotent re-submit, so the
      upload-then-submit CI loop in ``unitysvc-services-*`` repos doesn't flap
      red on a \"no real changes\" merge).
    - **Invalid content** ⇒ ``400`` (status set to ``rejected``).
    - Otherwise ⇒ status set to ``pending`` and the test pipeline dispatched.

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceUpdateResponse
    """

    return (
        await asyncio_detailed(
            service_id=service_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
