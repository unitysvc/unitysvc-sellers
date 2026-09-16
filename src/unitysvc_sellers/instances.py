"""``client.instances`` — preview or render system templates into seller services.

``/v1/seller/instances`` renders a
platform-owned template into the normal service ingest pipeline. Template
parameters are recorded on the generated service's source metadata; there is no
separate backend ``TemplateInstance`` object to manage.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

import httpx

from ._http import unwrap
from .exceptions import error_for_status

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient


class Instances:
    """Manager for previewing and creating services from system templates."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def create(
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
        from ._generated.models.template_instantiation_create_response import (
            TemplateInstantiationCreateResponse,
        )

        body: dict[str, Any] = {
            "template_id": str(template_id),
            "parameters": parameters or {},
            "auto_submit": auto_submit,
        }
        if name is not None:
            body["name"] = name
        if service_id is not None:
            body["service_id"] = str(service_id)
        try:
            response = self._client.get_httpx_client().post("/instances", json=body)
        except httpx.HTTPError as exc:
            raise error_for_status(0, detail=str(exc)) from exc

        if 200 <= response.status_code < 300:
            return TemplateInstantiationCreateResponse.from_dict(response.json())
        try:
            detail: Any = response.json()
        except ValueError:
            detail = response.text
        raise error_for_status(response.status_code, detail=detail, response_body=response.content)

    def render(
        self,
        template_id: str | UUID,
        *,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Preview a system-template render without creating a service.

        The returned provider/offering/listing data is suitable for
        ``usvc seller specs expand`` inspection output. It does not enqueue an
        ingest task or create any platform records.
        """
        from ._generated.api.seller_instances import seller_instances_render_instance as op
        from ._generated.models.template_instantiation_render import TemplateInstantiationRender
        from ._generated.models.template_instantiation_render_parameters import (
            TemplateInstantiationRenderParameters,
        )

        body = TemplateInstantiationRender(
            template_id=UUID(str(template_id)),
            parameters=TemplateInstantiationRenderParameters.from_dict(parameters or {}),
        )
        return unwrap(op.sync_detailed(client=self._client, body=body)).to_dict()
