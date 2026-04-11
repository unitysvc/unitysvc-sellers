"""Internal helpers for translating generated-client responses into typed
results or :mod:`unitysvc_sellers.exceptions`.

Generated operations from ``openapi-python-client`` return either
``sync_detailed`` (which yields a ``Response`` wrapper around the parsed
body) or ``sync`` (which returns the parsed body or ``None``). The
hand-written facades in :mod:`unitysvc_sellers.resources` always call
``sync_detailed`` and pass the result through :func:`unwrap`, so callers
get either a populated typed model or one of the
:class:`~unitysvc_sellers.exceptions.SellerSDKError` subclasses.
"""

from __future__ import annotations

import json
from typing import Any, TypeVar

from .exceptions import APIError, error_for_status

T = TypeVar("T")


def unwrap(response: Any) -> Any:
    """Convert a generated ``Response[T]`` into ``T`` or raise.

    The generated ``Response`` is an attrs class with these attributes:

    * ``status_code: HTTPStatus``
    * ``content: bytes``
    * ``parsed: T | ErrorResponse | HTTPValidationError | None``

    A 2xx with a parsed body is the success path. A non-2xx (or a 2xx
    with no parsed body, which the generator returns when the operation
    is documented as 204 No Content) is mapped to an exception.
    """
    status = int(response.status_code)
    parsed = getattr(response, "parsed", None)

    if 200 <= status < 300:
        # 204 No Content style — successful but nothing to return.
        if parsed is None:
            return None

        # If the parsed object is one of the documented error shapes, the
        # generator handed us an error body even though the status looks
        # OK (rare, but possible). Treat it as success.
        return parsed

    # Try to extract a useful detail payload from the response body.
    detail: Any
    try:
        detail = json.loads(response.content.decode("utf-8")) if response.content else None
    except (UnicodeDecodeError, json.JSONDecodeError):
        detail = response.content

    raise error_for_status(status, detail=detail, response_body=response.content)


def reraise_httpx(exc: Exception) -> None:
    """Wrap an httpx-level error in :class:`APIError` if it isn't one already.

    Use inside ``except`` blocks::

        try:
            return unwrap(services_list.sync_detailed(client=self._client))
        except httpx.HTTPError as exc:
            reraise_httpx(exc)
    """
    if isinstance(exc, APIError):
        raise
    raise APIError(str(exc), status_code=0) from exc
