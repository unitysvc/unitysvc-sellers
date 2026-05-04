"""Tests for ``unitysvc_sellers.format_data``.

Locks in the post-populate post-step regression: the plain
``format_data_files`` helper must actually rewrite files when
``check_only=False``, and the Typer-decorated ``format_data`` command
must keep working as a CLI entry point.
"""

import json
from pathlib import Path

from unitysvc_sellers.format_data import format_data_files


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class TestFormatDataFiles:
    """Direct unit tests for the plain helper used by ``populate``."""

    def test_rewrites_json_with_sorted_keys_and_trailing_newline(
        self, tmp_path: Path
    ) -> None:
        f = tmp_path / "listing.json"
        _write(f, '{"name":"x","a":1}')  # unsorted, no trailing newline

        ok = format_data_files(tmp_path, check_only=False)

        assert ok is True
        # Sorted keys, 2-space indent, trailing newline.
        assert f.read_text() == '{\n  "a": 1,\n  "name": "x"\n}\n'

    def test_already_formatted_is_idempotent(self, tmp_path: Path) -> None:
        f = tmp_path / "listing.json"
        canonical = '{\n  "a": 1,\n  "b": 2\n}\n'
        _write(f, canonical)

        ok = format_data_files(tmp_path, check_only=False)

        assert ok is True
        assert f.read_text() == canonical

    def test_check_only_does_not_rewrite(self, tmp_path: Path) -> None:
        f = tmp_path / "listing.json"
        original = '{"b":1,"a":2}'
        _write(f, original)

        ok = format_data_files(tmp_path, check_only=True)

        # File would need formatting → check returns False.
        assert ok is False
        # …but the file is left exactly as we wrote it.
        assert f.read_text() == original

    def test_check_only_passes_when_already_formatted(
        self, tmp_path: Path
    ) -> None:
        f = tmp_path / "listing.json"
        _write(f, '{\n  "a": 1\n}\n')

        ok = format_data_files(tmp_path, check_only=True)

        assert ok is True

    def test_strips_trailing_whitespace_from_md(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        _write(f, "# Title  \n\nbody  \n")  # trailing spaces

        ok = format_data_files(tmp_path, check_only=False)

        assert ok is True
        assert f.read_text() == "# Title\n\nbody\n"

    def test_invalid_json_returns_false(self, tmp_path: Path) -> None:
        f = tmp_path / "listing.json"
        _write(f, "{not valid json")

        ok = format_data_files(tmp_path, check_only=False)

        assert ok is False
        # File is left untouched on parse failure.
        assert f.read_text() == "{not valid json"


class TestFormatDataDoesNotLeakTyperDefaults:
    """Regression: previously ``populate.py`` called the Typer-decorated
    ``format_data(data_dir)`` as a regular function, and the
    ``check_only: bool = typer.Option(False, ...)`` default leaked
    through as an ``OptionInfo`` instance — which is truthy under
    Python's default ``__bool__``, silently turning every
    post-populate format pass into a no-op check-only run.

    The fix is to call the plain ``format_data_files`` helper.  These
    tests lock that contract in: the helper takes a real ``bool``,
    not a ``typer.Option`` default, and writes when ``check_only=False``.
    """

    def test_helper_does_not_take_typer_option_defaults(
        self, tmp_path: Path
    ) -> None:
        # Calling without the kwarg uses the helper's plain ``bool`` default
        # (``False``) and therefore writes — proving no Typer ``OptionInfo``
        # leak.
        f = tmp_path / "listing.json"
        _write(f, '{"b":1,"a":2}')

        format_data_files(tmp_path)  # no check_only kwarg

        # File got rewritten — would not happen if check_only had defaulted
        # to a truthy ``OptionInfo``.
        assert json.loads(f.read_text()) == {"a": 2, "b": 1}
        assert f.read_text().endswith("\n")
