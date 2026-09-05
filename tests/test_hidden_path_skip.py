"""Discovery walks must ignore hidden dot-directories.

Tooling routinely parks a *second copy of the repo* inside the repo: a git
worktree under ``.claude/worktrees/<branch>/``, an editor cache, a ``.venv``
with vendored fixtures. Those copies hold the same ``listing.json`` files with
the same ``listing.name``, so a walk that descends into them uploads (or
formats, or deprecates) every service twice — the second copy racing the first
onto the same backend ``service_id``.

``validate`` already skipped dot-paths; ``upload``/``format``/``--local-ids``
did not. ``unitysvc-core>=0.2.23`` skips them in its own walker, which covers
``find_files_by_pattern``; the walks below that bypass core apply the same
predicate themselves. These tests pin the behaviour at every seller-side entry
point regardless of which layer implements it, and pin the flip side: the skip
is computed **relative to the walk root**, so a catalog that legitimately lives
under a hidden directory (``~/.cache/repo``) is still discovered in full.
"""

from __future__ import annotations

import json
from pathlib import Path

from unitysvc_sellers.format_data import format_data_files
from unitysvc_sellers.params_render import discover_param_files
from unitysvc_sellers.specs_layout import find_service_folders
from unitysvc_sellers.utils import find_files_by_pattern, read_local_service_ids


def _write_service(folder: Path, name: str, *, service_id: str | None = None) -> Path:
    """Write a minimal spec folder; return its listing.json."""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "provider.json").write_text(json.dumps({"name": "labs"}))
    (folder / "offering.json").write_text(json.dumps({"name": name.split("/")[-1]}))
    listing = folder / "listing.json"
    listing.write_text(json.dumps({"name": name}))
    if service_id:
        (folder / "service.json").write_text(json.dumps({"service_id": service_id}))
    return listing


def _write_param_file(path: Path, name: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"template": "t", "parameters": {"name": name}}))
    return path


# --- find_files_by_pattern (upload, and most `services` commands) -----------


def test_find_files_by_pattern_skips_hidden_directories(tmp_path: Path) -> None:
    real = _write_service(tmp_path / "services" / "specs" / "svc", "labs/svc")
    worktree = _write_service(tmp_path / ".claude" / "worktrees" / "wt" / "services" / "specs" / "svc", "labs/svc")

    found = [p for p, _fmt, _data in find_files_by_pattern(tmp_path, "listing_v1")]

    assert real in found
    assert worktree not in found


def test_find_files_by_pattern_keeps_a_catalog_under_a_hidden_root(tmp_path: Path) -> None:
    """The skip is relative to the walk root — a repo cloned into ``.cache/``
    is a normal catalog, not a hidden one."""
    root = tmp_path / ".cache" / "repo"
    real = _write_service(root / "services" / "specs" / "svc", "labs/svc")

    found = [p for p, _fmt, _data in find_files_by_pattern(root, "listing_v1")]

    assert real in found


# --- param files (upload's system-template branch, specs render) -----------


def test_discover_param_files_skips_hidden_directories(tmp_path: Path) -> None:
    real = _write_param_file(tmp_path / "services" / "specs" / "svc.json", "labs/svc")
    worktree = _write_param_file(
        tmp_path / ".claude" / "worktrees" / "wt" / "services" / "specs" / "svc.json", "labs/svc"
    )

    found = discover_param_files(tmp_path)

    assert real in found
    assert worktree not in found


# --- validate's folder walk -------------------------------------------------


def test_find_service_folders_skips_hidden_directories(tmp_path: Path) -> None:
    real = _write_service(tmp_path / "svc", "labs/svc")
    worktree = _write_service(tmp_path / ".claude" / "worktrees" / "wt" / "svc", "labs/svc")

    folders = find_service_folders(tmp_path)

    assert real.parent in folders
    assert worktree.parent not in folders


def test_find_service_folders_keeps_a_catalog_under_a_hidden_root(tmp_path: Path) -> None:
    root = tmp_path / ".cache" / "repo" / "specs"
    real = _write_service(root / "svc", "labs/svc")

    assert find_service_folders(root) == [real.parent]


# --- --local-ids sidecar walk ----------------------------------------------


def test_read_local_service_ids_skips_hidden_directories(tmp_path: Path) -> None:
    _write_service(tmp_path / "services" / "specs" / "svc", "labs/svc", service_id="real-id")
    _write_service(
        tmp_path / ".claude" / "worktrees" / "wt" / "services" / "specs" / "svc",
        "labs/svc",
        service_id="stale-id",
    )

    assert read_local_service_ids(tmp_path) == ["real-id"]


# --- format ----------------------------------------------------------------


def test_format_data_files_skips_hidden_directories(tmp_path: Path) -> None:
    """Formatting must not reach into a nested worktree and rewrite its files."""
    _write_service(tmp_path / "services" / "specs" / "svc", "labs/svc")
    hidden = tmp_path / ".claude" / "worktrees" / "wt" / "services" / "specs" / "svc"
    hidden.mkdir(parents=True)
    unformatted = hidden / "listing.json"
    unformatted.write_text('{"b": 1, "a": 2}')

    assert format_data_files(tmp_path, check_only=False) is True
    assert unformatted.read_text() == '{"b": 1, "a": 2}'
