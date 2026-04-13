from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.price_rule_public import PriceRulePublic
from ...models.seller_promotion_update import SellerPromotionUpdate
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    promotion_id: UUID,
    *,
    body: SellerPromotionUpdate,
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
        "url": "/promotions/{promotion_id}".format(promotion_id=quote(str(promotion_id), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorResponse | HTTPValidationError | PriceRulePublic | None:
    if response.status_code == 200:
        response_200 = PriceRulePublic.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorResponse | HTTPValidationError | PriceRulePublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    promotion_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: SellerPromotionUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | PriceRulePublic]:
    r""" Update Promotion

     Update a promotion.

    Cannot change: code, source, seller_id.

    Status transitions are handled here via the ``status`` field in the
    request body. Valid transitions:

    - ``draft``/``paused`` -> ``active``: activate the promotion. Paused
      promotions go through ``resume_price_rule`` to clear pause metadata;
      draft promotions are updated directly.
    - ``active``/``scheduled`` -> ``paused``: pause the promotion via
      ``pause_price_rule`` (customers can no longer redeem).
    - Other target states fall through to a plain field update and are
      subject to the underlying CRUD layer's validation.

    Non-status fields (name, description, pricing, priority, service_groups)
    are updated in a single CRUD call before any status transition runs, so
    combining \"change pricing and pause\" in one call is well-defined.

    Args:
        promotion_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SellerPromotionUpdate): Schema for updating a seller promotion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | PriceRulePublic]
     """


    kwargs = _get_kwargs(
        promotion_id=promotion_id,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    promotion_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: SellerPromotionUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | PriceRulePublic | None:
    r""" Update Promotion

     Update a promotion.

    Cannot change: code, source, seller_id.

    Status transitions are handled here via the ``status`` field in the
    request body. Valid transitions:

    - ``draft``/``paused`` -> ``active``: activate the promotion. Paused
      promotions go through ``resume_price_rule`` to clear pause metadata;
      draft promotions are updated directly.
    - ``active``/``scheduled`` -> ``paused``: pause the promotion via
      ``pause_price_rule`` (customers can no longer redeem).
    - Other target states fall through to a plain field update and are
      subject to the underlying CRUD layer's validation.

    Non-status fields (name, description, pricing, priority, service_groups)
    are updated in a single CRUD call before any status transition runs, so
    combining \"change pricing and pause\" in one call is well-defined.

    Args:
        promotion_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SellerPromotionUpdate): Schema for updating a seller promotion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | PriceRulePublic
     """


    return sync_detailed(
        promotion_id=promotion_id,
client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    promotion_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: SellerPromotionUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | PriceRulePublic]:
    r""" Update Promotion

     Update a promotion.

    Cannot change: code, source, seller_id.

    Status transitions are handled here via the ``status`` field in the
    request body. Valid transitions:

    - ``draft``/``paused`` -> ``active``: activate the promotion. Paused
      promotions go through ``resume_price_rule`` to clear pause metadata;
      draft promotions are updated directly.
    - ``active``/``scheduled`` -> ``paused``: pause the promotion via
      ``pause_price_rule`` (customers can no longer redeem).
    - Other target states fall through to a plain field update and are
      subject to the underlying CRUD layer's validation.

    Non-status fields (name, description, pricing, priority, service_groups)
    are updated in a single CRUD call before any status transition runs, so
    combining \"change pricing and pause\" in one call is well-defined.

    Args:
        promotion_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SellerPromotionUpdate): Schema for updating a seller promotion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | PriceRulePublic]
     """


    kwargs = _get_kwargs(
        promotion_id=promotion_id,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    promotion_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: SellerPromotionUpdate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | PriceRulePublic | None:
    r""" Update Promotion

     Update a promotion.

    Cannot change: code, source, seller_id.

    Status transitions are handled here via the ``status`` field in the
    request body. Valid transitions:

    - ``draft``/``paused`` -> ``active``: activate the promotion. Paused
      promotions go through ``resume_price_rule`` to clear pause metadata;
      draft promotions are updated directly.
    - ``active``/``scheduled`` -> ``paused``: pause the promotion via
      ``pause_price_rule`` (customers can no longer redeem).
    - Other target states fall through to a plain field update and are
      subject to the underlying CRUD layer's validation.

    Non-status fields (name, description, pricing, priority, service_groups)
    are updated in a single CRUD call before any status transition runs, so
    combining \"change pricing and pause\" in one call is well-defined.

    Args:
        promotion_id (UUID):
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SellerPromotionUpdate): Schema for updating a seller promotion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | PriceRulePublic
     """


    return (await asyncio_detailed(
        promotion_id=promotion_id,
client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
