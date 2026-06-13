from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.service_form_submit_response import ServiceFormSubmitResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    form_id: str,
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
        "url": "/forms/{form_id}/submit".format(
            form_id=quote(str(form_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ServiceFormSubmitResponse | None:
    if response.status_code == 202:
        response_202 = ServiceFormSubmitResponse.from_dict(response.json())

        return response_202

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | ServiceFormSubmitResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    form_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceFormSubmitResponse]:
    """Submit Form

     Render and publish through the canonical ingest pipeline (async).

    Create (no ``service_id`` yet) requires the form's pinned template version
    to be **active**; revise (``service_id`` set) is allowed even on a
    deprecated version. The rendered listing carries the form's canonical
    ``service_id`` for revises, so the ingest worker branches exactly as it
    does for SDK uploads (create / revise-active / replace / unchanged).

    Returns 202 with the ingest ``task_id``; the form's ``service_id`` is
    reconciled from the task result on subsequent reads.

    Args:
        form_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceFormSubmitResponse]
    """

    kwargs = _get_kwargs(
        form_id=form_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    form_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceFormSubmitResponse | None:
    """Submit Form

     Render and publish through the canonical ingest pipeline (async).

    Create (no ``service_id`` yet) requires the form's pinned template version
    to be **active**; revise (``service_id`` set) is allowed even on a
    deprecated version. The rendered listing carries the form's canonical
    ``service_id`` for revises, so the ingest worker branches exactly as it
    does for SDK uploads (create / revise-active / replace / unchanged).

    Returns 202 with the ingest ``task_id``; the form's ``service_id`` is
    reconciled from the task result on subsequent reads.

    Args:
        form_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceFormSubmitResponse
    """

    return sync_detailed(
        form_id=form_id,
        client=client,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    form_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceFormSubmitResponse]:
    """Submit Form

     Render and publish through the canonical ingest pipeline (async).

    Create (no ``service_id`` yet) requires the form's pinned template version
    to be **active**; revise (``service_id`` set) is allowed even on a
    deprecated version. The rendered listing carries the form's canonical
    ``service_id`` for revises, so the ingest worker branches exactly as it
    does for SDK uploads (create / revise-active / replace / unchanged).

    Returns 202 with the ingest ``task_id``; the form's ``service_id`` is
    reconciled from the task result on subsequent reads.

    Args:
        form_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceFormSubmitResponse]
    """

    kwargs = _get_kwargs(
        form_id=form_id,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    form_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceFormSubmitResponse | None:
    """Submit Form

     Render and publish through the canonical ingest pipeline (async).

    Create (no ``service_id`` yet) requires the form's pinned template version
    to be **active**; revise (``service_id`` set) is allowed even on a
    deprecated version. The rendered listing carries the form's canonical
    ``service_id`` for revises, so the ingest worker branches exactly as it
    does for SDK uploads (create / revise-active / replace / unchanged).

    Returns 202 with the ingest ``task_id``; the form's ``service_id`` is
    reconciled from the task result on subsequent reads.

    Args:
        form_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceFormSubmitResponse
    """

    return (
        await asyncio_detailed(
            form_id=form_id,
            client=client,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
