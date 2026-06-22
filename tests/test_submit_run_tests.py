"""Tests for the ``run_tests`` control on submit (issue #115).

Submitting a service moves it ``draft|rejected → pending``. By default the
backend then runs the gateway diagnostic and flips the service to
``review`` / ``active`` / ``rejected``. ``run_tests=False`` skips the
diagnostic and parks the service at ``pending`` (routable) — the documented
path for on-wire testing of code examples.

Covers:
- SDK ``Service.submit(run_tests=...)`` builds the right PATCH body.
- CLI ``services submit`` exposes ``--run-tests/--no-run-tests`` (default on).
- CLI wiring: the flag reaches the PATCH body as ``run_tests``.
- ``withdraw`` / ``deprecate`` never send ``run_tests`` (it's submit-only).
"""

from __future__ import annotations

import inspect
import json
import uuid

import httpx
import pytest
import respx
from typer.testing import CliRunner

from unitysvc_sellers.cli import app as cli_app
from unitysvc_sellers.commands import services as services_cmd
from unitysvc_sellers.commands.services import submit_service
from unitysvc_sellers.services import Service

_BASE_URL = "https://seller.test.unitysvc"


# ---------------------------------------------------------------------------
# SDK: Service.submit(run_tests=...)
# ---------------------------------------------------------------------------


class _CapturingServices:
    """Stub of ``client.services`` that records the last update body."""

    def __init__(self) -> None:
        self.captured: tuple[str, dict] | None = None

    def update(self, service_id: str, body: dict) -> dict:
        self.captured = (str(service_id), body)
        return body


class _CapturingParent:
    def __init__(self) -> None:
        self.services = _CapturingServices()


class _Raw:
    id = "11111111-1111-1111-1111-111111111111"


def _proxy() -> tuple[Service, _CapturingParent]:
    parent = _CapturingParent()
    return Service(_Raw(), parent=parent), parent  # type: ignore[arg-type]


def test_sdk_submit_default_runs_tests() -> None:
    svc, parent = _proxy()
    svc.submit()
    assert parent.services.captured is not None
    _, body = parent.services.captured
    assert body == {"status": "pending", "run_tests": True}


def test_sdk_submit_no_run_tests() -> None:
    svc, parent = _proxy()
    svc.submit(run_tests=False)
    assert parent.services.captured is not None
    _, body = parent.services.captured
    assert body == {"status": "pending", "run_tests": False}


# ---------------------------------------------------------------------------
# CLI: surface lock
# ---------------------------------------------------------------------------


def test_cli_submit_exposes_run_tests_flag() -> None:
    """``submit`` carries a ``--run-tests/--no-run-tests`` boolean defaulting
    to tests-on (preserving the historical behaviour)."""
    opt = inspect.signature(submit_service).parameters["run_tests"].default
    decls = " ".join(opt.param_decls)
    assert "--run-tests" in decls
    assert "--no-run-tests" in decls
    assert opt.default is True


# ---------------------------------------------------------------------------
# CLI: the flag reaches the PATCH body
# ---------------------------------------------------------------------------


@pytest.fixture
def _runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "svcpass_test")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", _BASE_URL)


def _pin_resolution(monkeypatch: pytest.MonkeyPatch, sid: str) -> None:
    """Bypass id resolution so the test exercises only the status-change body."""
    monkeypatch.setattr(services_cmd, "_resolve_or_fetch_ids", lambda **_: [sid])


def _last_patch_body(sid: str) -> dict:
    patch_calls = [c for c in respx.calls if c.request.method == "PATCH" and str(sid) in str(c.request.url)]
    assert patch_calls, "expected a PATCH to the service"
    return json.loads(patch_calls[-1].request.content.decode())


@respx.mock
def test_cli_submit_default_sends_run_tests_true(
    monkeypatch: pytest.MonkeyPatch, _runner: CliRunner, _env: None
) -> None:
    sid = str(uuid.uuid4())
    _pin_resolution(monkeypatch, sid)
    respx.patch(f"{_BASE_URL}/services/{sid}").mock(return_value=httpx.Response(200, json={"id": sid}))

    result = _runner.invoke(cli_app, ["services", "submit", "--id", sid, "--yes"])

    assert result.exit_code == 0, result.stdout
    assert _last_patch_body(sid) == {"status": "pending", "run_tests": True}


@respx.mock
def test_cli_submit_no_run_tests_sends_false(
    monkeypatch: pytest.MonkeyPatch, _runner: CliRunner, _env: None
) -> None:
    sid = str(uuid.uuid4())
    _pin_resolution(monkeypatch, sid)
    respx.patch(f"{_BASE_URL}/services/{sid}").mock(return_value=httpx.Response(200, json={"id": sid}))

    result = _runner.invoke(cli_app, ["services", "submit", "--id", sid, "--no-run-tests", "--yes"])

    assert result.exit_code == 0, result.stdout
    assert _last_patch_body(sid) == {"status": "pending", "run_tests": False}


@respx.mock
def test_cli_withdraw_omits_run_tests(monkeypatch: pytest.MonkeyPatch, _runner: CliRunner, _env: None) -> None:
    """``run_tests`` is submit-only; ``withdraw`` (→ draft) must not send it."""
    sid = str(uuid.uuid4())
    _pin_resolution(monkeypatch, sid)
    respx.patch(f"{_BASE_URL}/services/{sid}").mock(return_value=httpx.Response(200, json={"id": sid}))

    result = _runner.invoke(cli_app, ["services", "withdraw", "--id", sid, "--yes"])

    assert result.exit_code == 0, result.stdout
    body = _last_patch_body(sid)
    assert body == {"status": "draft"}
    assert "run_tests" not in body
