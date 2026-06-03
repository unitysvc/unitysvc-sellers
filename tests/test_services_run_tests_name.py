"""Tests for ``--name`` selector on ``usvc_seller services run-tests``.

Covers the dispatch contract — the mutex check, single-match
resolution, multi-match looping, and zero-match graceful exit. The
end-to-end CLI rendering and the SDK plumbing are tested elsewhere
(``test_services_local_ids.py`` and the SDK-side ``test_aclient.py``);
this module isolates the new ``--name`` selector.

The SDK methods (``client.services.list``, ``client.services.run_tests``)
are mocked at the boundary so we don't depend on the live diagnostics
endpoint shape — it's evolving, and the dispatch we care about is
agnostic to the result body.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
import respx as _respx  # noqa: F401  imported to ensure fixture stack matches CI
from typer.testing import CliRunner

from unitysvc_sellers.cli import app as cli_app

API_BASE = "http://test.local/v1"
SID_A = "11111111-1111-1111-1111-111111111111"
SID_B = "22222222-2222-2222-2222-222222222222"


def _diag_ok(success: int = 1) -> SimpleNamespace:
    """Minimal RunTestsResult-shaped object the CLI renderer accepts."""
    return SimpleNamespace(
        status="success",
        outcome="ok",
        results=[],
        success_count=success,
        fail_count=0,
        skipped_count=0,
    )


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "test-key")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", API_BASE)


# ---------------------------------------------------------------------------
# Mutex
# ---------------------------------------------------------------------------


def test_rejects_both_service_id_and_name(env):
    """``run-tests <sid> --name <pat>`` is an error — exactly one source."""
    runner = CliRunner()
    result = runner.invoke(
        cli_app,
        ["services", "run-tests", SID_A, "--name", "cohere/command-r-plus"],
    )
    assert result.exit_code == 1, result.output
    assert "exactly one" in result.output.lower()


def test_rejects_neither_service_id_nor_name(env):
    """``run-tests`` with no target is an error."""
    runner = CliRunner()
    result = runner.invoke(cli_app, ["services", "run-tests"])
    assert result.exit_code == 1, result.output
    assert "exactly one" in result.output.lower()


# ---------------------------------------------------------------------------
# --name resolution
# ---------------------------------------------------------------------------


def _mock_clients(*, list_returns, run_tests_returns):
    """Build a patched ``async_client`` factory whose returned client
    has the given ``services.list`` and ``services.run_tests`` mocks.
    """
    services = SimpleNamespace(
        list=AsyncMock(return_value=list_returns),
        run_tests=AsyncMock(side_effect=run_tests_returns),
    )
    client = SimpleNamespace(services=services)

    class _Ctx:
        async def __aenter__(self):
            return client

        async def __aexit__(self, *exc):
            return False

    return services, lambda *a, **kw: _Ctx()


def _services_page(rows: list[dict]) -> SimpleNamespace:
    """Shape matching what ``model_list`` consumes from ``client.services.list``."""
    return SimpleNamespace(
        data=rows,
        next_cursor=None,
        has_more=False,
        count=len(rows),
    )


def test_name_literal_resolves_one_service(env):
    """A literal --name resolves to one match → one run_tests call."""
    page = _services_page([{"id": SID_A, "name": "cohere/command-r-plus"}])
    services, factory = _mock_clients(
        list_returns=page,
        run_tests_returns=[_diag_ok()],
    )

    with patch("unitysvc_sellers.commands.tests.async_client", factory):
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["services", "run-tests", "--name", "cohere/command-r-plus"],
        )

    assert result.exit_code == 0, result.output
    services.run_tests.assert_awaited_once()
    args = services.run_tests.await_args
    assert args.args[0] == SID_A, args.args
    assert "Found 1 service(s) matching" in result.output


def test_name_pattern_resolves_multiple_services_and_loops(env):
    """``--name 'cohere/*'`` matches two → run_tests called per match, in order."""
    page = _services_page(
        [
            {"id": SID_A, "name": "cohere/command-r-plus"},
            {"id": SID_B, "name": "cohere/embed-v4.0"},
        ]
    )
    services, factory = _mock_clients(
        list_returns=page,
        run_tests_returns=[_diag_ok(), _diag_ok()],
    )

    with patch("unitysvc_sellers.commands.tests.async_client", factory):
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["services", "run-tests", "--name", "cohere/*"],
        )

    assert result.exit_code == 0, result.output
    assert services.run_tests.await_count == 2
    called_ids = [call.args[0] for call in services.run_tests.await_args_list]
    assert called_ids == [SID_A, SID_B]
    assert "Found 2 service(s) matching" in result.output
    # Each service gets its own labelled header in multi-target mode.
    assert "cohere/command-r-plus" in result.output
    assert "cohere/embed-v4.0" in result.output


def test_name_with_no_matches_exits_zero(env):
    """A pattern that matches nothing isn't a failure — exit 0, friendly note."""
    page = _services_page([])
    services, factory = _mock_clients(list_returns=page, run_tests_returns=[])

    with patch("unitysvc_sellers.commands.tests.async_client", factory):
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["services", "run-tests", "--name", "no-such-thing/*"],
        )

    assert result.exit_code == 0, result.output
    services.run_tests.assert_not_awaited()
    assert "No services match" in result.output
