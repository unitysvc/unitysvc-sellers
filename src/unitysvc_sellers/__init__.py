"""UnitySVC Sellers — seller-facing tools for UnitySVC.

This package provides:

- The :class:`Client` HTTP SDK targeting the seller-tagged
  ``/v1/seller/*`` endpoints (services, promotions, groups, documents).
- The ``usvc_seller`` CLI with ``usvc_seller data *`` commands for
  organizing local seller catalogs (validate, format, populate, show,
  list, run test scripts) and ``usvc_seller data upload`` for pushing
  a catalog to the backend.

Quick start::

    from unitysvc_sellers import Client

    client = Client(api_key="svcpass_...")
    services = client.services.list()
    for s in services.data:
        print(s.name)

The seller context is encoded entirely in the API key, so no separate
``seller_id`` is required. The default base URL points at production
(``https://seller.unitysvc.com``); override with the ``base_url``
constructor argument or the ``UNITYSVC_SELLER_API_URL`` env var.
"""

from ._spec_version import SPEC_SHA256, SPEC_VERSION
from .aclient import AsyncClient
from .client import DEFAULT_SELLER_API_URL, ENV_SELLER_API_KEY, ENV_SELLER_API_URL, Client
from .exceptions import (
    APIError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    SellerSDKError,
    ServerError,
    ValidationError,
)
from .storage import upload_file

__author__ = """Bo Peng"""
__email__ = "bo.peng@unitysvc.com"

__all__ = [
    # Client
    "Client",
    "AsyncClient",
    # Storage
    "upload_file",
    "DEFAULT_SELLER_API_URL",
    "ENV_SELLER_API_KEY",
    "ENV_SELLER_API_URL",
    # Spec fingerprint
    "SPEC_SHA256",
    "SPEC_VERSION",
    # Exceptions
    "SellerSDKError",
    "APIError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
]
