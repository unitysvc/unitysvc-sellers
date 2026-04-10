from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.service_delete_response import ServiceDeleteResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    service_id: str,
    *,
    dryrun: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    if not isinstance(x_role_id, Unset):
        headers["x-role-id"] = x_role_id



    

    params: dict[str, Any] = {}

    params["dryrun"] = dryrun


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/seller/services/{service_id}".format(service_id=quote(str(service_id), safe=""),),
        "params": params,
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorResponse | HTTPValidationError | ServiceDeleteResponse | None:
    if response.status_code == 200:
        response_200 = ServiceDeleteResponse.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorResponse | HTTPValidationError | ServiceDeleteResponse]:
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
    dryrun: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | ServiceDeleteResponse]:
    r""" Delete Service

     Delete a service that has never been active.

    A service can only be deleted if:
    1. It belongs to the current seller.
    2. It has never been active (no archived history in ServiceData).
       Services that have been active are kept for audit trail.

    When ``dryrun=true``, the deletion is not performed — only the
    eligibility check runs and the result is returned in the response
    without raising. Use this to drive a proactive \"disable delete button\"
    UX in a dashboard, or to bulk-check a set of services before issuing
    the real deletes.

    When ``dryrun=false`` (default) and the service cannot be deleted,
    a 400 is raised with the reason.

    Cleanup of dependent records (access interfaces, enrollments, group
    memberships, recurrent requests, revisions) is handled by
    ``crud_service.delete_service``. The associated content entities
    (Provider, Offering, Listing) are content-addressed and may be shared,
    so they are not deleted.

    Supports partial ID matching on service_id (minimum 8 characters).

    Args:
        service_id (str):
        dryrun (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceDeleteResponse]
     """


    kwargs = _get_kwargs(
        service_id=service_id,
dryrun=dryrun,
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
    dryrun: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | ServiceDeleteResponse | None:
    r""" Delete Service

     Delete a service that has never been active.

    A service can only be deleted if:
    1. It belongs to the current seller.
    2. It has never been active (no archived history in ServiceData).
       Services that have been active are kept for audit trail.

    When ``dryrun=true``, the deletion is not performed — only the
    eligibility check runs and the result is returned in the response
    without raising. Use this to drive a proactive \"disable delete button\"
    UX in a dashboard, or to bulk-check a set of services before issuing
    the real deletes.

    When ``dryrun=false`` (default) and the service cannot be deleted,
    a 400 is raised with the reason.

    Cleanup of dependent records (access interfaces, enrollments, group
    memberships, recurrent requests, revisions) is handled by
    ``crud_service.delete_service``. The associated content entities
    (Provider, Offering, Listing) are content-addressed and may be shared,
    so they are not deleted.

    Supports partial ID matching on service_id (minimum 8 characters).

    Args:
        service_id (str):
        dryrun (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceDeleteResponse
     """


    return sync_detailed(
        service_id=service_id,
client=client,
dryrun=dryrun,
authorization=authorization,
x_role_id=x_role_id,

    ).parsed

async def asyncio_detailed(
    service_id: str,
    *,
    client: AuthenticatedClient | Client,
    dryrun: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> Response[ErrorResponse | HTTPValidationError | ServiceDeleteResponse]:
    r""" Delete Service

     Delete a service that has never been active.

    A service can only be deleted if:
    1. It belongs to the current seller.
    2. It has never been active (no archived history in ServiceData).
       Services that have been active are kept for audit trail.

    When ``dryrun=true``, the deletion is not performed — only the
    eligibility check runs and the result is returned in the response
    without raising. Use this to drive a proactive \"disable delete button\"
    UX in a dashboard, or to bulk-check a set of services before issuing
    the real deletes.

    When ``dryrun=false`` (default) and the service cannot be deleted,
    a 400 is raised with the reason.

    Cleanup of dependent records (access interfaces, enrollments, group
    memberships, recurrent requests, revisions) is handled by
    ``crud_service.delete_service``. The associated content entities
    (Provider, Offering, Listing) are content-addressed and may be shared,
    so they are not deleted.

    Supports partial ID matching on service_id (minimum 8 characters).

    Args:
        service_id (str):
        dryrun (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | HTTPValidationError | ServiceDeleteResponse]
     """


    kwargs = _get_kwargs(
        service_id=service_id,
dryrun=dryrun,
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
    dryrun: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    x_role_id: None | str | Unset = UNSET,

) -> ErrorResponse | HTTPValidationError | ServiceDeleteResponse | None:
    r""" Delete Service

     Delete a service that has never been active.

    A service can only be deleted if:
    1. It belongs to the current seller.
    2. It has never been active (no archived history in ServiceData).
       Services that have been active are kept for audit trail.

    When ``dryrun=true``, the deletion is not performed — only the
    eligibility check runs and the result is returned in the response
    without raising. Use this to drive a proactive \"disable delete button\"
    UX in a dashboard, or to bulk-check a set of services before issuing
    the real deletes.

    When ``dryrun=false`` (default) and the service cannot be deleted,
    a 400 is raised with the reason.

    Cleanup of dependent records (access interfaces, enrollments, group
    memberships, recurrent requests, revisions) is handled by
    ``crud_service.delete_service``. The associated content entities
    (Provider, Offering, Listing) are content-addressed and may be shared,
    so they are not deleted.

    Supports partial ID matching on service_id (minimum 8 characters).

    Args:
        service_id (str):
        dryrun (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        x_role_id (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | HTTPValidationError | ServiceDeleteResponse
     """


    return (await asyncio_detailed(
        service_id=service_id,
client=client,
dryrun=dryrun,
authorization=authorization,
x_role_id=x_role_id,

    )).parsed
