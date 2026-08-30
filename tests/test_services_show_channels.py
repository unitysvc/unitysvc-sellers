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
        "managed_by_template": "llm-fast",
        "offering": {
            "upstream_access_config": {
                "http_relay": {
                    "access_method": "http",
                    "type": "byok",
                    "customer_secrets_required": ["HTTP_RELAY_BASE_URL"],
                    "customer_secrets_optional": [{"name": "HTTP_RELAY_API_KEY", "default": ""}],
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
    assert "Template" in result.output
    assert "llm-fast" in result.output
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


def test_show_renders_platform_member_kind_and_facade(env):
    """A platform member reports its role and the facade it backs from the
    structured detail fields (#1979) — no text scraping."""
    detail = {
        "service_id": SID,
        "service_name": "crofai-deepseek-v3-2",
        "status": "active",
        "managed_by_template": None,
        "kind": "platform_member",
        "parent_id": "12345678-9abc-def0-1234-56789abcdef0",
        "parent_name": "llm-fast",
        "provider": {"name": "unitysvc-labs"},
        "offering": {"upstream_access_config": {}},
        "documents": [],
        "interfaces": [],
    }
    runner = CliRunner()
    with (
        patch(
            "unitysvc_sellers.commands.services._resolve_single_target_id",
            return_value=SID,
        ),
        patch("unitysvc_sellers.commands.services.async_client", _factory(detail)),
    ):
        result = runner.invoke(cli_app, ["services", "show", "--id", SID])

    assert result.exit_code == 0, result.output
    assert "Provider" in result.output
    assert "unitysvc-labs" in result.output
    assert "Kind" in result.output
    assert "platform_member" in result.output
    assert "Platform service" in result.output
    assert "llm-fast" in result.output


def test_show_platform_service_falls_back_to_parent_id_prefix(env):
    detail = {
        "service_id": SID,
        "service_name": "crofai-deepseek-v3-2",
        "status": "active",
        "kind": "platform_member",
        "parent_id": "12345678-9abc-def0-1234-56789abcdef0",
        "documents": [],
        "interfaces": [],
    }
    runner = CliRunner()
    with (
        patch(
            "unitysvc_sellers.commands.services._resolve_single_target_id",
            return_value=SID,
        ),
        patch("unitysvc_sellers.commands.services.async_client", _factory(detail)),
    ):
        result = runner.invoke(cli_app, ["services", "show", "--id", SID])

    assert result.exit_code == 0, result.output
    assert "Platform service" in result.output
    assert "12345678" in result.output


def test_show_regular_service_has_no_kind_row(env):
    detail = {
        "service_id": SID,
        "service_name": "plain-service",
        "status": "active",
        "kind": "regular",
        "documents": [],
        "interfaces": [],
    }
    runner = CliRunner()
    with (
        patch(
            "unitysvc_sellers.commands.services._resolve_single_target_id",
            return_value=SID,
        ),
        patch("unitysvc_sellers.commands.services.async_client", _factory(detail)),
    ):
        result = runner.invoke(cli_app, ["services", "show", "--id", SID])

    assert result.exit_code == 0, result.output
    assert "Kind" not in result.output
    assert "Platform service" not in result.output
