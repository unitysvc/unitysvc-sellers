"""Tests for ``usvc_seller platform-services list`` / ``show``.

These are the offline commands (no backend). ``instantiate`` needs a live
backend with system templates and is exercised by integration coverage.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from unitysvc_sellers.commands.platform_services import app

runner = CliRunner()


@pytest.fixture
def params_repo(tmp_path: Path) -> Path:
    """A repo with new and legacy member files, one with a sidecar."""
    platform = tmp_path / "platform_services" / "llm-fast" / "crofai"
    platform.mkdir(parents=True)
    (platform / "deepseek-v3.2.json").write_text(
        json.dumps(
            {
                "template": "llm-fast",
                "parameters": {
                    "api_base_url": "https://api.crofai.com/v1",
                    "api_key_secret": "CROFAI_API_KEY",
                    "model": "deepseek-v3.2",
                    "service_name": "crofai-deepseek-v3-2",
                },
            }
        )
        + "\n"
    )
    (platform / "deepseek-v3.2.service.json").write_text(
        json.dumps({"service_id": "def12345-0000-0000-0000-000000000000"}) + "\n"
    )

    acme = tmp_path / "params" / "acme"
    acme.mkdir(parents=True)
    (acme / "gpt.json").write_text(
        json.dumps(
            {
                "template": "openai-compatible-llm",
                "parameters": {"api_base_url": "https://acme.ai/v1", "input_price": 1.0},
            }
        )
        + "\n"
    )
    (acme / "gpt.service.json").write_text(json.dumps({"service_id": "abc12345-0000-0000-0000-000000000000"}) + "\n")
    (acme / "gpt2.json").write_text(
        json.dumps({"template": "openai-compatible-llm", "parameters": {"api_base_url": "https://acme.ai/v2"}}) + "\n"
    )
    return tmp_path


def test_list_shows_all_param_files(params_repo: Path) -> None:
    result = runner.invoke(app, ["list", "-d", str(params_repo)])
    assert result.exit_code == 0, result.output
    assert "llm-fast/crofai/deepseek-v3.2" in result.output
    assert "acme/gpt" in result.output
    assert "acme/gpt2" in result.output
    assert "llm-fast" in result.output
    assert "openai-compatible-llm" in result.output
    # the sidecar service_id surfaces (truncated)
    assert "def12345" in result.output
    assert "abc12345" in result.output


def test_list_json_and_name_filter(params_repo: Path) -> None:
    result = runner.invoke(app, ["list", "llm-fast/%", "-d", str(params_repo), "-f", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert [e["service_name"] for e in payload] == ["llm-fast/crofai/deepseek-v3.2"]
    assert payload[0]["template"] == "llm-fast"
    assert payload[0]["service_id"] == "def12345-0000-0000-0000-000000000000"
    assert "path" not in payload[0]


def test_list_still_supports_legacy_params_filter(params_repo: Path) -> None:
    result = runner.invoke(app, ["list", "acme/gpt2", "-d", str(params_repo), "-f", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert [e["service_name"] for e in payload] == ["acme/gpt2"]
    assert payload[0]["service_id"] is None
    assert "path" not in payload[0]


def test_list_empty_when_no_member_files(tmp_path: Path) -> None:
    result = runner.invoke(app, ["list", "-d", str(tmp_path)])
    assert result.exit_code == 0
    assert "No platform-service member files" in result.output


def test_show_one_param(params_repo: Path) -> None:
    result = runner.invoke(app, ["show", "llm-fast/crofai/deepseek-v3.2", "-d", str(params_repo)])
    assert result.exit_code == 0, result.output
    assert "llm-fast" in result.output
    assert "def12345-0000-0000-0000-000000000000" in result.output
    assert "api_base_url" in result.output


def test_show_json(params_repo: Path) -> None:
    result = runner.invoke(app, ["show", "acme/gpt2", "-d", str(params_repo), "-f", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["service_name"] == "acme/gpt2"
    assert payload["template"] == "openai-compatible-llm"
    assert payload["service_id"] is None


def test_show_missing_errors(params_repo: Path) -> None:
    result = runner.invoke(app, ["show", "acme/nope", "-d", str(params_repo)])
    assert result.exit_code == 1
    assert "No platform-service member file" in result.output


def test_instantiate_has_single_submit_flag_default_off() -> None:
    """``platform-services instantiate`` uses a single ``--submit`` flag, default off
    (draft), mirroring the backend's ``auto_submit=false`` — no ``--no-submit``."""
    import inspect

    from unitysvc_sellers.commands.platform_services import instantiate

    opt = inspect.signature(instantiate).parameters["submit"].default
    assert opt.default is False
    assert "--submit" in opt.param_decls
    assert "--no-submit" not in " ".join(opt.param_decls)
