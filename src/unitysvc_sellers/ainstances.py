"""``async_client.instances`` — async create-from-template ingestion.

Async mirror of :mod:`unitysvc_sellers.instances`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

import httpx

from .exceptions import error_for_status

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient


class AsyncInstances:
    """Async manager for create-from-template service ingestion."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def create(
        self,
        template_id: str | UUID,
        *,
        parameters: dict[str, Any] | None = None,
        name: str | None = None,
        auto_submit: bool = False,
        service_id: str | UUID | None = None,
    ) -> Any:
        """Create a service from ``template_id`` + ``parameters``.

        Renders the template into a **draft** service (the default, matching the
        backend's ``auto_submit=false``). Pass ``auto_submit=True`` to also submit
        that draft for review in the same call. Pass ``service_id`` to revise an
        existing service previously created from the same template. Returns the
        ingest ``task_id``.
        """
        from ._generated.models.template_instantiation_create import TemplateInstantiationCreate
        from ._generated.models.template_instantiation_create_parameters import (
            TemplateInstantiationCreateParameters,
        )
        from ._generated.models.template_instantiation_create_response import (
            TemplateInstantiationCreateResponse,
        )
        from ._generated.types import UNSET

        body = TemplateInstantiationCreate(
            template_id=UUID(str(template_id)),
            name=name if name is not None else UNSET,
            parameters=TemplateInstantiationCreateParameters.from_dict(parameters or {}),
            auto_submit=auto_submit,
            service_id=UUID(str(service_id)) if service_id is not None else UNSET,
        )
        try:
            response = await self._client.get_async_httpx_client().post("/instances", json=body.to_dict())
        except httpx.HTTPError as exc:
            raise error_for_status(0, detail=str(exc)) from exc

        if 200 <= response.status_code < 300:
            return TemplateInstantiationCreateResponse.from_dict(response.json())
        try:
            detail: Any = response.json()
        except ValueError:
            detail = response.text
        raise error_for_status(response.status_code, detail=detail, response_body=response.content)
