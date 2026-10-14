from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_test_status_response import DocumentTestStatusResponse
from ...models.document_test_update import DocumentTestUpdate
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    document_id: UUID,
    *,
    body: DocumentTestUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/documents/{document_id}".format(
            document_id=quote(str(document_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DocumentTestStatusResponse | ErrorResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = DocumentTestStatusResponse.from_dict(response.json())

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
) -> Response[DocumentTestStatusResponse | ErrorResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: DocumentTestUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[DocumentTestStatusResponse | ErrorResponse | HTTPValidationError]:
    """Update Document Test

     Skip or unskip a document's test.

    Dispatches on the body's ``status`` field:

    - ``skip`` — mark the test as skipped (stamps ``skipped_at`` /
      ``skipped_by``). Rejected for ``connectivity_test`` documents (only
      ``code_example`` can be skipped).
    - ``pending`` — unskip, and forget the document's recorded runs so the
      next run re-proves it.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller

    Args:
        document_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (DocumentTestUpdate): Request body for updating document test status.

            The ``status`` field drives dispatch:

            - ``skip`` — mark the test as skipped (stamps ``skipped_at`` /
              ``skipped_by``). Rejected for ``connectivity_test`` documents (only
              ``code_example`` can be skipped).
            - ``pending`` — unskip, and forget the document's recorded runs
              (including earned sticky passes), so the next run re-proves it.

            Test results are recorded only by the platform's own runners; a seller
            cannot report one.

            This endpoint replaces the previously-separate /skip and /unskip routes,
            which dispatched to the same backing field via different HTTP verbs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentTestStatusResponse | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: DocumentTestUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> DocumentTestStatusResponse | ErrorResponse | HTTPValidationError | None:
    """Update Document Test

     Skip or unskip a document's test.

    Dispatches on the body's ``status`` field:

    - ``skip`` — mark the test as skipped (stamps ``skipped_at`` /
      ``skipped_by``). Rejected for ``connectivity_test`` documents (only
      ``code_example`` can be skipped).
    - ``pending`` — unskip, and forget the document's recorded runs so the
      next run re-proves it.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller

    Args:
        document_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (DocumentTestUpdate): Request body for updating document test status.

            The ``status`` field drives dispatch:

            - ``skip`` — mark the test as skipped (stamps ``skipped_at`` /
              ``skipped_by``). Rejected for ``connectivity_test`` documents (only
              ``code_example`` can be skipped).
            - ``pending`` — unskip, and forget the document's recorded runs
              (including earned sticky passes), so the next run re-proves it.

            Test results are recorded only by the platform's own runners; a seller
            cannot report one.

            This endpoint replaces the previously-separate /skip and /unskip routes,
            which dispatched to the same backing field via different HTTP verbs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentTestStatusResponse | ErrorResponse | HTTPValidationError
    """

    return sync_detailed(
        document_id=document_id,
        client=client,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: DocumentTestUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[DocumentTestStatusResponse | ErrorResponse | HTTPValidationError]:
    """Update Document Test

     Skip or unskip a document's test.

    Dispatches on the body's ``status`` field:

    - ``skip`` — mark the test as skipped (stamps ``skipped_at`` /
      ``skipped_by``). Rejected for ``connectivity_test`` documents (only
      ``code_example`` can be skipped).
    - ``pending`` — unskip, and forget the document's recorded runs so the
      next run re-proves it.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller

    Args:
        document_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (DocumentTestUpdate): Request body for updating document test status.

            The ``status`` field drives dispatch:

            - ``skip`` — mark the test as skipped (stamps ``skipped_at`` /
              ``skipped_by``). Rejected for ``connectivity_test`` documents (only
              ``code_example`` can be skipped).
            - ``pending`` — unskip, and forget the document's recorded runs
              (including earned sticky passes), so the next run re-proves it.

            Test results are recorded only by the platform's own runners; a seller
            cannot report one.

            This endpoint replaces the previously-separate /skip and /unskip routes,
            which dispatched to the same backing field via different HTTP verbs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentTestStatusResponse | ErrorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        body=body,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    document_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: DocumentTestUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> DocumentTestStatusResponse | ErrorResponse | HTTPValidationError | None:
    """Update Document Test

     Skip or unskip a document's test.

    Dispatches on the body's ``status`` field:

    - ``skip`` — mark the test as skipped (stamps ``skipped_at`` /
      ``skipped_by``). Rejected for ``connectivity_test`` documents (only
      ``code_example`` can be skipped).
    - ``pending`` — unskip, and forget the document's recorded runs so the
      next run re-proves it.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller

    Args:
        document_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (DocumentTestUpdate): Request body for updating document test status.

            The ``status`` field drives dispatch:

            - ``skip`` — mark the test as skipped (stamps ``skipped_at`` /
              ``skipped_by``). Rejected for ``connectivity_test`` documents (only
              ``code_example`` can be skipped).
            - ``pending`` — unskip, and forget the document's recorded runs
              (including earned sticky passes), so the next run re-proves it.

            Test results are recorded only by the platform's own runners; a seller
            cannot report one.

            This endpoint replaces the previously-separate /skip and /unskip routes,
            which dispatched to the same backing field via different HTTP verbs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentTestStatusResponse | ErrorResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            document_id=document_id,
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
