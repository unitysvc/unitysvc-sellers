"""Bulk service commands label each line with the service name, not just an id.

``submit`` / ``enable-testing`` / ``set-visibility`` / ``delete`` all print one
line per service. Keyed on the uuid alone those lines say nothing about *what*
moved, so each id is resolved to its ``service_name`` first. Labelling is
cosmetic: when the lookup fails the command must still run and report bare ids.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from unitysvc_sellers.cli import app as cli_app
from unitysvc_sellers.commands import services as svc_mod

_BASE_URL = "https://seller.test.unitysvc"
_SID = "11111111-1111-1111-1111-111111111111"
_NAME = "cohere/command-r"


@pytest.fixture
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "svcpass_test")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", _BASE_URL)


def _patched_client(**methods):
    client = SimpleNamespace(services=SimpleNamespace(**methods))

    class _Ctx:
        async def __aenter__(self):
            return client

        async def __aexit__(self, *exc):
            return False

    return lambda *a, **kw: _Ctx()


def test_submit_line_names_the_service(_env: None) -> None:
    submit_mock = AsyncMock(return_value=SimpleNamespace(status="pending", message="submitted"))
    list_mock = AsyncMock(return_value=SimpleNamespace(data=[{"id": _SID, "name": _NAME}]))
    factory = _patched_client(submit_for_review=submit_mock, get=AsyncMock(return_value={"id": _SID}), list=list_mock)

    with patch("unitysvc_sellers.commands.services.async_client", factory):
        result = CliRunner().invoke(cli_app, ["services", "submit", "--id", _SID, "--yes"])

    assert result.exit_code == 0, result.output
    assert _NAME in result.output
    # The short id stays for disambiguation (a service and its pending
    # revision share a name), but the full uuid no longer carries the line.
    assert _SID[:8] in result.output


def test_labels_fall_back_to_the_id_when_names_are_unavailable(_env: None) -> None:
    """A failing name lookup must not fail the operation it decorates."""
    submit_mock = AsyncMock(return_value=SimpleNamespace(status="pending", message="submitted"))
    list_mock = AsyncMock(side_effect=RuntimeError("backend down"))
    factory = _patched_client(submit_for_review=submit_mock, get=AsyncMock(return_value={"id": _SID}), list=list_mock)

    with patch("unitysvc_sellers.commands.services.async_client", factory):
        result = CliRunner().invoke(cli_app, ["services", "submit", "--id", _SID, "--yes"])

    assert result.exit_code == 0, result.output
    submit_mock.assert_awaited_once()
    assert _SID in result.output


def test_fetch_service_names_ignores_unusable_ids() -> None:
    """Non-uuid ids never reach the API — the lookup just yields no labels."""
    assert svc_mod._fetch_service_names(None, _BASE_URL, ["not-a-uuid"]) == {}


def test_label_formats() -> None:
    names = {_SID: _NAME}
    assert svc_mod._label(_SID, names) == f"{_NAME} [dim]({_SID[:8]})[/dim]"
    assert svc_mod._plain_label(_SID, names) == f"{_NAME} ({_SID[:8]})"
    # Unknown id -> unchanged behaviour.
    assert svc_mod._label("other", names) == "other"
    assert svc_mod._plain_label("other", names) == "other"
