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
    ManifestResolutionError,
    _parse_secrets_text,
    _read_secrets_source,
    _resolve_rhs,
    app,
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# parser — (name, value, description, sensitive) tuples
# ---------------------------------------------------------------------------
def test_parse_extracts_values_and_descriptions() -> None:
    text = """
    # file header, attaches to nothing

    # the webhook base url
    export DISCORD_WEBHOOK_BASE="https://mock.unitysvc.dev/x"
    DISCORD_WEBHOOK_ID='demo'
    """
    assert _parse_secrets_text(text, environ={}) == [
        ("DISCORD_WEBHOOK_BASE", "https://mock.unitysvc.dev/x", "the webhook base url", None),
        ("DISCORD_WEBHOOK_ID", "demo", None, None),
    ]


def test_parse_multiline_description_and_header_separation() -> None:
    text = "# header\n\n# line 1\n# line 2\nFOO=bar\n"
    assert _parse_secrets_text(text, environ={}) == [("FOO", "bar", "line 1\nline 2", None)]


def test_parse_resolves_env_expansion() -> None:
    text = "# base\nBASE_URL=${BASE_URL:-https://default.example.com}\n# key\nAPI_KEY=${API_KEY:-}\n"
    # env value wins when set; unset falls back to the default (here empty).
    assert _parse_secrets_text(text, environ={"BASE_URL": "https://real.example.com"}) == [
        ("BASE_URL", "https://real.example.com", "base", None),
        ("API_KEY", "", "key", None),
    ]


def test_parse_env_default_used_when_unset() -> None:
    text = "X=${X:-fallback}\n"
    assert _parse_secrets_text(text, environ={}) == [("X", "fallback", None, None)]


def test_double_quoted_expansion_is_resolved_not_literal() -> None:
    # Regression: a fully double-quoted ``${...}`` used to short-circuit and
    # upload the literal string. The shell expands inside double quotes, so we do
    # too — this is the exact form the committed manifests use.
    assert _resolve_rhs('"${ENDPOINT:-https://d.example}"', {}) == "https://d.example"
    assert _resolve_rhs('"${ENDPOINT:-https://d.example}"', {"ENDPOINT": "https://real"}) == "https://real"
    assert _resolve_rhs('"${KEY:-}"', {}) == ""


def test_single_quoted_expansion_stays_literal() -> None:
    # Single quotes are literal in the shell — no expansion.
    assert _resolve_rhs("'${KEY:-x}'", {"KEY": "real"}) == "${KEY:-x}"


def test_required_bare_expansion_errors_when_unset_or_empty() -> None:
    # ``${NAME}`` (no default) is required: unset or empty aborts, quoted or not.
    with pytest.raises(ManifestResolutionError) as exc:
        _resolve_rhs("${SECRET_KEY}", {})
    assert exc.value.name == "SECRET_KEY"
    with pytest.raises(ManifestResolutionError):
        _resolve_rhs('"${SECRET_KEY}"', {})  # quoted, still required
    with pytest.raises(ManifestResolutionError):
        _resolve_rhs("${SECRET_KEY}", {"SECRET_KEY": ""})  # set but empty


def test_required_bare_expansion_uses_env_when_set() -> None:
    assert _resolve_rhs("${SECRET_KEY}", {"SECRET_KEY": "s3cr3t"}) == "s3cr3t"
    assert _resolve_rhs('"${SECRET_KEY}"', {"SECRET_KEY": "s3cr3t"}) == "s3cr3t"


def test_parse_two_line_optional_then_required_unset() -> None:
    # The reported case: an optional line followed by a required one for the same
    # name. Last assignment wins, and the required (defaultless) form aborts.
    with pytest.raises(ManifestResolutionError) as exc:
        _parse_secrets_text(
            'export K="${K:-}"\nexport K="${K}"\n',
            environ={},
        )
    assert exc.value.name == "K"


def test_parse_last_assignment_wins_and_keeps_position() -> None:
    assert _parse_secrets_text("A=1\nB=2\nA=3\n", environ={}) == [
        ("A", "3", None, None),
        ("B", "2", None, None),
    ]


def test_parse_skips_invalid_names_and_non_assignments() -> None:
    text = "1BAD=x\nnot an assignment\nGOOD=ok\n"
    assert _parse_secrets_text(text, environ={}) == [("GOOD", "ok", None, None)]


def test_parse_preserves_empty_values() -> None:
    assert _parse_secrets_text("OPT=\nREQ=v\n", environ={}) == [
        ("OPT", "", None, None),
        ("REQ", "v", None, None),
    ]


