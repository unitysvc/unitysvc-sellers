from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.price_rule_lifecycle_status_enum import check_price_rule_lifecycle_status_enum
from ...models.price_rule_lifecycle_status_enum import PriceRuleLifecycleStatusEnum
from ...models.price_rules_public import PriceRulesPublic
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    status: None | PriceRuleLifecycleStatusEnum | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    params: dict[str, Any] = {}

    params["skip"] = skip

    params["limit"] = limit

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, str):
        json_status = status
    else:
        json_status = status
    params["status"] = json_status


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/seller/promotions",
        "params": params,
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorResponse | HTTPValidationError | PriceRulesPublic | None:
    if response.status_code == 200:
        response_200 = PriceRulesPublic.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorResponse | HTTPValidationError | PriceRulesPublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    status: None | PriceRuleLifecycleStatusEnum | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | PriceRulesPublic]:
    """ List Promotions

     List seller's own promotions.

    Returns all promotion codes created by this seller.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        status (None | PriceRuleLifecycleStatusEnum | Unset): Filter by status
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | PriceRulesPublic]
     """


    kwargs = _get_kwargs(
        skip=skip,
limit=limit,
status=status,
x_role_id=x_role_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    status: None | PriceRuleLifecycleStatusEnum | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | PriceRulesPublic | None:
    """ List Promotions

     List seller's own promotions.

    Returns all promotion codes created by this seller.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        status (None | PriceRuleLifecycleStatusEnum | Unset): Filter by status
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | PriceRulesPublic
     """


    return sync_detailed(
        client=client,
skip=skip,
limit=limit,
status=status,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    status: None | PriceRuleLifecycleStatusEnum | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | PriceRulesPublic]:
    """ List Promotions

     List seller's own promotions.

    Returns all promotion codes created by this seller.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        status (None | PriceRuleLifecycleStatusEnum | Unset): Filter by status
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | PriceRulesPublic]
     """


    kwargs = _get_kwargs(
        skip=skip,
limit=limit,
status=status,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    status: None | PriceRuleLifecycleStatusEnum | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | PriceRulesPublic | None:
    """ List Promotions

     List seller's own promotions.

    Returns all promotion codes created by this seller.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        status (None | PriceRuleLifecycleStatusEnum | Unset): Filter by status
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | PriceRulesPublic
     """


    return (await asyncio_detailed(
        client=client,
skip=skip,
limit=limit,
status=status,
x_role_id=x_role_id,

    )).parsed
