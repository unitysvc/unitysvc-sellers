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
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
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
    client: AuthenticatedClient,
    interface: None | Unset | UUID = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[DocumentRenderResponse | ErrorResponse]:
    r"""Render Document

     Render a code-example or connectivity-test document on demand.

    Two modes via the ``interface`` query param:

    - ``interface=<uuid>`` → **gateway mode** (``local_testing=False``).
      Render context: the named :class:`AccessInterface`'s gateway URL +
      routing_key, plus the listing's ``enrollment_vars`` /
      ``ops_testing_parameters`` (``params``) / ``routing_vars``.  This
      is what ``usvc_seller services run-tests`` consumes per-interface,
      what the seller's \"preview as customer\" view calls, and what the
      anonymous marketplace ``/market/{id}`` page calls (for public
      documents).
    - ``interface`` omitted → **upstream mode** (``local_testing=True``).
      Render context: the offering's ``upstream_access_config`` (first
      interface).  Used for upstream connectivity testing (#878).
      Renders against the seller's upstream URL with ``${ secrets.X }``
      references resolved against the seller's secret store — the
      rendered output may inline credentials, so this mode is
      restricted to ops_customer (the platform test runner) and the
      seller-owner.

    Auth shape:

    - **Anonymous** is accepted for ``interface=<uuid>`` rendering of
      documents where ``is_public=True`` *and* the underlying service
      is ``active`` + ``visibility=public``.  This is the marketplace
      path: customers can render the same code they'd copy off the
      service-detail page.
    - **Seller-owner** can render any document on a service they own,
      in either mode.
    - **ops_customer** can render any document in any mode — the
      platform test runner needs upstream-mode access to verify
      seller-side connectivity.
    - All other authentications are rejected with 403.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the
    input was a template.  ``UNITYSVC_API_KEY`` is intentionally never
    inlined — it is read from the environment at execution time, on
    every code path.

    Args:
        document_id (str):
        interface (None | Unset | UUID):
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
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    document_id: str,
    *,
    client: AuthenticatedClient,
    interface: None | Unset | UUID = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> DocumentRenderResponse | ErrorResponse | None:
    r"""Render Document

     Render a code-example or connectivity-test document on demand.

    Two modes via the ``interface`` query param:

    - ``interface=<uuid>`` → **gateway mode** (``local_testing=False``).
      Render context: the named :class:`AccessInterface`'s gateway URL +
      routing_key, plus the listing's ``enrollment_vars`` /
      ``ops_testing_parameters`` (``params``) / ``routing_vars``.  This
      is what ``usvc_seller services run-tests`` consumes per-interface,
      what the seller's \"preview as customer\" view calls, and what the
      anonymous marketplace ``/market/{id}`` page calls (for public
      documents).
    - ``interface`` omitted → **upstream mode** (``local_testing=True``).
      Render context: the offering's ``upstream_access_config`` (first
      interface).  Used for upstream connectivity testing (#878).
      Renders against the seller's upstream URL with ``${ secrets.X }``
      references resolved against the seller's secret store — the
      rendered output may inline credentials, so this mode is
      restricted to ops_customer (the platform test runner) and the
      seller-owner.

    Auth shape:

    - **Anonymous** is accepted for ``interface=<uuid>`` rendering of
      documents where ``is_public=True`` *and* the underlying service
      is ``active`` + ``visibility=public``.  This is the marketplace
      path: customers can render the same code they'd copy off the
      service-detail page.
    - **Seller-owner** can render any document on a service they own,
      in either mode.
    - **ops_customer** can render any document in any mode — the
      platform test runner needs upstream-mode access to verify
      seller-side connectivity.
    - All other authentications are rejected with 403.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the
    input was a template.  ``UNITYSVC_API_KEY`` is intentionally never
    inlined — it is read from the environment at execution time, on
    every code path.

    Args:
        document_id (str):
        interface (None | Unset | UUID):
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
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    document_id: str,
    *,
    client: AuthenticatedClient,
    interface: None | Unset | UUID = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[DocumentRenderResponse | ErrorResponse]:
    r"""Render Document

     Render a code-example or connectivity-test document on demand.

    Two modes via the ``interface`` query param:

    - ``interface=<uuid>`` → **gateway mode** (``local_testing=False``).
      Render context: the named :class:`AccessInterface`'s gateway URL +
      routing_key, plus the listing's ``enrollment_vars`` /
      ``ops_testing_parameters`` (``params``) / ``routing_vars``.  This
      is what ``usvc_seller services run-tests`` consumes per-interface,
      what the seller's \"preview as customer\" view calls, and what the
      anonymous marketplace ``/market/{id}`` page calls (for public
      documents).
    - ``interface`` omitted → **upstream mode** (``local_testing=True``).
      Render context: the offering's ``upstream_access_config`` (first
      interface).  Used for upstream connectivity testing (#878).
      Renders against the seller's upstream URL with ``${ secrets.X }``
      references resolved against the seller's secret store — the
      rendered output may inline credentials, so this mode is
      restricted to ops_customer (the platform test runner) and the
      seller-owner.

    Auth shape:

    - **Anonymous** is accepted for ``interface=<uuid>`` rendering of
      documents where ``is_public=True`` *and* the underlying service
      is ``active`` + ``visibility=public``.  This is the marketplace
      path: customers can render the same code they'd copy off the
      service-detail page.
    - **Seller-owner** can render any document on a service they own,
      in either mode.
    - **ops_customer** can render any document in any mode — the
      platform test runner needs upstream-mode access to verify
      seller-side connectivity.
    - All other authentications are rejected with 403.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the
    input was a template.  ``UNITYSVC_API_KEY`` is intentionally never
    inlined — it is read from the environment at execution time, on
    every code path.

    Args:
        document_id (str):
        interface (None | Unset | UUID):
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
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    document_id: str,
    *,
    client: AuthenticatedClient,
    interface: None | Unset | UUID = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> DocumentRenderResponse | ErrorResponse | None:
    r"""Render Document

     Render a code-example or connectivity-test document on demand.

    Two modes via the ``interface`` query param:

    - ``interface=<uuid>`` → **gateway mode** (``local_testing=False``).
      Render context: the named :class:`AccessInterface`'s gateway URL +
      routing_key, plus the listing's ``enrollment_vars`` /
      ``ops_testing_parameters`` (``params``) / ``routing_vars``.  This
      is what ``usvc_seller services run-tests`` consumes per-interface,
      what the seller's \"preview as customer\" view calls, and what the
      anonymous marketplace ``/market/{id}`` page calls (for public
      documents).
    - ``interface`` omitted → **upstream mode** (``local_testing=True``).
      Render context: the offering's ``upstream_access_config`` (first
      interface).  Used for upstream connectivity testing (#878).
      Renders against the seller's upstream URL with ``${ secrets.X }``
      references resolved against the seller's secret store — the
      rendered output may inline credentials, so this mode is
      restricted to ops_customer (the platform test runner) and the
      seller-owner.

    Auth shape:

    - **Anonymous** is accepted for ``interface=<uuid>`` rendering of
      documents where ``is_public=True`` *and* the underlying service
      is ``active`` + ``visibility=public``.  This is the marketplace
      path: customers can render the same code they'd copy off the
      service-detail page.
    - **Seller-owner** can render any document on a service they own,
      in either mode.
    - **ops_customer** can render any document in any mode — the
      platform test runner needs upstream-mode access to verify
      seller-side connectivity.
    - All other authentications are rejected with 403.

    The rendered ``filename`` has the ``.j2`` suffix stripped when the
    input was a template.  ``UNITYSVC_API_KEY`` is intentionally never
    inlined — it is read from the environment at execution time, on
    every code path.

    Args:
        document_id (str):
        interface (None | Unset | UUID):
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
            x_role_id=x_role_id,
        )
    ).parsed
