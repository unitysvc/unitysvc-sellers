"""Tests for the ``<name>.override.json`` param-file companion.

A populator regenerates ``specs/<provider>/<name>.json`` on every run; the
committed override file — same shape, typically ``{"parameters": {…}}`` — is
deep-merged over it at render time by every ``specs`` command, so manual
corrections survive regeneration without touching the populator.
"""

import json
from pathlib import Path

import pytest

from tests.test_params_render import _make_repo
from unitysvc_sellers.params_render import (
    ParamRenderError,
    discover_param_files,
    load_param_data,
    materialized_param_specs,
    override_file_for,
)


def _write_override(root: Path, name: str, patch: dict) -> Path:
    path = root / "specs" / "unitysvc" / f"{name}.override.json"
    path.write_text(json.dumps(patch) + "\n")
    return path


def test_override_merges_into_parameters(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    _write_override(root, "resp200", {"parameters": {"label": "Overridden"}})

    data = load_param_data(root / "specs" / "unitysvc" / "resp200.json")
    assert data["parameters"]["label"] == "Overridden"  # patched
    assert data["parameters"]["status"] == 200  # untouched base value


def test_override_applies_in_materialized_render(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    _write_override(root, "resp200", {"parameters": {"label": "Overridden"}})

    with materialized_param_specs(root):
        # The context chdirs into the isolated temp copy — read relative.
        offering = json.loads(Path("specs/unitysvc/resp200/offering.json").read_text())
    assert "Overridden" in offering["summary"]


def test_override_file_is_not_a_param_file(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    _write_override(root, "resp200", {"parameters": {"label": "Overridden"}})
    found = discover_param_files(root)
    assert [p.name for p in found] == ["resp200.json"]


def test_deep_merge_semantics(tmp_path: Path) -> None:
    root = _make_repo(
        tmp_path,
        params={"resp200": {"status": 200, "label": "OK", "details": {"a": 1, "b": 2}}},
    )
    _write_override(root, "resp200", {"parameters": {"details": {"b": 3}}})
    data = load_param_data(root / "specs" / "unitysvc" / "resp200.json")
    assert data["parameters"]["details"] == {"a": 1, "b": 3}  # dicts merge per-key


def test_orphan_override_raises(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    _write_override(root, "resp999-typo", {"parameters": {"label": "x"}})
    with pytest.raises(ParamRenderError, match="no matching param file"):
        with materialized_param_specs(root):
            pass


def test_non_object_override_raises(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    path = root / "specs" / "unitysvc" / "resp200.override.json"
    path.write_text('["not", "an", "object"]\n')
    with pytest.raises(ParamRenderError, match="JSON object"):
        load_param_data(root / "specs" / "unitysvc" / "resp200.json")


def test_override_file_for_naming() -> None:
    assert override_file_for(Path("specs/p/m.json")) == Path("specs/p/m.override.json")
