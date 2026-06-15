"""Tests for ``usvc_seller params list`` / ``show`` over the ``params/`` folder.

These are the offline commands (no backend). ``instantiate`` needs a live
backend with system templates and is exercised by integration coverage.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from unitysvc_sellers.commands.params import app

runner = CliRunner()


@pytest.fixture
def params_repo(tmp_path: Path) -> Path:
    """A repo with a ``params/`` folder: two param files, one with a sidecar."""
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
    assert "acme/gpt" in result.output
    assert "acme/gpt2" in result.output
    assert "openai-compatible-llm" in result.output
    # the sidecar service_id surfaces (truncated)
    assert "abc12345" in result.output


def test_list_json_and_name_filter(params_repo: Path) -> None:
    result = runner.invoke(app, ["list", "acme/gpt2", "-d", str(params_repo), "-f", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert [e["service_name"] for e in payload] == ["acme/gpt2"]
    assert payload[0]["service_id"] is None
    assert "path" not in payload[0]


def test_list_empty_when_no_params_folder(tmp_path: Path) -> None:
    result = runner.invoke(app, ["list", "-d", str(tmp_path)])
    assert result.exit_code == 0
    assert "No param files" in result.output


def test_show_one_param(params_repo: Path) -> None:
    result = runner.invoke(app, ["show", "acme/gpt", "-d", str(params_repo)])
    assert result.exit_code == 0, result.output
    assert "openai-compatible-llm" in result.output
    assert "abc12345-0000-0000-0000-000000000000" in result.output
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
    assert "No param file" in result.output
