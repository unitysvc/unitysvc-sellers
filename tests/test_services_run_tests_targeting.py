"""Single-document targeting on ``usvc_seller services run-tests``.

Covers the three selectors:
- ``--document-id`` accepting a full UUID or an 8+ char prefix (resolved via
  ``documents.get`` the way ``show-test`` does),
- ``--test-file`` selecting a document by filename per service, and
- ``--category`` restricting to one document category server-side (no id
  lookup needed) — added so a post-deploy smoke test can ask for just
  ``connectivity_test`` without a doc-id-resolution round trip.

The SDK boundary (``client.services.get/run_tests``, ``client.documents.get``)
is mocked; we assert which document id / category is dispatched.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from unitysvc_sellers.cli import app as cli_app

API_BASE = "http://test.local/v1"
SID = "11111111-1111-1111-1111-111111111111"
DOC_FULL = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
DOC_OTHER = "99999999-8888-7777-6666-555555555555"


def _diag_ok() -> SimpleNamespace:
    return SimpleNamespace(
        status="success",
        outcome="ok",
        results=[],
        success_count=1,
        fail_count=0,
        skipped_count=0,
    )


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "test-key")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", API_BASE)


def _factory(*, service_detail=None, doc_get=None):
    services = SimpleNamespace(
        get=AsyncMock(return_value=service_detail or {}),
        run_tests=AsyncMock(return_value=_diag_ok()),
        list=AsyncMock(return_value=SimpleNamespace(data=[], next_cursor=None, has_more=False, count=0)),
    )
    documents = SimpleNamespace(get=AsyncMock(return_value=doc_get or {}))
    client = SimpleNamespace(services=services, documents=documents)

    class _Ctx:
        async def __aenter__(self):
            return client

        async def __aexit__(self, *exc):
            return False

    return services, documents, lambda *a, **kw: _Ctx()


def test_document_id_and_test_file_mutually_exclusive(env):
    result = CliRunner().invoke(
        cli_app,
        ["services", "run-tests", "--id", SID, "-d", "aaaaaaaa", "-t", "x.py.j2"],
    )
    assert result.exit_code == 1, result.output
    assert "mutually exclusive" in result.output.lower()


def test_document_id_short_prefix_rejected(env):
    result = CliRunner().invoke(cli_app, ["services", "run-tests", "--id", SID, "-d", "short"])
    assert result.exit_code == 1, result.output
    assert "at least 8" in result.output.lower()


def test_document_id_prefix_resolved_to_full_uuid(env):
    services, documents, factory = _factory(doc_get={"id": DOC_FULL})
    with patch("unitysvc_sellers.commands.tests.async_client", factory):
        result = CliRunner().invoke(cli_app, ["services", "run-tests", "--id", SID, "-d", "aaaaaaaa"])
    assert result.exit_code == 0, result.output
    documents.get.assert_awaited_once_with("aaaaaaaa")
    services.run_tests.assert_awaited_once()
    assert services.run_tests.await_args.kwargs["document_id"] == DOC_FULL


def test_test_file_resolves_doc_id_by_filename(env):
    detail = {
        "documents": [
            {"id": DOC_FULL, "filename": "anthropic-to-openai-code-example.py.j2"},
            {"id": DOC_OTHER, "filename": "code-example.sh.j2"},
        ]
    }
    services, documents, factory = _factory(service_detail=detail)
    with patch("unitysvc_sellers.commands.tests.async_client", factory):
        result = CliRunner().invoke(
            cli_app,
            ["services", "run-tests", "--id", SID, "-t", "anthropic-to-openai-code-example.py.j2"],
        )
    assert result.exit_code == 0, result.output
    services.run_tests.assert_awaited_once()
    assert services.run_tests.await_args.kwargs["document_id"] == DOC_FULL


def test_test_file_no_match_errors(env):
    detail = {"documents": [{"id": DOC_FULL, "filename": "code-example.sh.j2"}]}
    services, documents, factory = _factory(service_detail=detail)
    with patch("unitysvc_sellers.commands.tests.async_client", factory):
        result = CliRunner().invoke(cli_app, ["services", "run-tests", "--id", SID, "-t", "nope.py.j2"])
    assert result.exit_code != 0, result.output
    services.run_tests.assert_not_awaited()


def test_test_file_ambiguous_match_errors(env):
    detail = {
        "documents": [
            {"id": DOC_FULL, "filename": "a-code-example.py.j2"},
            {"id": DOC_OTHER, "filename": "b-code-example.py.j2"},
        ]
    }
    services, documents, factory = _factory(service_detail=detail)
    with patch("unitysvc_sellers.commands.tests.async_client", factory):
        # 'code-example.py.j2' is a suffix of both filenames → ambiguous.
        result = CliRunner().invoke(cli_app, ["services", "run-tests", "--id", SID, "-t", "code-example.py.j2"])
    assert result.exit_code != 0, result.output
    services.run_tests.assert_not_awaited()


def test_category_dispatched_without_doc_lookup(env):
    """``--category`` skips the document-resolution round trip entirely —
    it's a server-side filter, not a client-side id lookup like -d/-t."""
    services, documents, factory = _factory()
    with patch("unitysvc_sellers.commands.tests.async_client", factory):
        result = CliRunner().invoke(
            cli_app, ["services", "run-tests", "--id", SID, "--category", "connectivity_test"]
        )
    assert result.exit_code == 0, result.output
    documents.get.assert_not_awaited()
    services.run_tests.assert_awaited_once()
    assert services.run_tests.await_args.kwargs["category"] == "connectivity_test"
    assert services.run_tests.await_args.kwargs["document_id"] is None


def test_category_invalid_value_rejected(env):
    result = CliRunner().invoke(
        cli_app, ["services", "run-tests", "--id", SID, "--category", "logo"]
    )
    assert result.exit_code == 1, result.output
    assert "connectivity_test" in result.output
    assert "code_example" in result.output


@pytest.mark.parametrize("other_flag", [["-d", "aaaaaaaa"], ["-t", "x.py.j2"]])
def test_category_mutually_exclusive_with_document_selectors(env, other_flag):
    result = CliRunner().invoke(
        cli_app,
        ["services", "run-tests", "--id", SID, "--category", "connectivity_test", *other_flag],
    )
    assert result.exit_code == 1, result.output
    assert "mutually exclusive" in result.output.lower()
