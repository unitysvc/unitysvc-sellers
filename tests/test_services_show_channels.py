"""``usvc_seller services show`` renders the upstream channels (#1281/#1297).

The offering's ``upstream_access_config`` carries one entry per upstream
access channel with the per-channel ``type`` + customer secrets stamped at
ingest (#1305).  ``show`` must surface the channel *names* and types — they
were previously invisible (only the user-facing access interfaces showed).
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from unitysvc_sellers.cli import app as cli_app

SID = "198eaef8-d924-4df2-801c-f3fb7c0bc9f5"


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "test-key")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", "http://test.local/v1")


def _detail() -> dict:
    return {
        "service_id": SID,
        "service_name": "http-relay",
        "status": "active",
        "offering": {
            "upstream_access_config": {
                "http_relay": {
                    "access_method": "http",
                    "type": "byok",
                    "customer_secrets_required": ["HTTP_RELAY_BASE_URL"],
                    "customer_secrets_optional": [
                        {"name": "HTTP_RELAY_API_KEY", "default": ""}
                    ],
                },
                "plus": {
                    "access_method": "http",
                    "type": "enrollable",
                },
            }
        },
        "documents": [],
        "interfaces": [],
    }


def _factory(detail: dict):
    client = SimpleNamespace(
        services=SimpleNamespace(get=_AsyncReturn(detail)),
    )

    class _Ctx:
        async def __aenter__(self):
            return client

        async def __aexit__(self, *exc):
            return False

    return lambda *a, **kw: _Ctx()


class _AsyncReturn:
    def __init__(self, value):
        self._value = value

    async def __call__(self, *a, **kw):
        return self._value


def test_show_renders_upstream_channels(env):
    runner = CliRunner()
    with (
        patch(
            "unitysvc_sellers.commands.services._resolve_single_target_id",
            return_value=SID,
        ),
        patch("unitysvc_sellers.commands.services.async_client", _factory(_detail())),
    ):
        result = runner.invoke(cli_app, ["services", "show", "--id", SID])

    assert result.exit_code == 0, result.output
    assert "Upstream Channels (2)" in result.output
    # Channel names + their classified types are surfaced.
    assert "http_relay" in result.output
    assert "byok" in result.output
    assert "plus" in result.output
    assert "enrollable" in result.output
    # The enrollable channel is flagged as the enrollment channel.
    assert "enrollment channel" in result.output
    # Per-channel customer secrets are listed.
    assert "HTTP_RELAY_BASE_URL" in result.output
    assert "HTTP_RELAY_API_KEY" in result.output
