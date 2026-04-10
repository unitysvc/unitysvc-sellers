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
``seller_id`` is required. The default base URL points at the staging
environment (``https://seller.staging.unitysvc.com``); override with the
``base_url`` constructor argument or the ``UNITYSVC_BASE_URL`` env var.
"""

from .client import DEFAULT_BASE_URL, ENV_API_KEY, ENV_BASE_URL, Client
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

__author__ = """Bo Peng"""
__email__ = "bo.peng@unitysvc.com"

__all__ = [
    # Client
    "Client",
    "DEFAULT_BASE_URL",
    "ENV_API_KEY",
    "ENV_BASE_URL",
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
