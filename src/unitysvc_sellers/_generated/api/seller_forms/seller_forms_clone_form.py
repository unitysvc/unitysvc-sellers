from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    form_id: str,
    *,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id

    params: dict[str, Any] = {}

    json_name: None | str | Unset
    if isinstance(name, Unset):
        json_name = UNSET
    else:
        json_name = name
    params["name"] = json_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/forms/{form_id}/clone".format(
            form_id=quote(str(form_id), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> HTTPValidationError | None:
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    form_id: str,
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError]:
    r"""Clone Form

     Clone a form (\"create another\") rebound to the current active version.

    The clone copies parameters but starts a fresh service lineage. It rebinds
    to the template family's current **active** version and re-validates the
    copied parameters against that version's schema — disabled when the family
    has no active version.

    Args:
        form_id (str):
        name (None | str | Unset): Label for the clone
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError]
    """

    kwargs = _get_kwargs(
        form_id=form_id,
        name=name,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    form_id: str,
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | None:
    r"""Clone Form

     Clone a form (\"create another\") rebound to the current active version.

    The clone copies parameters but starts a fresh service lineage. It rebinds
    to the template family's current **active** version and re-validates the
    copied parameters against that version's schema — disabled when the family
    has no active version.

    Args:
        form_id (str):
        name (None | str | Unset): Label for the clone
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError
    """

    return sync_detailed(
        form_id=form_id,
        client=client,
        name=name,
        authorization=authorization,
        x_role_id=x_role_id,
    ).parsed


async def asyncio_detailed(
    form_id: str,
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> Response[HTTPValidationError]:
    r"""Clone Form

     Clone a form (\"create another\") rebound to the current active version.

    The clone copies parameters but starts a fresh service lineage. It rebinds
    to the template family's current **active** version and re-validates the
    copied parameters against that version's schema — disabled when the family
    has no active version.

    Args:
        form_id (str):
        name (None | str | Unset): Label for the clone
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError]
    """

    kwargs = _get_kwargs(
        form_id=form_id,
        name=name,
        authorization=authorization,
        x_role_id=x_role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    form_id: str,
    *,
    client: AuthenticatedClient | Client,
    name: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,
) -> HTTPValidationError | None:
    r"""Clone Form

     Clone a form (\"create another\") rebound to the current active version.

    The clone copies parameters but starts a fresh service lineage. It rebinds
    to the template family's current **active** version and re-validates the
    copied parameters against that version's schema — disabled when the family
    has no active version.

    Args:
        form_id (str):
        name (None | str | Unset): Label for the clone
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError
    """

    return (
        await asyncio_detailed(
            form_id=form_id,
            client=client,
            name=name,
            authorization=authorization,
            x_role_id=x_role_id,
        )
    ).parsed
