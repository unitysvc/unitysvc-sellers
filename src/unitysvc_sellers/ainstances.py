"""``async_client.instances`` — **deprecated** alias.

Async mirror of :mod:`unitysvc_sellers.instances`. Use
``async_client.services.create_from_template`` /
``async_client.services.render_from_template`` instead; this shim is removed in
0.5.0. See unitysvc#2386.
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any
from uuid import UUID

from .instances import _MOVED

if TYPE_CHECKING:
    from ._generated.models.service_upload_response import ServiceUploadResponse
    from .aservices import AsyncServices


class AsyncInstances:
    """Deprecated manager; delegates to :class:`~unitysvc_sellers.aservices.AsyncServices`."""

    def __init__(self, services: AsyncServices) -> None:
        self._services = services

    async def create(
        self,
        template_id: str | UUID,
        *,
        parameters: dict[str, Any] | None = None,
        name: str | None = None,
        auto_submit: bool = False,
        service_id: str | UUID | None = None,
    ) -> ServiceUploadResponse:
        """Deprecated. Use ``async_client.services.create_from_template``."""
        warnings.warn(
            _MOVED.format(new="create_from_template"), DeprecationWarning, stacklevel=2
        )
        return await self._services.create_from_template(
            template_id,
            parameters=parameters,
            name=name,
            auto_submit=auto_submit,
            service_id=service_id,
        )

    async def render(
        self,
        template_id: str | UUID,
        *,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Deprecated. Use ``async_client.services.render_from_template``."""
        warnings.warn(
            _MOVED.format(new="render_from_template"), DeprecationWarning, stacklevel=2
        )
        return await self._services.render_from_template(template_id, parameters=parameters)
