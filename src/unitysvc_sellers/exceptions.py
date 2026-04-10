"""Exception hierarchy for the seller SDK.

All errors raised by ``unitysvc_sellers`` are subclasses of
:class:`SellerSDKError`, which in turn is a subclass of ``Exception``.
This lets callers choose the granularity that fits their use case::

    try:
        client.services.list()
    except NotFoundError:
        ...
    except SellerSDKError:
        ...
"""

from __future__ import annotations

from typing import Any

__all__ = [
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


class SellerSDKError(Exception):
    """Base class for all errors raised by ``unitysvc_sellers``."""


class APIError(SellerSDKError):
    """The server returned a non-success status code.

    Attributes:
        status_code: HTTP status code.
        detail: Parsed error payload from the server (usually a dict
            matching ``ErrorResponse``), or the raw text if not JSON.
        response_body: Raw response bytes, useful for debugging.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        detail: Any = None,
        response_body: bytes | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail
        self.response_body = response_body


class AuthenticationError(APIError):
    """401 Unauthorized. The API key is missing, invalid, or expired."""


class PermissionError(APIError):  # noqa: A001 — shadow builtin is intentional
    """403 Forbidden. The authenticated seller cannot perform this action."""


class NotFoundError(APIError):
    """404 Not Found. The requested resource does not exist for this seller."""


class ValidationError(APIError):
    """400/422. The request body failed server-side validation.

    ``detail`` typically contains a list of per-field errors.
    """


class ConflictError(APIError):
    """409 Conflict. The request conflicts with server state (e.g. duplicate name)."""


class RateLimitError(APIError):
    """429 Too Many Requests. Retry after the backoff window."""


class ServerError(APIError):
    """5xx. The server encountered an error. Safe to retry idempotent requests."""


def error_for_status(
    status_code: int,
    *,
    detail: Any = None,
    response_body: bytes | None = None,
) -> APIError:
    """Map an HTTP status code to the most specific ``APIError`` subclass."""
    message = f"API request failed with status {status_code}"
    if isinstance(detail, dict) and detail.get("detail"):
        message = f"{message}: {detail['detail']}"

    mapping: dict[int, type[APIError]] = {
        400: ValidationError,
        401: AuthenticationError,
        403: PermissionError,
        404: NotFoundError,
        409: ConflictError,
        422: ValidationError,
        429: RateLimitError,
    }
    if 500 <= status_code < 600:
        cls: type[APIError] = ServerError
    else:
        cls = mapping.get(status_code, APIError)
    return cls(
        message,
        status_code=status_code,
        detail=detail,
        response_body=response_body,
    )
