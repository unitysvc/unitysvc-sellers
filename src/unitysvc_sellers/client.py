"""Public seller SDK client.

The :class:`Client` is a thin facade over the auto-generated low-level
client in :mod:`unitysvc_sellers._generated`. It exposes resource
namespaces (``services``, ``promotions``, ``groups``, ``documents``)
that map 1:1 to the seller-tagged backend routes.

Example::

    from unitysvc_sellers import Client

    client = Client(api_key="svcpass_...")
    services = client.services.list()
    for service in services.data:
        print(service.name)

    # Or read credentials from the environment
    client = Client.from_env()
    client.services.list()

The seller context is encoded entirely in the API key, so no explicit
``seller_id`` is required. The default base URL points at the
production seller subdomain::

    https://seller.unitysvc.com/v1

The SDK's generated paths are semantic resource paths
(``/services/{id}``, ``/documents/{id}``, …) without any ``/seller``
wrapper — the seller scope is carried by the subdomain and the API
key. A single SDK release therefore works against any deployment
layout without regeneration; point ``base_url`` at whatever prefix the
deployment uses::

    # Production (default)
    Client(base_url="https://seller.unitysvc.com/v1")

    # Staging (seller-scoped subdomain)
    Client(base_url="https://seller.staging.unitysvc.com/v1")

    # Local development against a running backend
    Client(base_url="http://localhost:8000/v1/seller")

Override via the ``base_url`` constructor argument or the
``UNITYSVC_SELLER_API_URL`` environment variable.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import httpx

from ._generated.client import AuthenticatedClient as _LowLevelClient

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from .resources.documents import DocumentsResource
    from .resources.groups import GroupsResource
    from .resources.promotions import PromotionsResource
    from .resources.secrets import SecretsResource
    from .resources.services import ServicesResource
    from .resources.tasks import TasksResource
    from .resources.upload import UploadResult

DEFAULT_SELLER_API_URL = "https://seller.unitysvc.com/v1"
ENV_SELLER_API_KEY = "UNITYSVC_SELLER_API_KEY"
ENV_SELLER_API_URL = "UNITYSVC_SELLER_API_URL"


class Client:
    """Synchronous seller SDK client.

    Args:
        api_key: A seller API key (``svcpass_...``). Encodes the seller
            context, so no separate ``seller_id`` is required.
        base_url: Override the default base URL. If not provided, falls
            back to the ``UNITYSVC_SELLER_API_URL`` environment variable, then
            to :data:`DEFAULT_SELLER_API_URL`.
        timeout: Per-request timeout in seconds. Default 30s.
        verify_ssl: Whether to verify TLS certificates. Default ``True``.
            Set to ``False`` only for local testing against a self-signed
            backend.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float | httpx.Timeout | None = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        resolved_base_url = base_url or os.environ.get(ENV_SELLER_API_URL) or DEFAULT_SELLER_API_URL

        if isinstance(timeout, (int, float)):
            timeout_obj = httpx.Timeout(float(timeout))
        else:
            timeout_obj = timeout  # type: ignore[assignment]

        self._client = _LowLevelClient(
            base_url=resolved_base_url,
            token=api_key,
            timeout=timeout_obj,
            verify_ssl=verify_ssl,
            raise_on_unexpected_status=False,
        )
        self._api_key = api_key
        self._base_url = resolved_base_url

        # Lazy resource initialization happens on first attribute access
        # via the cached properties below.
        self._services: ServicesResource | None = None
        self._promotions: PromotionsResource | None = None
        self._groups: GroupsResource | None = None
        self._documents: DocumentsResource | None = None
        self._tasks: TasksResource | None = None
        self._secrets: SecretsResource | None = None

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_env(cls, **kwargs: object) -> Client:
        """Construct a client from environment variables.

        Reads :data:`ENV_SELLER_API_KEY` (required) and :data:`ENV_SELLER_API_URL`
        (optional). Any extra keyword arguments are forwarded to the
        :class:`Client` constructor.
        """
        api_key = os.environ.get(ENV_SELLER_API_KEY)
        if not api_key:
            raise RuntimeError(
                f"Environment variable {ENV_SELLER_API_KEY} is not set. "
                f"Set it to a seller API key (svcpass_...) or pass api_key= explicitly."
            )
        return cls(api_key=api_key, **kwargs)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Resource namespaces (lazy)
    # ------------------------------------------------------------------
    @property
    def services(self) -> ServicesResource:
        if self._services is None:
            from .resources.services import ServicesResource

            self._services = ServicesResource(self._client)
        return self._services

    @property
    def promotions(self) -> PromotionsResource:
        if self._promotions is None:
            from .resources.promotions import PromotionsResource

            self._promotions = PromotionsResource(self._client)
        return self._promotions

    @property
    def groups(self) -> GroupsResource:
        if self._groups is None:
            from .resources.groups import GroupsResource

            self._groups = GroupsResource(self._client)
        return self._groups

    @property
    def documents(self) -> DocumentsResource:
        if self._documents is None:
            from .resources.documents import DocumentsResource

            self._documents = DocumentsResource(self._client)
        return self._documents

    @property
    def tasks(self) -> TasksResource:
        if self._tasks is None:
            from .resources.tasks import TasksResource

            self._tasks = TasksResource(self._client)
        return self._tasks

    @property
    def secrets(self) -> SecretsResource:
        if self._secrets is None:
            from .resources.secrets import SecretsResource

            self._secrets = SecretsResource(self._client)
        return self._secrets

    # ------------------------------------------------------------------
    # High-level catalog upload
    # ------------------------------------------------------------------
    def upload(
        self,
        data_dir: str | Path,
        *,
        dryrun: bool = False,
        upload_services: bool = True,
        upload_promotions: bool = True,
        upload_groups: bool = True,
        on_progress: Callable[[str, str, str, str], None] | None = None,
    ) -> UploadResult:
        """Upload an entire seller catalog directory.

        Thin wrapper around
        :func:`unitysvc_sellers.resources.upload.upload_directory`.
        See that function for argument and return-type docs.
        """
        from pathlib import Path as _Path

        from .resources.upload import upload_directory

        return upload_directory(
            self,
            _Path(str(data_dir)),
            dryrun=dryrun,
            upload_services=upload_services,
            upload_promotions=upload_promotions,
            upload_groups=upload_groups,
            on_progress=on_progress,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Close the underlying httpx client and release its connection pool."""
        # The generated client lazily creates an httpx.Client; close it if it exists.
        # Access the private attribute via the public method since the underlying
        # client object exposes the same name.
        try:
            self._client.get_httpx_client().close()
        except Exception:
            pass

    def __enter__(self) -> Client:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
