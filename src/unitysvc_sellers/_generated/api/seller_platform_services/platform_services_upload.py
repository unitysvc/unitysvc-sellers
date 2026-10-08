from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.platform_service_upload import PlatformServiceUpload
from ...models.service_upload_response import ServiceUploadResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: PlatformServiceUpload,
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
        "url": "/platform-services",
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
    body: PlatformServiceUpload,
    idempotency_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | ServiceUploadResponse]:
    """Upload Platform Service

     Publish a platform service together with its member template.

    The platform service is identified by ``service_status.service_id`` when
    given (it survives a rename), else by this seller's platform service of
    that name. Its listing must declare the ``/p`` address it serves.

    Requires a ``trusted`` or ``partner`` seller. The response is ``202`` with
    the ingest ``task_id``; the task result carries the platform service id,
    the action taken and the member template id.

    Args:
        idempotency_key (None | str | Unset): Optional client-supplied key for safe retries. When
            set, the server guarantees the underlying work runs at most once for this key within a 24h
            window — replaying the same key returns the same task id without queueing the work twice.
            Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (PlatformServiceUpload): A platform service and its member template, published
            together (#2569).

            A platform service is a seller's product: it buys capacity from member
            sellers and resells it at a ``/p`` address its listing declares. The member
            template is what other sellers instantiate to join it, so it travels in the
            same upload and is owned through the platform service.

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
    body: PlatformServiceUpload,
    idempotency_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | ServiceUploadResponse | None:
    """Upload Platform Service

     Publish a platform service together with its member template.

    The platform service is identified by ``service_status.service_id`` when
    given (it survives a rename), else by this seller's platform service of
    that name. Its listing must declare the ``/p`` address it serves.

    Requires a ``trusted`` or ``partner`` seller. The response is ``202`` with
    the ingest ``task_id``; the task result carries the platform service id,
    the action taken and the member template id.

    Args:
        idempotency_key (None | str | Unset): Optional client-supplied key for safe retries. When
            set, the server guarantees the underlying work runs at most once for this key within a 24h
            window — replaying the same key returns the same task id without queueing the work twice.
            Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (PlatformServiceUpload): A platform service and its member template, published
            together (#2569).

            A platform service is a seller's product: it buys capacity from member
            sellers and resells it at a ``/p`` address its listing declares. The member
            template is what other sellers instantiate to join it, so it travels in the
            same upload and is owned through the platform service.

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
    body: PlatformServiceUpload,
    idempotency_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | ServiceUploadResponse]:
    """Upload Platform Service

     Publish a platform service together with its member template.

    The platform service is identified by ``service_status.service_id`` when
    given (it survives a rename), else by this seller's platform service of
    that name. Its listing must declare the ``/p`` address it serves.

    Requires a ``trusted`` or ``partner`` seller. The response is ``202`` with
    the ingest ``task_id``; the task result carries the platform service id,
    the action taken and the member template id.

    Args:
        idempotency_key (None | str | Unset): Optional client-supplied key for safe retries. When
            set, the server guarantees the underlying work runs at most once for this key within a 24h
            window — replaying the same key returns the same task id without queueing the work twice.
            Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (PlatformServiceUpload): A platform service and its member template, published
            together (#2569).

            A platform service is a seller's product: it buys capacity from member
            sellers and resells it at a ``/p`` address its listing declares. The member
            template is what other sellers instantiate to join it, so it travels in the
            same upload and is owned through the platform service.

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
    body: PlatformServiceUpload,
    idempotency_key: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | ServiceUploadResponse | None:
    """Upload Platform Service

     Publish a platform service together with its member template.

    The platform service is identified by ``service_status.service_id`` when
    given (it survives a rename), else by this seller's platform service of
    that name. Its listing must declare the ``/p`` address it serves.

    Requires a ``trusted`` or ``partner`` seller. The response is ``202`` with
    the ingest ``task_id``; the task result carries the platform service id,
    the action taken and the member template id.

    Args:
        idempotency_key (None | str | Unset): Optional client-supplied key for safe retries. When
            set, the server guarantees the underlying work runs at most once for this key within a 24h
            window — replaying the same key returns the same task id without queueing the work twice.
            Allowed characters: A-Z, a-z, 0-9, underscore, hyphen. Length 1–128.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (PlatformServiceUpload): A platform service and its member template, published
            together (#2569).

            A platform service is a seller's product: it buys capacity from member
            sellers and resells it at a ``/p`` address its listing declares. The member
            template is what other sellers instantiate to join it, so it travels in the
            same upload and is owned through the platform service.

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
