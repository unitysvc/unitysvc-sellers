"""``client.instances`` — **deprecated** alias for the from-template methods.

The endpoint moved to ``POST /v1/seller/services/from-template`` (unitysvc#2386):
there was never an "instance" resource to manage — rendering a platform-owned
template is simply the second constructor for a service, and template parameters
are recorded on the generated service's source metadata.

Use :attr:`Client.services` instead::

    client.services.create_from_template(template_id, parameters={...})
    client.services.render_from_template(template_id, parameters={...})

This shim delegates to those and will be removed in 0.5.0.
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any
from uuid import UUID

if TYPE_CHECKING:
    from ._generated.models.service_upload_response import ServiceUploadResponse
    from .services import Services

_MOVED = (
    "client.instances is deprecated and will be removed in 0.5.0; the endpoint "
    "moved to POST /services/from-template. Use client.services.{new} instead."
)


class Instances:
    """Deprecated manager; delegates to :class:`~unitysvc_sellers.services.Services`."""

    def __init__(self, services: Services) -> None:
        self._services = services

    def create(
        self,
        template_id: str | UUID,
        *,
        parameters: dict[str, Any] | None = None,
        name: str | None = None,
        auto_submit: bool = False,
        service_id: str | UUID | None = None,
    ) -> ServiceUploadResponse:
        """Deprecated. Use ``client.services.create_from_template``."""
        warnings.warn(
            _MOVED.format(new="create_from_template"), DeprecationWarning, stacklevel=2
        )
        return self._services.create_from_template(
            template_id,
            parameters=parameters,
            name=name,
            auto_submit=auto_submit,
            service_id=service_id,
        )

    def render(
        self,
        template_id: str | UUID,
        *,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Deprecated. Use ``client.services.render_from_template``."""
        warnings.warn(
            _MOVED.format(new="render_from_template"), DeprecationWarning, stacklevel=2
        )
        return self._services.render_from_template(template_id, parameters=parameters)
