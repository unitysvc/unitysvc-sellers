from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.secrets_public import SecretsPublic
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union



def _get_kwargs(
    *,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    params: dict[str, Any] = {}

    params["skip"] = skip

    params["limit"] = limit


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/secrets/",
        "params": params,
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[HTTPValidationError, SecretsPublic]]:
    if response.status_code == 200:
        response_200 = SecretsPublic.from_dict(response.json())



        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())



        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[HTTPValidationError, SecretsPublic]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[HTTPValidationError, SecretsPublic]]:
    """ List Secrets

     List the current seller's secrets.

    Returns secret metadata only — values are never returned.

    Args:
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SecretsPublic]]
     """


    kwargs = _get_kwargs(
        skip=skip,
limit=limit,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[HTTPValidationError, SecretsPublic]]:
    """ List Secrets

     List the current seller's secrets.

    Returns secret metadata only — values are never returned.

    Args:
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SecretsPublic]
     """


    return sync_detailed(
        client=client,
skip=skip,
limit=limit,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[HTTPValidationError, SecretsPublic]]:
    """ List Secrets

     List the current seller's secrets.

    Returns secret metadata only — values are never returned.

    Args:
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SecretsPublic]]
     """


    kwargs = _get_kwargs(
        skip=skip,
limit=limit,
authorization=authorization,
x_role_id=x_role_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[HTTPValidationError, SecretsPublic]]:
    """ List Secrets

     List the current seller's secrets.

    Returns secret metadata only — values are never returned.

    Args:
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SecretsPublic]
     """


    return (await asyncio_detailed(
        client=client,
skip=skip,
limit=limit,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
