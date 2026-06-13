from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.service_form_create import ServiceFormCreate
from ...models.service_form_instantiate_response import ServiceFormInstantiateResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ServiceFormCreate,
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
        "url": "/forms/instantiate",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ServiceFormInstantiateResponse | None:
    if response.status_code == 202:
        response_202 = ServiceFormInstantiateResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ServiceFormInstantiateResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceFormCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceFormInstantiateResponse]:
    """Instantiate Form

     One-shot: create a form from a template + parameters and submit it.

    This is the single path to a service from a template (dashboard, CLI, and
    CI all use it). Creates the backing ``ServiceForm`` (the durable provenance
    handle, and the basis for capability-pool membership) and dispatches it
    through the canonical ingest pipeline in one call. The template must be
    **active**. Returns 202 with the new ``form_id`` and the ingest ``task_id``.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceFormCreate): Create a form bound to the active version of a template.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceFormInstantiateResponse]
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
    body: ServiceFormCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceFormInstantiateResponse | None:
    """Instantiate Form

     One-shot: create a form from a template + parameters and submit it.

    This is the single path to a service from a template (dashboard, CLI, and
    CI all use it). Creates the backing ``ServiceForm`` (the durable provenance
    handle, and the basis for capability-pool membership) and dispatches it
    through the canonical ingest pipeline in one call. The template must be
    **active**. Returns 202 with the new ``form_id`` and the ingest ``task_id``.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceFormCreate): Create a form bound to the active version of a template.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceFormInstantiateResponse
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
    body: ServiceFormCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ServiceFormInstantiateResponse]:
    """Instantiate Form

     One-shot: create a form from a template + parameters and submit it.

    This is the single path to a service from a template (dashboard, CLI, and
    CI all use it). Creates the backing ``ServiceForm`` (the durable provenance
    handle, and the basis for capability-pool membership) and dispatches it
    through the canonical ingest pipeline in one call. The template must be
    **active**. Returns 202 with the new ``form_id`` and the ingest ``task_id``.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceFormCreate): Create a form bound to the active version of a template.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ServiceFormInstantiateResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ServiceFormCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | ServiceFormInstantiateResponse | None:
    """Instantiate Form

     One-shot: create a form from a template + parameters and submit it.

    This is the single path to a service from a template (dashboard, CLI, and
    CI all use it). Creates the backing ``ServiceForm`` (the durable provenance
    handle, and the basis for capability-pool membership) and dispatches it
    through the canonical ingest pipeline in one call. The template must be
    **active**. Returns 202 with the new ``form_id`` and the ingest ``task_id``.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceFormCreate): Create a form bound to the active version of a template.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ServiceFormInstantiateResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
