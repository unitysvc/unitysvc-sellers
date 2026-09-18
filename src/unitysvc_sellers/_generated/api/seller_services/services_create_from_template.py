from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.service_upload_response import ServiceUploadResponse
from ...models.template_instantiation_create import TemplateInstantiationCreate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: TemplateInstantiationCreate,
    idempotency_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(idempotency_key, Unset):
        headers["Idempotency-Key"] = idempotency_key

    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/services/from-template",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | ServiceUploadResponse | None:
    if response.status_code == 202:
        response_202 = ServiceUploadResponse.from_dict(response.json())

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
) -> Response[ErrorResponse | HTTPValidationError | ServiceUploadResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: TemplateInstantiationCreate,
    idempotency_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | ServiceUploadResponse]:
    """Create Service From Template

     Create or revise a service from a platform template + parameters.

    The second constructor for a service, alongside ``POST /services``: that
    one takes the whole provider + offering + listing payload, this one takes
    a template id plus parameters and renders the payload server-side. Both
    queue the same ingest task and return the same ``202`` + ``task_id``.

    This is stateless — the backend stores generation provenance on the
    generated Service, not in a separate row, which is why there is no
    instance object in the response.

    Pass ``service_id`` to re-render an existing template-managed service
    (the ``<name>.service.json`` sidecar that ``usvc_seller specs upload``
    writes back); omit it to create a fresh one.

    Headers:
    - Idempotency-Key: Optional client-supplied key for safe retries, with
      the same semantics as ``POST /services`` — the key becomes the Celery
      task id and is deduped for 24 hours, so replaying it returns the same
      task id instead of queueing a second render.

    Args:
        idempotency_key (None | str | Unset): Optional client-supplied key for safe retries. When
            set, the server guarantees the underlying work runs at most once for this key within a 24h
            window — replaying the same key returns the same task id without queueing the work twice.
            Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstantiationCreate): Request body for ``POST /v1/seller/services/from-
            template``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceUploadResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        idempotency_key=idempotency_key,
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
    body: TemplateInstantiationCreate,
    idempotency_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | ServiceUploadResponse | None:
    """Create Service From Template

     Create or revise a service from a platform template + parameters.

    The second constructor for a service, alongside ``POST /services``: that
    one takes the whole provider + offering + listing payload, this one takes
    a template id plus parameters and renders the payload server-side. Both
    queue the same ingest task and return the same ``202`` + ``task_id``.

    This is stateless — the backend stores generation provenance on the
    generated Service, not in a separate row, which is why there is no
    instance object in the response.

    Pass ``service_id`` to re-render an existing template-managed service
    (the ``<name>.service.json`` sidecar that ``usvc_seller specs upload``
    writes back); omit it to create a fresh one.

    Headers:
    - Idempotency-Key: Optional client-supplied key for safe retries, with
      the same semantics as ``POST /services`` — the key becomes the Celery
      task id and is deduped for 24 hours, so replaying it returns the same
      task id instead of queueing a second render.

    Args:
        idempotency_key (None | str | Unset): Optional client-supplied key for safe retries. When
            set, the server guarantees the underlying work runs at most once for this key within a 24h
            window — replaying the same key returns the same task id without queueing the work twice.
            Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstantiationCreate): Request body for ``POST /v1/seller/services/from-
            template``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceUploadResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        idempotency_key=idempotency_key,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: TemplateInstantiationCreate,
    idempotency_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | ServiceUploadResponse]:
    """Create Service From Template

     Create or revise a service from a platform template + parameters.

    The second constructor for a service, alongside ``POST /services``: that
    one takes the whole provider + offering + listing payload, this one takes
    a template id plus parameters and renders the payload server-side. Both
    queue the same ingest task and return the same ``202`` + ``task_id``.

    This is stateless — the backend stores generation provenance on the
    generated Service, not in a separate row, which is why there is no
    instance object in the response.

    Pass ``service_id`` to re-render an existing template-managed service
    (the ``<name>.service.json`` sidecar that ``usvc_seller specs upload``
    writes back); omit it to create a fresh one.

    Headers:
    - Idempotency-Key: Optional client-supplied key for safe retries, with
      the same semantics as ``POST /services`` — the key becomes the Celery
      task id and is deduped for 24 hours, so replaying it returns the same
      task id instead of queueing a second render.

    Args:
        idempotency_key (None | str | Unset): Optional client-supplied key for safe retries. When
            set, the server guarantees the underlying work runs at most once for this key within a 24h
            window — replaying the same key returns the same task id without queueing the work twice.
            Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstantiationCreate): Request body for ``POST /v1/seller/services/from-
            template``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceUploadResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        idempotency_key=idempotency_key,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: TemplateInstantiationCreate,
    idempotency_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | ServiceUploadResponse | None:
    """Create Service From Template

     Create or revise a service from a platform template + parameters.

    The second constructor for a service, alongside ``POST /services``: that
    one takes the whole provider + offering + listing payload, this one takes
    a template id plus parameters and renders the payload server-side. Both
    queue the same ingest task and return the same ``202`` + ``task_id``.

    This is stateless — the backend stores generation provenance on the
    generated Service, not in a separate row, which is why there is no
    instance object in the response.

    Pass ``service_id`` to re-render an existing template-managed service
    (the ``<name>.service.json`` sidecar that ``usvc_seller specs upload``
    writes back); omit it to create a fresh one.

    Headers:
    - Idempotency-Key: Optional client-supplied key for safe retries, with
      the same semantics as ``POST /services`` — the key becomes the Celery
      task id and is deduped for 24 hours, so replaying it returns the same
      task id instead of queueing a second render.

    Args:
        idempotency_key (None | str | Unset): Optional client-supplied key for safe retries. When
            set, the server guarantees the underlying work runs at most once for this key within a 24h
            window — replaying the same key returns the same task id without queueing the work twice.
            Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (TemplateInstantiationCreate): Request body for ``POST /v1/seller/services/from-
            template``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceUploadResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            idempotency_key=idempotency_key,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
