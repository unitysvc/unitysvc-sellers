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


def _client_returning(doc: dict, details: dict | None = None):
    """Fake client. ``details`` maps ``(interface_id, channel, upstream)``
    selector tuples to test-details responses; a missing selector (or
    ``details=None``, the pre-#1901 backend) raises, which the CLI treats
    as "fall back to the inline meta fields"."""

    async def _test_details(_doc_id, **sel):
        key = (sel.get("interface_id"), sel.get("channel"), bool(sel.get("upstream")))
        if details is None or key not in details:
            raise RuntimeError("no details endpoint")
        return details[key]

    documents = SimpleNamespace(get=AsyncMock(return_value=doc), test_details=_test_details)
    client = SimpleNamespace(documents=documents)

    class _Ctx:
        async def __aenter__(self):
            return client

        async def __aexit__(self, *exc):
            return False

    return lambda *a, **kw: _Ctx()


def _invoke(doc: dict, details: dict | None = None):
    with patch(
        "unitysvc_sellers.commands.tests.async_client",
        _client_returning(doc, details),
    ):
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


IFACE = "4f983e90-5028-4d5d-936d-bc35d6da92ad"


def test_streams_come_from_the_details_endpoint(monkeypatch):
    """Post-#1901 the meta cell carries only the record; stdout and the
    rendered script arrive from GET /documents/{id}/test-details."""
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "k")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", "http://test.local/v1")
    doc = _base_doc(
        {
            "status": "script_failed",
            "tests": {
                IFACE: {
                    "name": "smtp_gateway",
                    "status": "script_failed",
                    "exit_code": 1,
                    "detail_key": "tests/" + "0" * 64 + ".json",
                }
            },
        }
    )
    details = {
        (IFACE, None, False): {
            "source": "blob",
            "expired": False,
            "stdout": "BLOB-STDOUT-MARKER",
            "rendered_script": _RENDERED,
        }
    }
    result = _invoke(doc, details)
    assert result.exit_code == 0, result.output
    assert "BLOB-STDOUT-MARKER" in result.output
    assert "rendered script (executed)" in result.output
    assert "urlparse('smtp://gw:587')" in result.output


def test_expired_details_show_hint_and_keep_the_record(monkeypatch):
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "k")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", "http://test.local/v1")
    doc = _base_doc(
        {
            "status": "script_failed",
            "tests": {
                IFACE: {
                    "name": "smtp_gateway",
                    "status": "script_failed",
                    "exit_code": 1,
                    "detail_key": "tests/" + "0" * 64 + ".json",
                }
            },
        }
    )
    details = {(IFACE, None, False): {"expired": True}}
    result = _invoke(doc, details)
    assert result.exit_code == 0, result.output
    assert "details expired" in result.output
    assert "run-tests --force" in result.output
    # The recorded outcome still prints even though the streams are gone.
    assert "script_failed" in result.output


def test_older_backend_without_endpoint_falls_back_to_inline(monkeypatch):
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "k")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", "http://test.local/v1")
    doc = _base_doc(
        {
            "status": "script_failed",
            "tests": {
                IFACE: {
                    "name": "smtp_gateway",
                    "status": "script_failed",
                    "stdout": "INLINE-STDOUT-MARKER",
                }
            },
        }
    )
    result = _invoke(doc, details=None)  # every details call raises
    assert result.exit_code == 0, result.output
    assert "INLINE-STDOUT-MARKER" in result.output
    assert "details expired" not in result.output


def test_already_passed_and_last_attempt_are_surfaced(monkeypatch):
    """Sticky pass (unitysvc#1902): an inherited pass says so, and a later
    transient failure shows as last_attempt without demoting the pass."""
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "k")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", "http://test.local/v1")
    doc = _base_doc(
        {
            "status": "success",
            "tests": {
                IFACE: {
                    "name": "provider_api",
                    "status": "success",
                    "outcome": "already_passed",
                    "last_attempt": {
                        "status": "script_failed",
                        "error": "HTTP 429: rate limited",
                    },
                }
            },
        }
    )
    result = _invoke(doc)
    assert result.exit_code == 0, result.output
    # Rich wraps at terminal width, so compare against whitespace-normalized
    # output rather than raw lines.
    flat_output = " ".join(result.output.split())
    assert "passed earlier" in flat_output
    assert "last attempt: script_failed" in flat_output
    assert "429" in flat_output
    assert "earned pass retained" in flat_output
