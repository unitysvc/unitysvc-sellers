from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.service_update import ServiceUpdate
from ...models.service_update_response import ServiceUpdateResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    service_id: str,
    *,
    body: ServiceUpdate,
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
        "url": "/services/{service_id}".format(service_id=quote(str(service_id), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorResponse | HTTPValidationError | ServiceUpdateResponse | None:
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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorResponse | HTTPValidationError | ServiceUpdateResponse]:
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
    body: ServiceUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | ServiceUpdateResponse]:
    r""" Update Service

     Update a service — status, visibility, routing vars, and/or list price.

    All fields are optional. Include only the fields you want to change.
    Multiple fields can be updated in a single request.

    **Status** transitions (seller-allowed):
    draft → pending, rejected → pending, rejected → draft,
    pending → draft, active → deprecated.

    **Visibility**: ``public`` / ``unlisted`` / ``private``.
    Only active services can be set to ``public``.

    **Routing vars** and **list price** accept two forms:

    - *Full replacement* — a plain dict replaces the entire value::

        {\"routing_vars\": {\"region\": \"us-east\", \"count\": 42}}
        {\"list_price\": {\"type\": \"constant\", \"price\": \"1.00\"}}

    - *Partial update* — a dict with ``set`` and/or ``remove`` keys::

        {\"routing_vars\": {\"set\": {\"count\": 43}, \"remove\": [\"region\"]}}
        {\"list_price\": {\"set\": {\"input\": \"0.40\"}, \"remove\": [\"reference\"]}}

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceUpdate): Unified request body for updating a service.

            All fields are optional — include only the fields you want to change.
            Multiple fields can be updated in a single request.

            ``routing_vars`` and ``list_price`` accept two forms:

            - **Full replacement** — a plain dict replaces the entire value::

                {"routing_vars": {"region": "us-east", "count": 42}}

            - **Partial update** — a dict with ``set`` and/or ``remove`` keys::

                {"routing_vars": {"set": {"count": 43}, "remove": ["region"]}}

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceUpdateResponse]
     """


    kwargs = _get_kwargs(
        service_id=service_id,
body=body,
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
    body: ServiceUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | ServiceUpdateResponse | None:
    r""" Update Service

     Update a service — status, visibility, routing vars, and/or list price.

    All fields are optional. Include only the fields you want to change.
    Multiple fields can be updated in a single request.

    **Status** transitions (seller-allowed):
    draft → pending, rejected → pending, rejected → draft,
    pending → draft, active → deprecated.

    **Visibility**: ``public`` / ``unlisted`` / ``private``.
    Only active services can be set to ``public``.

    **Routing vars** and **list price** accept two forms:

    - *Full replacement* — a plain dict replaces the entire value::

        {\"routing_vars\": {\"region\": \"us-east\", \"count\": 42}}
        {\"list_price\": {\"type\": \"constant\", \"price\": \"1.00\"}}

    - *Partial update* — a dict with ``set`` and/or ``remove`` keys::

        {\"routing_vars\": {\"set\": {\"count\": 43}, \"remove\": [\"region\"]}}
        {\"list_price\": {\"set\": {\"input\": \"0.40\"}, \"remove\": [\"reference\"]}}

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceUpdate): Unified request body for updating a service.

            All fields are optional — include only the fields you want to change.
            Multiple fields can be updated in a single request.

            ``routing_vars`` and ``list_price`` accept two forms:

            - **Full replacement** — a plain dict replaces the entire value::

                {"routing_vars": {"region": "us-east", "count": 42}}

            - **Partial update** — a dict with ``set`` and/or ``remove`` keys::

                {"routing_vars": {"set": {"count": 43}, "remove": ["region"]}}

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceUpdateResponse
     """


    return sync_detailed(
        service_id=service_id,
client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ServiceUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | ServiceUpdateResponse]:
    r""" Update Service

     Update a service — status, visibility, routing vars, and/or list price.

    All fields are optional. Include only the fields you want to change.
    Multiple fields can be updated in a single request.

    **Status** transitions (seller-allowed):
    draft → pending, rejected → pending, rejected → draft,
    pending → draft, active → deprecated.

    **Visibility**: ``public`` / ``unlisted`` / ``private``.
    Only active services can be set to ``public``.

    **Routing vars** and **list price** accept two forms:

    - *Full replacement* — a plain dict replaces the entire value::

        {\"routing_vars\": {\"region\": \"us-east\", \"count\": 42}}
        {\"list_price\": {\"type\": \"constant\", \"price\": \"1.00\"}}

    - *Partial update* — a dict with ``set`` and/or ``remove`` keys::

        {\"routing_vars\": {\"set\": {\"count\": 43}, \"remove\": [\"region\"]}}
        {\"list_price\": {\"set\": {\"input\": \"0.40\"}, \"remove\": [\"reference\"]}}

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceUpdate): Unified request body for updating a service.

            All fields are optional — include only the fields you want to change.
            Multiple fields can be updated in a single request.

            ``routing_vars`` and ``list_price`` accept two forms:

            - **Full replacement** — a plain dict replaces the entire value::

                {"routing_vars": {"region": "us-east", "count": 42}}

            - **Partial update** — a dict with ``set`` and/or ``remove`` keys::

                {"routing_vars": {"set": {"count": 43}, "remove": ["region"]}}

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceUpdateResponse]
     """


    kwargs = _get_kwargs(
        service_id=service_id,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ServiceUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | ServiceUpdateResponse | None:
    r""" Update Service

     Update a service — status, visibility, routing vars, and/or list price.

    All fields are optional. Include only the fields you want to change.
    Multiple fields can be updated in a single request.

    **Status** transitions (seller-allowed):
    draft → pending, rejected → pending, rejected → draft,
    pending → draft, active → deprecated.

    **Visibility**: ``public`` / ``unlisted`` / ``private``.
    Only active services can be set to ``public``.

    **Routing vars** and **list price** accept two forms:

    - *Full replacement* — a plain dict replaces the entire value::

        {\"routing_vars\": {\"region\": \"us-east\", \"count\": 42}}
        {\"list_price\": {\"type\": \"constant\", \"price\": \"1.00\"}}

    - *Partial update* — a dict with ``set`` and/or ``remove`` keys::

        {\"routing_vars\": {\"set\": {\"count\": 43}, \"remove\": [\"region\"]}}
        {\"list_price\": {\"set\": {\"input\": \"0.40\"}, \"remove\": [\"reference\"]}}

    Args:
        service_id (str):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (ServiceUpdate): Unified request body for updating a service.

            All fields are optional — include only the fields you want to change.
            Multiple fields can be updated in a single request.

            ``routing_vars`` and ``list_price`` accept two forms:

            - **Full replacement** — a plain dict replaces the entire value::

                {"routing_vars": {"region": "us-east", "count": 42}}

            - **Partial update** — a dict with ``set`` and/or ``remove`` keys::

                {"routing_vars": {"set": {"count": 43}, "remove": ["region"]}}

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceUpdateResponse
     """


    return (await asyncio_detailed(
        service_id=service_id,
client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
