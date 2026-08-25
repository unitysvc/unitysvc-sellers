"""Tests for the model_overrides.toml convention (load/skip/apply/warn)."""

import logging
from pathlib import Path

import pytest

from unitysvc_sellers.model_overrides import (
    ModelOverrides,
    load_model_overrides,
)


def _write(tmp_path: Path, body: str) -> Path:
    (tmp_path / "model_overrides.toml").write_text(body)
    return tmp_path


def test_missing_file_is_noop(tmp_path: Path) -> None:
    ov = load_model_overrides(tmp_path)
    assert ov.entries == {}
    assert not ov.skip("anything")
    vars_in = {"supports_tools": True}
    assert ov.apply("anything", vars_in) == vars_in


def test_skip_and_apply(tmp_path: Path) -> None:
    ov = load_model_overrides(
        _write(
            tmp_path,
            """
[models."greg-1-mini"]
skip = true
comment = "listed but 404s at inference (2026-08-25)"

[models."Qwen/Qwen2.5-VL-72B-Instruct"]
supports_tools = false
comment = "deployment 400s on tools"

[models."old-model"]
deprecated = true
comment = "delisted upstream"
""",
        )
    )
    assert ov.skip("greg-1-mini")
    assert not ov.skip("Qwen/Qwen2.5-VL-72B-Instruct")

    merged = ov.apply("Qwen/Qwen2.5-VL-72B-Instruct", {"supports_tools": True, "status": "ready"})
    assert merged["supports_tools"] is False
    assert merged["status"] == "ready"  # field override does not touch status

    dep = ov.apply("old-model", {"status": "ready"})
    assert dep["status"] == "deprecated"

    # comment/skip/deprecated never leak into template vars
    assert "comment" not in merged and "comment" not in dep
    assert "deprecated" not in dep

    # input dict is not mutated
    original = {"supports_tools": True}
    ov.apply("Qwen/Qwen2.5-VL-72B-Instruct", original)
    assert original["supports_tools"] is True


def test_unmatched_entries_warn(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    ov = load_model_overrides(
        _write(
            tmp_path,
            """
[models."ghost-model"]
supports_tools = false
comment = "never existed"
""",
        )
    )
    with caplog.at_level(logging.WARNING):
        stale = ov.warn_unmatched({"real-model"})
    assert stale == ["ghost-model"]
    assert "ghost-model" in caplog.text


def test_skip_without_comment_rejected(tmp_path: Path) -> None:
    _write(tmp_path, '[models."m1"]\nskip = true\n')
    with pytest.raises(ValueError, match="comment"):
        load_model_overrides(tmp_path)


def test_non_bool_flag_rejected(tmp_path: Path) -> None:
    _write(tmp_path, '[models."m1"]\nskip = "yes"\ncomment = "x"\n')
    with pytest.raises(ValueError, match="boolean"):
        load_model_overrides(tmp_path)


def test_non_table_entry_rejected(tmp_path: Path) -> None:
    _write(tmp_path, '[models]\nm1 = "skip"\n')
    with pytest.raises(ValueError, match="table"):
        load_model_overrides(tmp_path)


def test_default_object_is_empty() -> None:
    ov = ModelOverrides()
    assert ov.apply("m", {"a": 1}) == {"a": 1}
    assert ov.warn_unmatched(set()) == []


def test_spec_shaped_subtables_rejected(tmp_path: Path) -> None:
    """offering/listing/provider sub-tables are reserved for a future v2."""
    _write(
        tmp_path,
        """
[models."m1".offering.details]
context_length = 32768
""",
    )
    with pytest.raises(ValueError, match="reserved for future spec-shaped"):
        load_model_overrides(tmp_path)