def test_parse_does_not_strip_inner_hash() -> None:
    # Unquoted or quoted, a ``#`` not preceded by whitespace is part of the value.
    assert _parse_secrets_text('TOK="a#b"\n', environ={}) == [("TOK", "a#b", None, None)]
    assert _parse_secrets_text("TOK=a#b\n", environ={}) == [("TOK", "a#b", None, None)]


# ---------------------------------------------------------------------------
# parser — trailing ``# variable`` marker
# ---------------------------------------------------------------------------
def test_parse_trailing_variable_marker_sets_sensitive_false() -> None:
    text = "# from address\nNOTIFY_FROM=alerts@acme.com   # variable\nKEY=sk-abc\n"
    assert _parse_secrets_text(text, environ={}) == [
        ("NOTIFY_FROM", "alerts@acme.com", "from address", False),
        ("KEY", "sk-abc", None, None),
    ]


def test_parse_variable_marker_is_case_insensitive_and_env_aware() -> None:
    text = "BASE=${BASE:-https://d.example}  # Variable\n"
    assert _parse_secrets_text(text, environ={"BASE": "https://real.example"}) == [
        ("BASE", "https://real.example", None, False),
    ]


def test_parse_non_marker_trailing_comment_is_stripped_but_stays_secret() -> None:
    # A trailing comment that is not the marker is dropped (shell semantics),
    # and the entry stays a secret.
    assert _parse_secrets_text("TOK=sk-abc   # rotate me\n", environ={}) == [
        ("TOK", "sk-abc", None, None),
    ]


def test_parse_quoted_value_keeps_hash_but_honors_trailing_marker() -> None:
    assert _parse_secrets_text('P="a b#c"   # variable\n', environ={}) == [
        ("P", "a b#c", None, False),
    ]


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


def test_required_unset_aborts_with_clean_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # A required ``${NAME}`` whose var is unset fails the upload (exit 1) with a
    # targeted message, rather than a traceback or a silent empty upload.
    monkeypatch.delenv("S3_RELAY_SECRET_KEY", raising=False)
    f = tmp_path / "secrets.env.example"
    f.write_text('export S3_RELAY_SECRET_KEY="${S3_RELAY_SECRET_KEY}"\n')
    result = runner.invoke(app, ["upload", str(f), "--dry-run"])
    assert result.exit_code == 1
    assert "S3_RELAY_SECRET_KEY" in result.output
    assert "required" in result.output.lower()


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
        self.calls: list[tuple[str, str, str | None, bool | None]] = []

    async def set(
        self,
        name: str,
        value: str,
        *,
        sensitive: bool | None = None,
        description: str | None = None,
    ) -> SimpleNamespace:
        self.calls.append((name, value, description, sensitive))
        return SimpleNamespace(name=name, sensitive=sensitive)


def _patch_sink(monkeypatch: pytest.MonkeyPatch) -> _Sink:
    sink = _Sink()

    @asynccontextmanager
    async def fake_async_client(api_key=None, base_url=None):  # type: ignore[no-untyped-def]
        yield SimpleNamespace(secrets=sink)

    monkeypatch.setattr("unitysvc_sellers.commands.secrets.async_client", fake_async_client)
    return sink


def test_upload_sets_every_entry_with_its_description(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    f = tmp_path / "secrets.env.example"
    # Source semantics: every declared entry is set, empties included (they carry
    # the description); the description is the comment block above each var.
    f.write_text("# guidance for A\nA=1\nEMPTY=\n")
    result = runner.invoke(app, ["upload", str(f)])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("A", "1", "guidance for A", None), ("EMPTY", "", None, None)]
    assert "uploaded 2" in result.output


def test_upload_threads_variable_marker_as_sensitive_false(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    f = tmp_path / "secrets.env.example"
    f.write_text("NOTIFY_FROM=alerts@acme.com  # variable\nKEY=sk-abc\n")
    result = runner.invoke(app, ["upload", str(f)])

    assert result.exit_code == 0, result.output
    assert sink.calls == [
        ("NOTIFY_FROM", "alerts@acme.com", None, False),
        ("KEY", "sk-abc", None, None),
    ]
    assert "1 as variable(s)" in result.output


def test_set_variable_flag_passes_sensitive_false(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["set", "NOTIFY_FROM", "--value", "alerts@acme.com", "--variable"])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("NOTIFY_FROM", "alerts@acme.com", None, False)]
    assert "Set variable" in result.output


def test_set_without_variable_leaves_sensitive_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    sink = _patch_sink(monkeypatch)

    result = runner.invoke(app, ["set", "KEY", "--value", "sk-abc"])

    assert result.exit_code == 0, result.output
    assert sink.calls == [("KEY", "sk-abc", None, None)]
    assert "Set secret" in result.output
