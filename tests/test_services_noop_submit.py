"""Tests for the no-op-submit silencer in ``services submit``.

Covers:

- ``_is_noop_status_change`` recognizes the specific backend 400s that
  mean "this status change is a no-op" (catalog already matches
  desired state) and ignores unrelated 400s / wrong status codes.
- ``_bulk_status_change`` treats those 400s as ``skipped`` rather than
  ``failed``, so CI re-runs that find nothing to do exit zero.

The end-to-end ``services submit`` CLI path is covered by
``test_services_local_ids.py``; this file targets the new branching
in isolation so a future tweak to the bulk-helper UX can't silently
re-introduce the CI-flap that motivated this change.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from unitysvc_sellers.commands.services import (
    _bulk_status_change,
    _is_noop_status_change,
)
from unitysvc_sellers.exceptions import APIError

API_BASE = "http://test.local/v1"
SID_A = "11111111-1111-1111-1111-111111111111"
SID_B = "22222222-2222-2222-2222-222222222222"


# ---------------------------------------------------------------------------
# _is_noop_status_change
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "message",
    [
        # Real text from backend services.py:834 (duplicate active service).
        "API request failed with status 400: A service with identical "
        "content already exists: d7c429fa-cb73-4efb-8260-d74e75659fce "
        "(status: active). Please modify the service data before submitting.",
        # Real text from services.py:831 (no-changes-on-revision path).
        "API request failed with status 400: No changes detected. Please "
        "modify the service before submitting for review.",
    ],
)
def test_is_noop_recognizes_known_phrases(message: str) -> None:
    exc = APIError(message, status_code=400)
    assert _is_noop_status_change(exc) is True


def test_is_noop_rejects_unrelated_400() -> None:
    exc = APIError(
        "API request failed with status 400: Cannot change status from "
        "'active'. Contact admin for assistance.",
        status_code=400,
    )
    assert _is_noop_status_change(exc) is False


def test_is_noop_rejects_non_400_even_with_phrase() -> None:
    # Defensive: if some future endpoint surfaces the same wording at
    # 500 we don't want to silently swallow that.
    exc = APIError(
        "A service with identical content already exists in cache",
        status_code=500,
    )
    assert _is_noop_status_change(exc) is False


def test_is_noop_matches_phrase_when_no_status_code() -> None:
    # Some wrapper paths raise plain ``Exception`` without a
    # ``status_code`` attribute; phrase match alone is enough there.
    exc = Exception(
        "wrapped: API request failed with status 400: A service with "
        "identical content already exists ..."
    )
    assert _is_noop_status_change(exc) is True


# ---------------------------------------------------------------------------
# _bulk_status_change behavior on no-op 400
# ---------------------------------------------------------------------------


def _noop_400_response() -> httpx.Response:
    return httpx.Response(
        400,
        json={
            "detail": (
                f"A service with identical content already exists: {SID_B} "
                "(status: active). Please modify the service data before "
                "submitting."
            )
        },
    )


def _real_400_response() -> httpx.Response:
    return httpx.Response(
        400,
        json={"detail": "Cannot change status from 'active'."},
    )


def _success_response() -> httpx.Response:
    return httpx.Response(
        200,
        json={"id": SID_A, "status": "pending"},
    )


def test_bulk_status_change_counts_noop_as_skipped_and_exits_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A run where every PATCH returns the no-op 400 must not raise
    ``typer.Exit`` — CI needs to stay green on identical re-runs.
    """
    with respx.mock(base_url=API_BASE, assert_all_called=True) as mock:
        mock.patch(f"/services/{SID_A}").mock(return_value=_noop_400_response())
        # Should NOT raise typer.Exit.
        _bulk_status_change(
            api_key="test-key",
            base_url=API_BASE,
            service_ids=[SID_A],
            status="pending",
            success_verb="Submitted",
            confirm_prompt="ignored",
            yes=True,
        )

    out = capsys.readouterr().out
    assert "skipped" in out.lower()
    assert "no-op" in out.lower()
    # Critical: no failure line for a noop-only run.
    assert "Failed" not in out


def test_bulk_status_change_still_exits_one_on_real_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An unrelated 400 must still count as a failure and exit non-zero
    — this is the regression guard for the silencer ever growing too
    permissive.
    """
    import typer

    with respx.mock(base_url=API_BASE, assert_all_called=True) as mock:
        mock.patch(f"/services/{SID_A}").mock(return_value=_success_response())
        mock.patch(f"/services/{SID_B}").mock(return_value=_real_400_response())

        with pytest.raises(typer.Exit) as exc_info:
            _bulk_status_change(
                api_key="test-key",
                base_url=API_BASE,
                service_ids=[SID_A, SID_B],
                status="pending",
                success_verb="Submitted",
                confirm_prompt="ignored",
                yes=True,
            )

    assert exc_info.value.exit_code == 1
    out = capsys.readouterr().out
    assert "Failed" in out


def test_bulk_status_change_mixed_outcomes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Mixed success + skip (no failures) — must still exit zero and
    surface the skip line so the operator can see what was no-op'd.
    """
    with respx.mock(base_url=API_BASE, assert_all_called=True) as mock:
        mock.patch(f"/services/{SID_A}").mock(return_value=_success_response())
        mock.patch(f"/services/{SID_B}").mock(return_value=_noop_400_response())

        _bulk_status_change(
            api_key="test-key",
            base_url=API_BASE,
            service_ids=[SID_A, SID_B],
            status="pending",
            success_verb="Submitted",
            confirm_prompt="ignored",
            yes=True,
        )

    out = capsys.readouterr().out
    assert "Success" in out and "1/2" in out
    assert "Skipped" in out and "1/2" in out
    assert "Failed" not in out
