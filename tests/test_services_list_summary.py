"""Tests for the `services list` pagination summary line.

The list endpoint is keyset-paginated (`CursorPage`: data / next_cursor /
has_more) and has no total, so the only honest "are we done?" signal is
`has_more`. These tests pin the wording the CLI uses to surface it, and
drive the real command over a mocked backend to check it is actually
reached on each output path.
"""

from __future__ import annotations

import json

import httpx as _httpx
import pytest
import respx as _respx
from typer.testing import CliRunner

from unitysvc_sellers.cli import app as _cli_app
from unitysvc_sellers.commands.services import _pagination_summary

# Reuse the ServicePublic / CursorPage payload builders rather than keeping a
# second copy in sync with the response schema.
from .test_services_local_ids import _list_page as _page
from .test_services_local_ids import _public_payload

_BASE_URL = "https://seller.test.unitysvc"
_UUID_A = "11111111-1111-1111-1111-111111111111"
_UUID_B = "22222222-2222-2222-2222-222222222222"


@pytest.fixture
def _runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "svcpass_test")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", _BASE_URL)


def _payload(service_id: str, name: str) -> dict:
    return _public_payload(service_id, name=name, status="rejected")


class TestPaginationSummary:
    def test_more_available_names_the_cursor(self) -> None:
        summary = _pagination_summary(50, next_cursor="CURSOR123", has_more=True)
        assert "50 services displayed" in summary
        assert "--cursor CURSOR123" in summary

    def test_exhausted_says_no_more_items(self) -> None:
        summary = _pagination_summary(37, next_cursor=None, has_more=False)
        assert "37 services displayed" in summary
        assert "no more items" in summary
        assert "--cursor" not in summary

    def test_singular_count_is_not_pluralised(self) -> None:
        assert _pagination_summary(1, next_cursor=None, has_more=False).startswith("1 service displayed")

    def test_zero_is_pluralised(self) -> None:
        assert _pagination_summary(0, next_cursor=None, has_more=False).startswith("0 services displayed")

    def test_has_more_without_cursor_falls_back_to_all(self) -> None:
        # Defensive: the backend only omits next_cursor when the page is empty,
        # but a truncated list must never render "--cursor None".
        summary = _pagination_summary(50, next_cursor=None, has_more=True)
        assert "None" not in summary
        assert "--all" in summary
        assert "no more items" not in summary

    def test_rich_markup_is_balanced(self) -> None:
        # Unbalanced rich tags render literally and look like a bug.
        for summary in (
            _pagination_summary(50, next_cursor="C", has_more=True),
            _pagination_summary(3, next_cursor=None, has_more=False),
        ):
            assert summary.count("[dim]") == summary.count("[/dim]")
            assert summary.count("[bold]") == summary.count("[/bold]")


class TestListCommandPrintsSummary:
    """End-to-end over a mocked backend: the summary must actually be reached."""

    @_respx.mock
    def test_truncated_table_advertises_the_cursor(self, _runner: CliRunner, _env: None) -> None:
        _respx.get(f"{_BASE_URL}/services").mock(
            return_value=_httpx.Response(
                200,
                json=_page([_payload(_UUID_A, "alpha")], has_more=True, next_cursor="NEXT99"),
            )
        )

        result = _runner.invoke(
            _cli_app,
            ["services", "list", "--status", "rejected", "--fields", "id,name"],
        )

        assert result.exit_code == 0, result.stdout
        # Rich wraps at the runner's narrow terminal, so match on fragments.
        assert "1 service displayed" in result.stdout
        assert "NEXT99" in result.stdout

    @_respx.mock
    def test_exhausted_table_says_no_more_items(self, _runner: CliRunner, _env: None) -> None:
        _respx.get(f"{_BASE_URL}/services").mock(
            return_value=_httpx.Response(
                200,
                json=_page([_payload(_UUID_A, "alpha"), _payload(_UUID_B, "beta")]),
            )
        )

        result = _runner.invoke(
            _cli_app,
            ["services", "list", "--status", "rejected", "--fields", "id,name"],
        )

        assert result.exit_code == 0, result.stdout
        assert "2 services displayed" in result.stdout
        assert "no more items" in result.stdout

    @_respx.mock
    def test_json_stdout_stays_parseable(self, _runner: CliRunner, _env: None) -> None:
        """The summary must not land in stdout and corrupt `... -f json | jq`."""
        _respx.get(f"{_BASE_URL}/services").mock(
            return_value=_httpx.Response(
                200,
                json=_page([_payload(_UUID_A, "alpha")], has_more=True, next_cursor="NEXT99"),
            )
        )

        result = _runner.invoke(
            _cli_app,
            ["services", "list", "--status", "rejected", "--format", "json"],
        )

        assert result.exit_code == 0, result.stdout
        rendered = json.loads(result.stdout)
        assert [svc["name"] for svc in rendered] == ["alpha"]

    @_respx.mock
    def test_all_drains_pages_then_reports_complete(self, _runner: CliRunner, _env: None) -> None:
        pages = [
            _httpx.Response(200, json=_page([_payload(_UUID_A, "alpha")], has_more=True, next_cursor="P2")),
            _httpx.Response(200, json=_page([_payload(_UUID_B, "beta")])),
        ]
        _respx.get(f"{_BASE_URL}/services").mock(side_effect=pages)

        result = _runner.invoke(
            _cli_app,
            ["services", "list", "--status", "rejected", "--all", "--fields", "id,name"],
        )

        assert result.exit_code == 0, result.stdout
        assert "2 services displayed" in result.stdout
        assert "no more items" in result.stdout
