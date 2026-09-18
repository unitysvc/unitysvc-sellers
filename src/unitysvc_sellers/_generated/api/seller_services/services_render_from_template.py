from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.template_instantiation_render import TemplateInstantiationRender
from ...models.template_instantiation_render_response import TemplateInstantiationRenderResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: TemplateInstantiationRender,
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
        "url": "/services/from-template/render",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | TemplateInstantiationRenderResponse | None:
    if response.status_code == 200:
        response_200 = TemplateInstantiationRenderResponse.from_dict(response.json())

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
) -> Response[ErrorResponse | HTTPValidationError | TemplateInstantiationRenderResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: TemplateInstantiationRender,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | TemplateInstantiationRenderResponse]:
    """Render Service From Template

     Preview a system-template render for local inspection.

    The dry run of ``POST /services/from-template``: the template bodies stay
    platform-owned, and this gives the seller the same bounded rendering path
    without creating a service, task, or document record.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstantiationRender): Render a platform-owned template without creating a
            service.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | TemplateInstantiationRenderResponse]
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
    body: TemplateInstantiationRender,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | TemplateInstantiationRenderResponse | None:
    """Render Service From Template

     Preview a system-template render for local inspection.

    The dry run of ``POST /services/from-template``: the template bodies stay
    platform-owned, and this gives the seller the same bounded rendering path
    without creating a service, task, or document record.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstantiationRender): Render a platform-owned template without creating a
            service.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | TemplateInstantiationRenderResponse
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
    body: TemplateInstantiationRender,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | TemplateInstantiationRenderResponse]:
    """Render Service From Template

     Preview a system-template render for local inspection.

    The dry run of ``POST /services/from-template``: the template bodies stay
    platform-owned, and this gives the seller the same bounded rendering path
    without creating a service, task, or document record.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstantiationRender): Render a platform-owned template without creating a
            service.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | TemplateInstantiationRenderResponse]
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
    body: TemplateInstantiationRender,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | TemplateInstantiationRenderResponse | None:
    """Render Service From Template

     Preview a system-template render for local inspection.

    The dry run of ``POST /services/from-template``: the template bodies stay
    platform-owned, and this gives the seller the same bounded rendering path
    without creating a service, task, or document record.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstantiationRender): Render a platform-owned template without creating a
            service.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | TemplateInstantiationRenderResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
