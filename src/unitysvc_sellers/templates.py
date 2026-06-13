"""``client.templates`` — platform service templates a seller can instantiate.

Wraps the seller-tagged ``/v1/seller/templates`` listing operations plus the
one-shot ``/v1/seller/forms/instantiate`` (template + parameters → a submitted
service). ``list`` / ``get`` expose the active platform templates and their
parameter schemas; ``instantiate`` creates the backing form and dispatches the
service to the publish pipeline, returning ``form_id`` + ``task_id``.

See the platform's curated templates (e.g. an OpenAI-compatible LLM endpoint):
``client.templates.instantiate(template_id, parameters={...})`` is the
SDK/CLI counterpart of the dashboard's *Create from template* flow.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient


class Templates:
    """Manager for platform service templates (seller-facing, read + instantiate)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        service_type: Any | None = None,
    ) -> Any:
        """List the active templates this seller can instantiate."""
        from ._generated.api.seller_templates import (
            seller_templates_list_seller_templates as op,
        )
        from ._generated.types import UNSET

        return unwrap(
            op.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
                service_type=service_type if service_type is not None else UNSET,
            )
        )

    def get(self, template_id: str | UUID) -> Any:
        """Fetch one template's metadata + parameter schema."""
        from ._generated.api.seller_templates import (
            seller_templates_get_seller_template as op,
        )

        return unwrap(op.sync_detailed(str(template_id), client=self._client))

    def instantiate(
        self,
        template_id: str | UUID,
        *,
        parameters: dict[str, Any] | None = None,
        name: str | None = None,
    ) -> Any:
        """Create a service from ``template_id`` + ``parameters`` in one call.

        Renders the template, creates the backing form, and submits to the
        publish pipeline. Returns a record with ``form_id`` and ``task_id``.
        """
        from ._generated.api.seller_forms import seller_forms_instantiate_form as op
        from ._generated.models.parameters import Parameters
        from ._generated.models.service_form_create import ServiceFormCreate
        from ._generated.types import UNSET

        body = ServiceFormCreate(
            template_id=UUID(str(template_id)),
            name=name if name is not None else UNSET,
            parameters=Parameters.from_dict(parameters or {}),
        )
        return unwrap(op.sync_detailed(client=self._client, body=body))
