"""`services show-test`, `show-test-results` and `list-tests` read the test
runs the platform records per service (unitysvc#2628), not ``meta.test``.

``show-test`` shows a document's latest run with its output — the rendered
script that executed, not the unrendered ``.j2`` template (#1268).
``show-test-results`` shows a service's verdict and runs, and one run's output.
``list-tests`` takes each document's status from the service's runs.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from unitysvc_sellers.cli import app as cli_app
from unitysvc_sellers.commands.tests import _doc_statuses
from unitysvc_sellers.exceptions import NotFoundError

DOC_ID = "6a7ce374-d3f4-43e4-981e-5538957e0cb3"
OTHER_DOC = "9b1c2d3e-0000-4000-8000-000000000001"
SERVICE_ID = "11111111-2222-4333-8444-555555555555"
IFACE = "4f983e90-5028-4d5d-936d-bc35d6da92ad"
RUN_ID = "aaaabbbb-cccc-4ddd-8eee-ffff00001111"
_TEMPLATE = "import smtplib\n{% if local_testing %}\nsmtp_host = '{{ host }}'\n{% endif %}\n"
_RENDERED = "import smtplib\nfrom urllib.parse import urlparse\nparsed = urlparse('smtp://gw:587')\n"


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "k")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", "http://test.local/v1")
    # Wide enough that rich does not elide the runs table's cells.
    monkeypatch.setenv("COLUMNS", "200")


def _doc(meta: dict | None = None) -> dict:
    return {
        "id": DOC_ID,
        "title": "Python code example",
        "category": "code_example",
        "mime_type": "python",
        "file_content": _TEMPLATE,
        "meta": meta or {},
    }


def _run(**over: object) -> dict:
    return {
        "id": RUN_ID,
        "document_id": DOC_ID,
        "document_title": "Python code example",
        "interface_id": IFACE,
        "channel_name": None,
        "status": "script_failed",
        "exit_code": 1,
        "executed_at": "2026-10-14T00:00:00Z",
        **over,
    }


def _client(
    *,
    doc: dict | None = None,
    latest: dict | Exception | None = None,
    results: dict | None = None,
    output: dict | None = None,
    detail: dict | None = None,
):
    async def _test_details(_doc_id, **_sel):
        if isinstance(latest, Exception):
            raise latest
        return latest

    documents = SimpleNamespace(get=AsyncMock(return_value=doc), test_details=_test_details)
    services = SimpleNamespace(
        test_results=AsyncMock(return_value=results),
        test_run_output=AsyncMock(return_value=output),
        get=AsyncMock(return_value=detail),
    )
    client = SimpleNamespace(documents=documents, services=services)

    class _Ctx:
        async def __aenter__(self):
            return client

        async def __aexit__(self, *exc):
            return False

    return lambda *a, **kw: _Ctx(), client


def _invoke(args: list[str], **client_kw):
    factory, client = _client(**client_kw)
    with (
        patch("unitysvc_sellers.commands.tests.async_client", factory),
        patch(
            "unitysvc_sellers.commands.services._resolve_single_target_id",
            lambda *a, **kw: SERVICE_ID,
        ),
    ):
        return CliRunner().invoke(cli_app, ["services", *args]), client


# --------------------------------------------------------------------------- show-test


def test_show_test_prints_the_latest_run_and_its_rendered_script() -> None:
    result, _ = _invoke(
        ["show-test", DOC_ID],
        doc=_doc(),
        latest={
            "status": "script_failed",
            "exit_code": 1,
            "executed_at": "2026-10-14T00:00:00Z",
            "stdout": "gateway said no",
            "stderr": "Traceback: boom",
            "env": {"SERVICE_BASE_URL": "http://gw/svc"},
            "rendered_script": _RENDERED,
            "expired": False,
        },
    )

    assert result.exit_code == 0, result.output
    assert "script_failed" in result.output
    assert "gateway said no" in result.output and "Traceback: boom" in result.output
    assert "urlparse('smtp://gw:587')" in result.output
    # The unrendered template is never shown as if it ran.
    assert "{% if local_testing %}" not in result.output


def test_show_test_without_a_recorded_run_is_pending() -> None:
    result, _ = _invoke(["show-test", DOC_ID], doc=_doc(), latest=NotFoundError("no run", status_code=404))

    assert result.exit_code == 0, result.output
    assert "pending" in result.output
    assert "No recorded run" in result.output


def test_show_test_reports_a_skipped_document() -> None:
    result, _ = _invoke(
        ["show-test", DOC_ID],
        doc=_doc({"test": {"status": "skip"}}),
        latest=NotFoundError("no run", status_code=404),
    )

    assert result.exit_code == 0, result.output
    assert "skip" in result.output


def test_show_test_says_when_output_expired() -> None:
    result, _ = _invoke(
        ["show-test", DOC_ID],
        doc=_doc(),
        latest={"status": "success", "exit_code": 0, "expired": True},
    )

    assert result.exit_code == 0, result.output
    assert "output expired" in result.output


# --------------------------------------------------------------------------- show-test-results


def _results(**over: object) -> dict:
    return {
        "service_id": SERVICE_ID,
        "platform_service_id": None,
        "platform_service_name": None,
        "passed": False,
        "error": "1 test(s) failed",
        "runs": [_run()],
        "not_run": [{"document_id": OTHER_DOC, "document_title": "Connectivity test", "reason": "missing"}],
        "skipped": [],
        **over,
    }


def test_show_test_results_lists_the_verdict_runs_and_gaps() -> None:
    result, client = _invoke(["show-test-results", "--id", SERVICE_ID], results=_results())

    assert result.exit_code == 0, result.output
    client.services.test_results.assert_awaited_once_with(SERVICE_ID)
    assert "1 test(s) failed" in result.output
    assert RUN_ID[:8] in result.output and "script_failed" in result.output
    assert "not run (missing)" in result.output and "Connectivity test" in result.output


def test_show_test_results_names_the_platform_service_for_a_member() -> None:
    result, _ = _invoke(
        ["show-test-results", "--id", SERVICE_ID],
        results=_results(platform_service_id="p", platform_service_name="labs/llm-fast", not_run=[]),
    )

    assert result.exit_code == 0, result.output
    assert "labs/llm-fast" in result.output


def test_show_test_results_prints_one_runs_output_by_prefix() -> None:
    result, client = _invoke(
        ["show-test-results", "--id", SERVICE_ID, "--run", RUN_ID[:8]],
        results=_results(),
        output={"status": "script_failed", "exit_code": 1, "stderr": "HTTP 429", "rendered_script": _RENDERED},
    )

    assert result.exit_code == 0, result.output
    client.services.test_run_output.assert_awaited_once_with(SERVICE_ID, RUN_ID)
    assert "HTTP 429" in result.output and "urlparse('smtp://gw:587')" in result.output


def test_show_platform_tests_is_an_alias() -> None:
    result, client = _invoke(["show-platform-tests", "--id", SERVICE_ID], results=_results())

    assert result.exit_code == 0, result.output
    client.services.test_results.assert_awaited_once_with(SERVICE_ID)


# --------------------------------------------------------------------------- list-tests


def test_doc_statuses_follow_the_runs_gaps_and_skips() -> None:
    statuses = _doc_statuses(
        {
            "runs": [
                _run(status="success"),
                _run(document_id=OTHER_DOC, status="success"),
                # An upstream probe is evidence, never a pass.
                _run(document_id="upstream-only", interface_id=None, status="success"),
            ],
            # A required run is still missing for OTHER_DOC.
            "not_run": [{"document_id": OTHER_DOC}],
            "skipped": [{"document_id": "skipped-doc"}],
        }
    )

    assert statuses == {
        DOC_ID: "success",
        OTHER_DOC: "pending",
        "upstream-only": "pending",
        "skipped-doc": "skip",
    }


def test_list_tests_takes_status_from_the_service_runs() -> None:
    result, _ = _invoke(
        ["list-tests", "--id", SERVICE_ID, "--format", "json"],
        detail={"id": SERVICE_ID, "name": "acme/svc", "documents": [_doc({"test": {"status": "success"}})]},
        results=_results(not_run=[]),
    )

    assert result.exit_code == 0, result.output
    # The run failed; a stale meta.test "success" is ignored.
    assert '"status": "script_failed"' in result.output
