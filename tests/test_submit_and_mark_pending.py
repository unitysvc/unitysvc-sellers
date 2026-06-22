"""Tests for the split between ``services submit`` and ``services mark-pending``.

- ``submit`` → ``POST /services/{id}/submit`` (validate + set pending + run the
  activation test pipeline).
- ``mark-pending`` → ``PATCH /services/{id}`` ``status=pending`` (pure status
  change, no tests).

Covers the SDK (``Services.submit_for_review`` / ``Service.mark_pending``) and
the CLI wiring for both commands.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from unitysvc_sellers import Client
from unitysvc_sellers.cli import app as cli_app

_BASE_URL = "https://seller.test.unitysvc"
_SID = "11111111-1111-1111-1111-111111111111"


@pytest.fixture
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "svcpass_test")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", _BASE_URL)


# ---------------------------------------------------------------------------
# SDK
# ---------------------------------------------------------------------------


@respx.mock
def test_sdk_submit_for_review_posts_to_submit_endpoint() -> None:
    route = respx.post(f"{_BASE_URL}/services/{_SID}/submit").mock(
        return_value=httpx.Response(
            200, json={"id": _SID, "status": "pending", "message": "Service submitted for review"}
        )
    )
    client = Client(api_key="svcpass_test", base_url=_BASE_URL)
    resp = client.services.submit_for_review(_SID)

    assert route.called
    assert resp.status == "pending"
    assert resp.message == "Service submitted for review"


@respx.mock
def test_sdk_mark_pending_patches_status() -> None:
    """``Service.mark_pending`` is a plain PATCH status=pending — no /submit."""
    from unitysvc_sellers.services import Service

    patch_route = respx.patch(f"{_BASE_URL}/services/{_SID}").mock(
        return_value=httpx.Response(200, json={"id": _SID, "status": "pending"})
    )
    submit_route = respx.post(f"{_BASE_URL}/services/{_SID}/submit").mock(
        return_value=httpx.Response(200, json={"id": _SID})
    )

    client = Client(api_key="svcpass_test", base_url=_BASE_URL)
    # Build the proxy directly (skip the GET round-trip) — we only care that
    # mark_pending() issues the PATCH, not the submit POST.
    Service(SimpleNamespace(id=_SID), parent=client).mark_pending()

    assert patch_route.called
    body = patch_route.calls.last.request.content.decode()
    assert '"status"' in body and "pending" in body
    # mark_pending must NOT hit the submit (test-running) endpoint.
    assert not submit_route.called


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------


def _patched_client(**methods: AsyncMock):
    services = SimpleNamespace(**methods)
    client = SimpleNamespace(services=services)

    class _Ctx:
        async def __aenter__(self):
            return client

        async def __aexit__(self, *exc):
            return False

    return lambda *a, **kw: _Ctx()


def test_cli_submit_calls_submit_for_review(_env: None) -> None:
    submit_mock = AsyncMock(return_value=SimpleNamespace(status="pending", message="Service submitted for review"))
    get_mock = AsyncMock(return_value={"id": _SID})
    factory = _patched_client(submit_for_review=submit_mock, get=get_mock)

    with patch("unitysvc_sellers.commands.services.async_client", factory):
        result = CliRunner().invoke(cli_app, ["services", "submit", "--id", _SID, "--yes"])

    assert result.exit_code == 0, result.output
    submit_mock.assert_awaited_once()
    assert str(submit_mock.await_args.args[0]) == _SID


def test_cli_mark_pending_patches_status(_env: None) -> None:
    update_mock = AsyncMock(return_value=SimpleNamespace(status="pending"))
    get_mock = AsyncMock(return_value={"id": _SID})
    submit_mock = AsyncMock(return_value=SimpleNamespace(status="pending"))
    factory = _patched_client(update=update_mock, get=get_mock, submit_for_review=submit_mock)

    with patch("unitysvc_sellers.commands.services.async_client", factory):
        result = CliRunner().invoke(cli_app, ["services", "mark-pending", "--id", _SID, "--yes"])

    assert result.exit_code == 0, result.output
    update_mock.assert_awaited_once()
    assert update_mock.await_args.args[0] == _SID or str(update_mock.await_args.args[0]) == _SID
    assert update_mock.await_args.args[1] == {"status": "pending"}
    # mark-pending must not run the activation pipeline.
    submit_mock.assert_not_awaited()
