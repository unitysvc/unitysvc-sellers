"""`services show-test` must display the rendered script that executed, not the
unrendered `.j2` template (#1268)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from unitysvc_sellers.cli import app as cli_app

DOC_ID = "6a7ce374-d3f4-43e4-981e-5538957e0cb3"
_TEMPLATE = "import smtplib\n{% if local_testing %}\nsmtp_host = '{{ host }}'\n{% endif %}\n"
_RENDERED = "import smtplib\nfrom urllib.parse import urlparse\nparsed = urlparse('smtp://gw:587')\n"


def _client_returning(doc: dict):
    documents = SimpleNamespace(get=AsyncMock(return_value=doc))
    client = SimpleNamespace(documents=documents)

    class _Ctx:
        async def __aenter__(self):
            return client

        async def __aexit__(self, *exc):
            return False

    return lambda *a, **kw: _Ctx()


def _invoke(doc: dict):
    with patch("unitysvc_sellers.commands.tests.async_client", _client_returning(doc)):
        return CliRunner().invoke(cli_app, ["services", "show-test", DOC_ID])


def _base_doc(test_block: dict) -> dict:
    return {
        "id": DOC_ID,
        "title": "Python code example",
        "category": "code_example",
        "mime_type": "python",
        "file_content": _TEMPLATE,
        "meta": {"test": test_block},
    }


def test_per_interface_rendered_script_is_shown(monkeypatch):
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "k")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", "http://test.local/v1")
    doc = _base_doc(
        {
            "status": "script_failed",
            "tests": {
                "4f983e90-5028-4d5d-936d-bc35d6da92ad": {
                    "name": "smtp_gateway",
                    "status": "script_failed",
                    "exit_code": 1,
                    "rendered_script": _RENDERED,
                }
            },
        }
    )
    result = _invoke(doc)
    assert result.exit_code == 0, result.output
    assert "rendered script (executed)" in result.output
    assert "urlparse('smtp://gw:587')" in result.output  # the rendered branch
    # The unrendered template is never displayed.
    assert "{% if local_testing %}" not in result.output


def test_single_doc_rendered_script_at_top_level(monkeypatch):
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "k")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", "http://test.local/v1")
    doc = _base_doc({"status": "success", "rendered_script": _RENDERED})
    result = _invoke(doc)
    assert result.exit_code == 0, result.output
    assert "rendered script (executed)" in result.output
    assert "{% if local_testing %}" not in result.output


def test_no_script_shown_when_never_executed(monkeypatch):
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "k")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", "http://test.local/v1")
    doc = _base_doc({"status": "pending"})  # never executed → no rendered script
    result = _invoke(doc)
    assert result.exit_code == 0, result.output
    assert "rendered script (executed)" not in result.output
    # No unrendered-template fallback either.
    assert "{% if local_testing %}" not in result.output
