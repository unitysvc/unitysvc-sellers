import datetime
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx
from dateutil.parser import isoparse

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.seller_cycle_earnings_response import SellerCycleEarningsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    cycle_start: datetime.date | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_cycle_start: None | str | Unset
    if isinstance(cycle_start, Unset):
        json_cycle_start = UNSET
    elif isinstance(cycle_start, datetime.date):
        json_cycle_start = cycle_start.isoformat()
    else:
        json_cycle_start = cycle_start
    params["cycle_start"] = json_cycle_start

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/usage/cycle",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SellerCycleEarningsResponse | None:
    if response.status_code == 200:
        response_200 = SellerCycleEarningsResponse.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | SellerCycleEarningsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    cycle_start: datetime.date | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SellerCycleEarningsResponse]:
    """Cycle-to-date earnings

     Per-service usage and earnings for the current billing cycle, and what the seller has earned so far.
    Sellers bill on the calendar month. Defaults to the cycle in progress; pass cycle_start to read an
    earlier one.

    Args:
        cycle_start (datetime.date | None | Unset): First day of the cycle to report. Defaults to
            the calendar month in progress. Any day in the target month is accepted.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SellerCycleEarningsResponse]
    """

    kwargs = _get_kwargs(
        cycle_start=cycle_start,
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
    cycle_start: datetime.date | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SellerCycleEarningsResponse | None:
    """Cycle-to-date earnings

     Per-service usage and earnings for the current billing cycle, and what the seller has earned so far.
    Sellers bill on the calendar month. Defaults to the cycle in progress; pass cycle_start to read an
    earlier one.

    Args:
        cycle_start (datetime.date | None | Unset): First day of the cycle to report. Defaults to
            the calendar month in progress. Any day in the target month is accepted.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SellerCycleEarningsResponse
    """

    return sync_detailed(
        client=client,
        cycle_start=cycle_start,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    cycle_start: datetime.date | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SellerCycleEarningsResponse]:
    """Cycle-to-date earnings

     Per-service usage and earnings for the current billing cycle, and what the seller has earned so far.
    Sellers bill on the calendar month. Defaults to the cycle in progress; pass cycle_start to read an
    earlier one.

    Args:
        cycle_start (datetime.date | None | Unset): First day of the cycle to report. Defaults to
            the calendar month in progress. Any day in the target month is accepted.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SellerCycleEarningsResponse]
    """

    kwargs = _get_kwargs(
        cycle_start=cycle_start,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    cycle_start: datetime.date | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | SellerCycleEarningsResponse | None:
    """Cycle-to-date earnings

     Per-service usage and earnings for the current billing cycle, and what the seller has earned so far.
    Sellers bill on the calendar month. Defaults to the cycle in progress; pass cycle_start to read an
    earlier one.

    Args:
        cycle_start (datetime.date | None | Unset): First day of the cycle to report. Defaults to
            the calendar month in progress. Any day in the target month is accepted.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SellerCycleEarningsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            cycle_start=cycle_start,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
