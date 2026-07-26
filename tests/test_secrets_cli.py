"""Tests for ``usvc_seller secrets upload`` and its ``.env``-style manifest parser.

The parser and dry-run path are fully offline. The actual upload loop is
covered by monkeypatching ``async_client`` so no backend is required.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
import typer
from typer.testing import CliRunner

from unitysvc_sellers.commands.secrets import (
    _parse_secrets_text,
    _read_secrets_source,
    app,
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# parser — (name, value, description) triples
# ---------------------------------------------------------------------------
def test_parse_extracts_values_and_descriptions() -> None:
    text = """
    # file header, attaches to nothing

    # the webhook base url
    export DISCORD_WEBHOOK_BASE="https://mock.unitysvc.dev/x"
    DISCORD_WEBHOOK_ID='demo'
    """
    assert _parse_secrets_text(text, environ={}) == [
        ("DISCORD_WEBHOOK_BASE", "https://mock.unitysvc.dev/x", "the webhook base url"),
        ("DISCORD_WEBHOOK_ID", "demo", None),
    ]


def test_parse_multiline_description_and_header_separation() -> None:
    text = "# header\n\n# line 1\n# line 2\nFOO=bar\n"
    assert _parse_secrets_text(text, environ={}) == [("FOO", "bar", "line 1\nline 2")]


def test_parse_resolves_env_expansion() -> None:
    text = "# base\nBASE_URL=${BASE_URL:-https://default.example.com}\n# key\nAPI_KEY=${API_KEY:-}\n"
    # env value wins when set; unset falls back to the default (here empty).
    assert _parse_secrets_text(text, environ={"BASE_URL": "https://real.example.com"}) == [
        ("BASE_URL", "https://real.example.com", "base"),
        ("API_KEY", "", "key"),
    ]


def test_parse_env_default_used_when_unset() -> None:
    text = "X=${X:-fallback}\n"
    assert _parse_secrets_text(text, environ={}) == [("X", "fallback", None)]


def test_parse_last_assignment_wins_and_keeps_position() -> None:
    assert _parse_secrets_text("A=1\nB=2\nA=3\n", environ={}) == [
        ("A", "3", None),
        ("B", "2", None),
    ]


def test_parse_skips_invalid_names_and_non_assignments() -> None:
    text = "1BAD=x\nnot an assignment\nGOOD=ok\n"
    assert _parse_secrets_text(text, environ={}) == [("GOOD", "ok", None)]


def test_parse_preserves_empty_values() -> None:
    assert _parse_secrets_text("OPT=\nREQ=v\n", environ={}) == [
        ("OPT", "", None),
        ("REQ", "v", None),
    ]


def test_parse_does_not_strip_inner_hash() -> None:
    assert _parse_secrets_text('TOK="a#b"\n', environ={}) == [("TOK", "a#b", None)]


# ---------------------------------------------------------------------------
# dry-run (offline)
# ---------------------------------------------------------------------------
def test_dry_run_lists_all_entries_and_flags_descriptions(tmp_path: Path) -> None:
    f = tmp_path / "secrets.env.example"
    f.write_text("# guidance for A\nA=${A:-1}\nEMPTY=${EMPTY:-}\n")
    result = runner.invoke(app, ["upload", str(f), "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "A" in result.output and "EMPTY" in result.output
    assert "would set" in result.output
    assert "would upload 2" in result.output
    assert "1 with a description" in result.output


def test_dry_run_json(tmp_path: Path) -> None:
    f = tmp_path / "secrets.env.example"
    f.write_text("# d\nA=1\nEMPTY=\n")
    result = runner.invoke(app, ["upload", str(f), "--dry-run", "-f", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload == [
        {"name": "A", "status": "would set (+desc)"},
        {"name": "EMPTY", "status": "would set"},
    ]


def test_dry_run_reads_dash_stdin() -> None:
    result = runner.invoke(app, ["upload", "-", "--dry-run"], input="export FOO=bar\n")
    assert result.exit_code == 0, result.output
    assert "FOO" in result.output and "would upload 1" in result.output


def test_dry_run_reads_piped_stdin_by_default() -> None:
    result = runner.invoke(app, ["upload", "--dry-run"], input="BAZ=qux\n")
    assert result.exit_code == 0, result.output
    assert "BAZ" in result.output


def test_missing_file_errors() -> None:
    result = runner.invoke(app, ["upload", "/no/such/secrets.txt", "--dry-run"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_empty_input_is_a_clean_noop() -> None:
    result = runner.invoke(app, ["upload", "-", "--dry-run"], input="# nothing here\n")
    assert result.exit_code == 0
    assert "No secrets found" in result.output


def test_no_file_and_interactive_terminal_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """No FILE and an interactive terminal is a usage error — no implicit default."""

    class _Tty:
        def isatty(self) -> bool:
            return True

        def read(self) -> str:  # pragma: no cover — must never be reached
            raise AssertionError("stdin should not be read at an interactive terminal")

    monkeypatch.setattr("sys.stdin", _Tty())
    with pytest.raises(typer.Exit) as exc:
        _read_secrets_source(None)
    assert exc.value.exit_code == 2


# ---------------------------------------------------------------------------
# real upload path (async_client monkeypatched — no backend)
# ---------------------------------------------------------------------------
class _Sink:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str | None]] = []

    async def set(self, name: str, value: str, *, description: str | None = None) -> SimpleNamespace:
        self.calls.append((name, value, description))
        return SimpleNamespace(name=name)


def test_upload_sets_every_entry_with_its_description(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _Sink()

    @asynccontextmanager
    async def fake_async_client(api_key=None, base_url=None):  # type: ignore[no-untyped-def]
        yield SimpleNamespace(secrets=sink)

    monkeypatch.setattr("unitysvc_sellers.commands.secrets.async_client", fake_async_client)

    f = tmp_path / "secrets.env.example"
    # Source semantics: every declared entry is set, empties included (they carry
    # the description); the description is the comment block above each var.
    f.write_text("# guidance for A\nA=1\nEMPTY=\n")
    result = runner.invoke(app, ["upload", str(f)])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("A", "1", "guidance for A"), ("EMPTY", "", None)]
    assert "uploaded 2" in result.output
