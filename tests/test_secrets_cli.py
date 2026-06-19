"""Tests for ``usvc_seller secrets upload`` and its dotenv-style parser.

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
# parser
# ---------------------------------------------------------------------------
def test_parse_handles_export_quotes_comments_and_blanks() -> None:
    text = """
    # a comment
    export DISCORD_WEBHOOK_BASE="https://mock.unitysvc.dev/discord/api/webhooks"

    DISCORD_WEBHOOK_ID='demo'
    export DISCORD_WEBHOOK_TOKEN=demotoken
    """
    assert _parse_secrets_text(text) == [
        ("DISCORD_WEBHOOK_BASE", "https://mock.unitysvc.dev/discord/api/webhooks"),
        ("DISCORD_WEBHOOK_ID", "demo"),
        ("DISCORD_WEBHOOK_TOKEN", "demotoken"),
    ]


def test_parse_last_assignment_wins_and_keeps_position() -> None:
    assert _parse_secrets_text("A=1\nB=2\nA=3\n") == [("A", "3"), ("B", "2")]


def test_parse_skips_invalid_names_and_non_assignments() -> None:
    text = "1BAD=x\nnot an assignment\nGOOD=ok\n"
    assert _parse_secrets_text(text) == [("GOOD", "ok")]


def test_parse_preserves_empty_values() -> None:
    # Empty values are kept (the command decides to skip them).
    assert _parse_secrets_text("OPT=\nREQ=v\n") == [("OPT", ""), ("REQ", "v")]


def test_parse_does_not_strip_inner_hash() -> None:
    # '#' only starts a comment at the beginning of a (stripped) line.
    assert _parse_secrets_text('TOK="a#b"\n') == [("TOK", "a#b")]


# ---------------------------------------------------------------------------
# dry-run (offline)
# ---------------------------------------------------------------------------
def test_dry_run_from_file_lists_names_without_network(tmp_path: Path) -> None:
    f = tmp_path / "secrets.txt"
    f.write_text("export A=1\nB=2\nEMPTY=\n")
    result = runner.invoke(app, ["upload", str(f), "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "A" in result.output and "B" in result.output
    assert "would set" in result.output
    assert "would upload 2" in result.output
    assert "skipped 1" in result.output


def test_dry_run_json(tmp_path: Path) -> None:
    f = tmp_path / "secrets.txt"
    f.write_text("A=1\nEMPTY=\n")
    result = runner.invoke(app, ["upload", str(f), "--dry-run", "-f", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload == [
        {"name": "A", "status": "would set"},
        {"name": "EMPTY", "status": "skip (empty)"},
    ]


def test_dry_run_reads_dash_stdin() -> None:
    result = runner.invoke(app, ["upload", "-", "--dry-run"], input="export FOO=bar\n")
    assert result.exit_code == 0, result.output
    assert "FOO" in result.output and "would upload 1" in result.output


def test_dry_run_reads_piped_stdin_by_default() -> None:
    # No FILE arg + piped stdin (CliRunner stdin is not a tty) → read stdin.
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
        self.calls: list[tuple[str, str]] = []

    async def set(self, name: str, value: str) -> SimpleNamespace:
        self.calls.append((name, value))
        return SimpleNamespace(name=name)


def test_upload_sets_each_nonempty_secret_and_skips_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _Sink()

    @asynccontextmanager
    async def fake_async_client(api_key=None, base_url=None):  # type: ignore[no-untyped-def]
        yield SimpleNamespace(secrets=sink)

    monkeypatch.setattr("unitysvc_sellers.commands.secrets.async_client", fake_async_client)

    f = tmp_path / "secrets.txt"
    f.write_text("export A=1\nB=2\nEMPTY=\n")
    result = runner.invoke(app, ["upload", str(f)])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("A", "1"), ("B", "2")]  # EMPTY skipped, not sent
    assert "uploaded 2" in result.output
    assert "skipped 1" in result.output
