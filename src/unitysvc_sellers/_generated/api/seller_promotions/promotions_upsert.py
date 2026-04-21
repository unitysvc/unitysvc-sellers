from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.price_rule_public import PriceRulePublic
from ...models.seller_promotion_create import SellerPromotionCreate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: SellerPromotionCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/promotions",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | HTTPValidationError | PriceRulePublic | None:
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


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorResponse | HTTPValidationError | PriceRulePublic]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SellerPromotionCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | PriceRulePublic]:
    """Upsert Promotion

     Create or update a promotion by name (idempotent upsert).

    If a promotion with the same name exists for this seller, it is updated.
    Otherwise, a new promotion is created. This enables CLI-driven workflows
    where promotions are managed as files identified by name.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SellerPromotionCreate): Schema for sellers creating a promotion.

            Inherits all fields from PromotionData (unitysvc-core).
            The backend auto-sets source=seller_code and seller_id from
            the authenticated user, and decomposes scope into internal fields
            (code, requires_redemption, service_groups,
            PriceRuleServiceTarget) during ingestion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | PriceRulePublic]
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
    body: SellerPromotionCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | PriceRulePublic | None:
    """Upsert Promotion

     Create or update a promotion by name (idempotent upsert).

    If a promotion with the same name exists for this seller, it is updated.
    Otherwise, a new promotion is created. This enables CLI-driven workflows
    where promotions are managed as files identified by name.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SellerPromotionCreate): Schema for sellers creating a promotion.

            Inherits all fields from PromotionData (unitysvc-core).
            The backend auto-sets source=seller_code and seller_id from
            the authenticated user, and decomposes scope into internal fields
            (code, requires_redemption, service_groups,
            PriceRuleServiceTarget) during ingestion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | PriceRulePublic
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
    body: SellerPromotionCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[ErrorResponse | HTTPValidationError | PriceRulePublic]:
    """Upsert Promotion

     Create or update a promotion by name (idempotent upsert).

    If a promotion with the same name exists for this seller, it is updated.
    Otherwise, a new promotion is created. This enables CLI-driven workflows
    where promotions are managed as files identified by name.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SellerPromotionCreate): Schema for sellers creating a promotion.

            Inherits all fields from PromotionData (unitysvc-core).
            The backend auto-sets source=seller_code and seller_id from
            the authenticated user, and decomposes scope into internal fields
            (code, requires_redemption, service_groups,
            PriceRuleServiceTarget) during ingestion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | PriceRulePublic]
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
    body: SellerPromotionCreate,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> ErrorResponse | HTTPValidationError | PriceRulePublic | None:
    """Upsert Promotion

     Create or update a promotion by name (idempotent upsert).

    If a promotion with the same name exists for this seller, it is updated.
    Otherwise, a new promotion is created. This enables CLI-driven workflows
    where promotions are managed as files identified by name.

    Args:
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):
        body (SellerPromotionCreate): Schema for sellers creating a promotion.

            Inherits all fields from PromotionData (unitysvc-core).
            The backend auto-sets source=seller_code and seller_id from
            the authenticated user, and decomposes scope into internal fields
            (code, requires_redemption, service_groups,
            PriceRuleServiceTarget) during ingestion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | PriceRulePublic
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
