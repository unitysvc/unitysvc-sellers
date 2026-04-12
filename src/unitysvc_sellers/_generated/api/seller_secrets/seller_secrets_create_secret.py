from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.secret_create import SecretCreate
from ...models.secret_public import SecretPublic
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union



def _get_kwargs(
    *,
    body: SecretCreate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/secrets/",
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[HTTPValidationError, SecretPublic]]:
    if response.status_code == 201:
        response_201 = SecretPublic.from_dict(response.json())



        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())



        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[HTTPValidationError, SecretPublic]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SecretCreate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[HTTPValidationError, SecretPublic]]:
    """ Create Secret

     Create a new secret for the current seller.

    The secret is encrypted and associated with the seller derived
    from the ``X-Role-Id`` header. **The value cannot be retrieved
    after creation** — store it securely before submitting.

    Args:
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (SecretCreate): Schema for creating a secret.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SecretPublic]]
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
    client: Union[AuthenticatedClient, Client],
    body: SecretCreate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[HTTPValidationError, SecretPublic]]:
    """ Create Secret

     Create a new secret for the current seller.

    The secret is encrypted and associated with the seller derived
    from the ``X-Role-Id`` header. **The value cannot be retrieved
    after creation** — store it securely before submitting.

    Args:
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (SecretCreate): Schema for creating a secret.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SecretPublic]
     """


    return sync_detailed(
        client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SecretCreate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Response[Union[HTTPValidationError, SecretPublic]]:
    """ Create Secret

     Create a new secret for the current seller.

    The secret is encrypted and associated with the seller derived
    from the ``X-Role-Id`` header. **The value cannot be retrieved
    after creation** — store it securely before submitting.

    Args:
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (SecretCreate): Schema for creating a secret.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SecretPublic]]
     """


    kwargs = _get_kwargs(
        body=body,
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
    body: SecretCreate,
    authorization: Union[None, Unset, str] = UNSET,
    x_role_id: Union[None, Unset, str] = UNSET,

) -> Optional[Union[HTTPValidationError, SecretPublic]]:
    """ Create Secret

     Create a new secret for the current seller.

    The secret is encrypted and associated with the seller derived
    from the ``X-Role-Id`` header. **The value cannot be retrieved
    after creation** — store it securely before submitting.

    Args:
        authorization (Union[None, Unset, str]):
        x_role_id (Union[None, Unset, str]):
        body (SecretCreate): Schema for creating a secret.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SecretPublic]
     """


    return (await asyncio_detailed(
        client=client,
body=body,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
