"""Opt-in gate for experimental SDK/CLI features (unitysvc#1540).

The backend ships not-production-ready features (e.g. the async order-based S3
delivery model) behind its own ``EXPERIMENTAL`` deployment flag — they 404 on
production and only route on staging. The SDK carries the generated code for
those endpoints, but hides the high-level accessors and CLI commands unless the
user opts in with ``UNITYSVC_EXPERIMENTAL`` AND points at a deployment that
serves them (staging).

    export UNITYSVC_EXPERIMENTAL=1
"""

from __future__ import annotations

import os

from .exceptions import ExperimentalDisabledError

_TRUTHY = {"1", "true", "yes", "on"}


def experimental_enabled() -> bool:
    """True when ``UNITYSVC_EXPERIMENTAL`` is set to a truthy value."""
    return os.environ.get("UNITYSVC_EXPERIMENTAL", "").strip().lower() in _TRUTHY


def require_experimental(feature: str = "This feature") -> None:
    """Raise :class:`ExperimentalDisabledError` unless experimental is enabled.

    Call at the top of an experimental SDK method so a caller gets a clear,
    actionable error instead of a confusing 404 from production.
    """
    if not experimental_enabled():
        raise ExperimentalDisabledError(
            f"{feature} is experimental and not enabled. Set "
            "UNITYSVC_EXPERIMENTAL=1 and use a deployment that serves it "
            "(e.g. staging)."
        )
