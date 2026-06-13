from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.template_instance_create import TemplateInstanceCreate
from ...models.template_instance_create_response import TemplateInstanceCreateResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: TemplateInstanceCreate,
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
        "url": "/instances",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | TemplateInstanceCreateResponse | None:
    if response.status_code == 202:
        response_202 = TemplateInstanceCreateResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | TemplateInstanceCreateResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: TemplateInstanceCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | TemplateInstanceCreateResponse]:
    r"""Create Instance

     Create a service from a template + parameters.

    The single path to a service from a template (dashboard, CLI, and CI all
    use it). Creates the backing ``TemplateInstance`` (the durable provenance
    handle, and the basis for capability-pool membership) and renders it into a
    **draft** service via the canonical ingest pipeline. With
    ``auto_submit=True`` (the dashboard's one-click \"create & submit\") the draft
    is also submitted for review in the same async chain; otherwise it stays a
    reviewable draft. The template must be **active**. Returns 202 with the new
    ``instance_id`` and the ingest ``task_id``.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstanceCreate): Create a template instance and render it into a service.

            Always produces a ``TemplateInstance`` + a **draft** ``Service``. Set
            ``auto_submit=True`` to also submit that draft for review in the same call
            (the one-click "create & submit" path); leave it ``False`` to create a
            reviewable draft and submit later via ``PATCH /seller/services`` (the batch
            path). Request-only — not stored on the instance.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | TemplateInstanceCreateResponse]
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
    body: TemplateInstanceCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | TemplateInstanceCreateResponse | None:
    r"""Create Instance

     Create a service from a template + parameters.

    The single path to a service from a template (dashboard, CLI, and CI all
    use it). Creates the backing ``TemplateInstance`` (the durable provenance
    handle, and the basis for capability-pool membership) and renders it into a
    **draft** service via the canonical ingest pipeline. With
    ``auto_submit=True`` (the dashboard's one-click \"create & submit\") the draft
    is also submitted for review in the same async chain; otherwise it stays a
    reviewable draft. The template must be **active**. Returns 202 with the new
    ``instance_id`` and the ingest ``task_id``.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstanceCreate): Create a template instance and render it into a service.

            Always produces a ``TemplateInstance`` + a **draft** ``Service``. Set
            ``auto_submit=True`` to also submit that draft for review in the same call
            (the one-click "create & submit" path); leave it ``False`` to create a
            reviewable draft and submit later via ``PATCH /seller/services`` (the batch
            path). Request-only — not stored on the instance.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | TemplateInstanceCreateResponse
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
    body: TemplateInstanceCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | TemplateInstanceCreateResponse]:
    r"""Create Instance

     Create a service from a template + parameters.

    The single path to a service from a template (dashboard, CLI, and CI all
    use it). Creates the backing ``TemplateInstance`` (the durable provenance
    handle, and the basis for capability-pool membership) and renders it into a
    **draft** service via the canonical ingest pipeline. With
    ``auto_submit=True`` (the dashboard's one-click \"create & submit\") the draft
    is also submitted for review in the same async chain; otherwise it stays a
    reviewable draft. The template must be **active**. Returns 202 with the new
    ``instance_id`` and the ingest ``task_id``.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstanceCreate): Create a template instance and render it into a service.

            Always produces a ``TemplateInstance`` + a **draft** ``Service``. Set
            ``auto_submit=True`` to also submit that draft for review in the same call
            (the one-click "create & submit" path); leave it ``False`` to create a
            reviewable draft and submit later via ``PATCH /seller/services`` (the batch
            path). Request-only — not stored on the instance.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | TemplateInstanceCreateResponse]
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
    body: TemplateInstanceCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | TemplateInstanceCreateResponse | None:
    r"""Create Instance

     Create a service from a template + parameters.

    The single path to a service from a template (dashboard, CLI, and CI all
    use it). Creates the backing ``TemplateInstance`` (the durable provenance
    handle, and the basis for capability-pool membership) and renders it into a
    **draft** service via the canonical ingest pipeline. With
    ``auto_submit=True`` (the dashboard's one-click \"create & submit\") the draft
    is also submitted for review in the same async chain; otherwise it stays a
    reviewable draft. The template must be **active**. Returns 202 with the new
    ``instance_id`` and the ingest ``task_id``.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstanceCreate): Create a template instance and render it into a service.

            Always produces a ``TemplateInstance`` + a **draft** ``Service``. Set
            ``auto_submit=True`` to also submit that draft for review in the same call
            (the one-click "create & submit" path); leave it ``False`` to create a
            reviewable draft and submit later via ``PATCH /seller/services`` (the batch
            path). Request-only — not stored on the instance.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | TemplateInstanceCreateResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
