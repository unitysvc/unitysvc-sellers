from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_render_response import DocumentRenderResponse
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    document_id: str,
    *,
    interface: None | Unset | UUID = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_interface: None | str | Unset
    if isinstance(interface, Unset):
        json_interface = UNSET
    elif isinstance(interface, UUID):
        json_interface = str(interface)
    else:
        json_interface = interface
    params["interface"] = json_interface

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/documents/{document_id}/render".format(
            document_id=quote(str(document_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DocumentRenderResponse | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = DocumentRenderResponse.from_dict(response.json())

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
        response_422 = ErrorResponse.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DocumentRenderResponse | ErrorResponse]:
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
    interface: None | Unset | UUID = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[DocumentRenderResponse | ErrorResponse]:
    r"""Render Document

     Render a code-example or connectivity-test document on demand.

    Returns the document's ``file_content`` after Jinja2 expansion against a
    render context derived from the document's service.  The mode is selected
    by the ``interface`` query param:

    - ``interface=<uuid>`` → **gateway / e2e mode** (``local_testing=False``).
      Render context: the named :class:`AccessInterface`'s gateway URL +
      routing_key, plus the listing's ``enrollment_vars`` /
      ``ops_testing_parameters`` (``params``) / ``routing_vars``.  This is
      what ``usvc_seller services run-tests`` consumes per-interface, and
      what the frontend calls to display \"the code I'd run\".
    - ``interface`` omitted → **upstream mode** (``local_testing=True``).
      Render context: the offering's ``upstream_access_config`` (first
      interface).  Used for upstream connectivity testing (#878); output
      matches ``usvc_seller data run-tests`` byte-for-byte.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller
    - When ``interface`` is given: the interface must belong to the same
      service.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the input
    was a template.  ``UNITYSVC_API_KEY`` is intentionally never inlined — it
    is read from the environment at execution time, on every code path.

    Args:
        document_id (str):
        interface (None | Unset | UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentRenderResponse | ErrorResponse]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        interface=interface,
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
    interface: None | Unset | UUID = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> DocumentRenderResponse | ErrorResponse | None:
    r"""Render Document

     Render a code-example or connectivity-test document on demand.

    Returns the document's ``file_content`` after Jinja2 expansion against a
    render context derived from the document's service.  The mode is selected
    by the ``interface`` query param:

    - ``interface=<uuid>`` → **gateway / e2e mode** (``local_testing=False``).
      Render context: the named :class:`AccessInterface`'s gateway URL +
      routing_key, plus the listing's ``enrollment_vars`` /
      ``ops_testing_parameters`` (``params``) / ``routing_vars``.  This is
      what ``usvc_seller services run-tests`` consumes per-interface, and
      what the frontend calls to display \"the code I'd run\".
    - ``interface`` omitted → **upstream mode** (``local_testing=True``).
      Render context: the offering's ``upstream_access_config`` (first
      interface).  Used for upstream connectivity testing (#878); output
      matches ``usvc_seller data run-tests`` byte-for-byte.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller
    - When ``interface`` is given: the interface must belong to the same
      service.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the input
    was a template.  ``UNITYSVC_API_KEY`` is intentionally never inlined — it
    is read from the environment at execution time, on every code path.

    Args:
        document_id (str):
        interface (None | Unset | UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentRenderResponse | ErrorResponse
    """

    return sync_detailed(
        document_id=document_id,
        client=client,
        interface=interface,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    document_id: str,
    *,
    client: AuthenticatedClient | Client,
    interface: None | Unset | UUID = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[DocumentRenderResponse | ErrorResponse]:
    r"""Render Document

     Render a code-example or connectivity-test document on demand.

    Returns the document's ``file_content`` after Jinja2 expansion against a
    render context derived from the document's service.  The mode is selected
    by the ``interface`` query param:

    - ``interface=<uuid>`` → **gateway / e2e mode** (``local_testing=False``).
      Render context: the named :class:`AccessInterface`'s gateway URL +
      routing_key, plus the listing's ``enrollment_vars`` /
      ``ops_testing_parameters`` (``params``) / ``routing_vars``.  This is
      what ``usvc_seller services run-tests`` consumes per-interface, and
      what the frontend calls to display \"the code I'd run\".
    - ``interface`` omitted → **upstream mode** (``local_testing=True``).
      Render context: the offering's ``upstream_access_config`` (first
      interface).  Used for upstream connectivity testing (#878); output
      matches ``usvc_seller data run-tests`` byte-for-byte.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller
    - When ``interface`` is given: the interface must belong to the same
      service.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the input
    was a template.  ``UNITYSVC_API_KEY`` is intentionally never inlined — it
    is read from the environment at execution time, on every code path.

    Args:
        document_id (str):
        interface (None | Unset | UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentRenderResponse | ErrorResponse]
    """

    kwargs = _get_kwargs(
        document_id=document_id,
        interface=interface,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    document_id: str,
    *,
    client: AuthenticatedClient | Client,
    interface: None | Unset | UUID = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> DocumentRenderResponse | ErrorResponse | None:
    r"""Render Document

     Render a code-example or connectivity-test document on demand.

    Returns the document's ``file_content`` after Jinja2 expansion against a
    render context derived from the document's service.  The mode is selected
    by the ``interface`` query param:

    - ``interface=<uuid>`` → **gateway / e2e mode** (``local_testing=False``).
      Render context: the named :class:`AccessInterface`'s gateway URL +
      routing_key, plus the listing's ``enrollment_vars`` /
      ``ops_testing_parameters`` (``params``) / ``routing_vars``.  This is
      what ``usvc_seller services run-tests`` consumes per-interface, and
      what the frontend calls to display \"the code I'd run\".
    - ``interface`` omitted → **upstream mode** (``local_testing=True``).
      Render context: the offering's ``upstream_access_config`` (first
      interface).  Used for upstream connectivity testing (#878); output
      matches ``usvc_seller data run-tests`` byte-for-byte.

    The document must:
    - Have category ``code_example`` or ``connectivity_test``
    - Belong to a service owned by the current seller
    - When ``interface`` is given: the interface must belong to the same
      service.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the input
    was a template.  ``UNITYSVC_API_KEY`` is intentionally never inlined — it
    is read from the environment at execution time, on every code path.

    Args:
        document_id (str):
        interface (None | Unset | UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentRenderResponse | ErrorResponse
    """

    return (
        await asyncio_detailed(
            document_id=document_id,
            client=client,
            interface=interface,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
