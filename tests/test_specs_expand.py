"""Tests for ``usvc_seller specs expand`` and the informal ``expanded/`` tree.

``expand`` renders a param file (``specs/<name>.json``) into a *static*,
user-owned inspection tree at the repo root (``expanded/<name>/``) that the
formal pipeline must ignore — it is never validated, uploaded, or refreshed by
anything except a re-run of ``expand`` itself.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from unitysvc_sellers.specs import app as specs_app
from unitysvc_sellers.utils import find_files_by_schema

from .test_params_render import OFFERING_J2, PROVIDER, _make_repo

runner = CliRunner()

# A listing whose only document is a bundled preset reference. ``expand
# --presets`` should turn the ``$doc_preset`` sentinel into a record that points
# at a LOCAL copy of the bundled file.
_LISTING_PRESET_J2 = """{
  "name": "{{ service_name }}",
  "display_name": "P {{ status }}",
  "currency": "USD",
  "status": "ready",
  "list_price": {"type": "constant", "price": "0", "description": "Free"},
  "user_access_interfaces": {"direct_response": {"access_method": "http", "base_url": "x"}},
  "documents": {"Connectivity": {"$doc_preset": "s3_connectivity_v1"}}
}
"""


def _make_preset_repo(tmp_path: Path) -> Path:
    """Repo whose template emits a ``$doc_preset`` document reference."""
    tdir = tmp_path / "templates" / "p"
    tdir.mkdir(parents=True)
    (tdir / "provider.json").write_text(PROVIDER + "\n")
    (tdir / "offering.json.j2").write_text(OFFERING_J2)
    (tdir / "listing.json.j2").write_text(_LISTING_PRESET_J2)
    specs = tmp_path / "specs" / "unitysvc"
    specs.mkdir(parents=True)
    (specs / "p1.json").write_text(json.dumps({"template": "p", "parameters": {"status": 200, "label": "OK"}}) + "\n")
    return tmp_path


def test_find_files_by_schema_excludes_top_level_expanded_tree(tmp_path: Path) -> None:
    """Discovery must skip the informal ``expanded/`` tree but keep ``specs/``."""
    specs_listing = tmp_path / "specs" / "unitysvc" / "foo" / "listing.json"
    specs_listing.parent.mkdir(parents=True)
    specs_listing.write_text(json.dumps({"name": "unitysvc/foo"}))

    expanded_listing = tmp_path / "expanded" / "unitysvc" / "foo" / "listing.json"
    expanded_listing.parent.mkdir(parents=True)
    expanded_listing.write_text(json.dumps({"name": "unitysvc/foo"}))

    found = {p for p, _, _ in find_files_by_schema(tmp_path, "listing_v1")}

    assert specs_listing in found
    assert expanded_listing not in found


def test_expand_param_file_writes_static_inspection_tree(tmp_path: Path) -> None:
    """``expand_param_file`` renders into ``expanded/<name>/`` and leaves both the
    param file and the formal ``specs/`` tree untouched."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_repo(tmp_path)  # specs/unitysvc/resp200.json (param file)
    param_file = root / "specs" / "unitysvc" / "resp200.json"

    folder = expand_param_file(param_file)

    assert folder == root / "expanded" / "unitysvc" / "resp200"
    for f in ("provider.json", "offering.json", "listing.json", "connectivity.sh.j2"):
        assert (folder / f).is_file(), f
    listing = json.loads((folder / "listing.json").read_text())
    assert listing["name"] == "unitysvc/resp200"
    # Inspection-only: no backend identity record is ever written here.
    assert not (folder / "service.json").exists()
    # The formal layout is untouched: param file stays, no specs/<name>/ folder.
    assert param_file.exists()
    assert not (root / "specs" / "unitysvc" / "resp200").exists()


def test_expand_param_file_custom_output_dir(tmp_path: Path) -> None:
    """``output_dir`` overrides the default ``expanded/`` location; the full
    ``<service_name>`` path is still nested under it."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_repo(tmp_path)
    out = tmp_path / "scratch"

    folder = expand_param_file(root / "specs" / "unitysvc" / "resp200.json", output_dir=out)

    assert folder == out / "unitysvc" / "resp200"
    assert (folder / "listing.json").is_file()


def test_expand_multiple_services_share_dir_without_collision(tmp_path: Path) -> None:
    """Two services expanded into one dir land in distinct ``<service_name>/``
    subfolders — the collision-avoidance invariant."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_repo(
        tmp_path,
        params={"resp200": {"status": 200, "label": "OK"}, "resp404": {"status": 404, "label": "NF"}},
    )
    out = tmp_path / "expanded"

    f200 = expand_param_file(root / "specs" / "unitysvc" / "resp200.json", output_dir=out)
    f404 = expand_param_file(root / "specs" / "unitysvc" / "resp404.json", output_dir=out)

    assert f200 != f404
    assert json.loads((f200 / "listing.json").read_text())["name"] == "unitysvc/resp200"
    assert json.loads((f404 / "listing.json").read_text())["name"] == "unitysvc/resp404"


def test_expand_flat_writes_files_directly_into_dir(tmp_path: Path) -> None:
    """``flat`` drops the ``<service_name>/`` nesting — files land directly in the
    output dir, with predictable paths regardless of service name."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_repo(tmp_path)
    out = tmp_path / "look"

    folder = expand_param_file(root / "specs" / "unitysvc" / "resp200.json", output_dir=out, flat=True)

    assert folder == out
    for f in ("provider.json", "offering.json", "listing.json", "connectivity.sh.j2"):
        assert (out / f).is_file(), f
    assert not (out / "unitysvc").exists()
    # Content still carries the real service name (only the *path* is flattened).
    assert json.loads((out / "listing.json").read_text())["name"] == "unitysvc/resp200"


def test_expand_flat_preserves_unrelated_files(tmp_path: Path) -> None:
    """Flat must not nuke the output dir — it only writes its own spec files."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_repo(tmp_path)
    out = tmp_path / "look"
    out.mkdir()
    (out / "notes.txt").write_text("keep me")

    expand_param_file(root / "specs" / "unitysvc" / "resp200.json", output_dir=out, flat=True)

    assert (out / "notes.txt").read_text() == "keep me"
    assert (out / "listing.json").is_file()


def test_expand_command_flat_option(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    out = tmp_path / "look"

    result = runner.invoke(specs_app, ["expand", "unitysvc/resp200", "--flat", "-o", str(out), "-d", str(root)])

    assert result.exit_code == 0, result.output
    assert (out / "listing.json").is_file()
    assert not (out / "unitysvc").exists()


def test_expand_param_file_is_idempotent(tmp_path: Path) -> None:
    """Re-running refreshes the folder in place (overwrites a stale render)."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_repo(tmp_path)
    param_file = root / "specs" / "unitysvc" / "resp200.json"

    folder = expand_param_file(param_file)
    (folder / "stale.txt").write_text("left over from a previous expand\n")

    again = expand_param_file(param_file)

    assert again == folder
    assert (folder / "listing.json").is_file()
    assert not (folder / "stale.txt").exists()


def test_expand_without_presets_leaves_sentinel_untouched(tmp_path: Path) -> None:
    """Default expand keeps ``$doc_preset`` as authored — no file is materialized."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_preset_repo(tmp_path)
    folder = expand_param_file(root / "specs" / "unitysvc" / "p1.json")

    listing = json.loads((folder / "listing.json").read_text())
    assert listing["documents"]["Connectivity"] == {"$doc_preset": "s3_connectivity_v1"}


def test_expand_presets_materializes_doc_into_folder(tmp_path: Path) -> None:
    """``--presets`` resolves the sentinel and copies the bundled doc in, with a
    folder-local ``file_path`` so the render is self-contained."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_preset_repo(tmp_path)
    folder = expand_param_file(root / "specs" / "unitysvc" / "p1.json", expand_presets=True)

    listing = json.loads((folder / "listing.json").read_text())
    record = listing["documents"]["Connectivity"]

    # Sentinel resolved away, file_path now points at a local sibling that exists.
    assert "$doc_preset" not in json.dumps(record)
    assert not Path(record["file_path"]).is_absolute()
    assert (folder / record["file_path"]).is_file()


def test_expand_command_renders_and_reports(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)

    result = runner.invoke(specs_app, ["expand", "unitysvc/resp200", "-d", str(root)])

    assert result.exit_code == 0, result.output
    folder = root / "expanded" / "unitysvc" / "resp200"
    assert (folder / "listing.json").is_file()
    # The folder path is reported (rich may soft-wrap it, so compare whitespace-free).
    assert str(folder) in "".join(result.output.split())


def test_expand_command_presets_flag(tmp_path: Path) -> None:
    root = _make_preset_repo(tmp_path)

    result = runner.invoke(specs_app, ["expand", "unitysvc/p1", "--presets", "-d", str(root)])

    assert result.exit_code == 0, result.output
    listing = json.loads((root / "expanded" / "unitysvc" / "p1" / "listing.json").read_text())
    assert "$doc_preset" not in json.dumps(listing["documents"]["Connectivity"])


def test_expand_command_output_dir_option(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    out = tmp_path / "look_here"

    result = runner.invoke(specs_app, ["expand", "unitysvc/resp200", "-o", str(out), "-d", str(root)])

    assert result.exit_code == 0, result.output
    assert (out / "unitysvc" / "resp200" / "listing.json").is_file()
    # Default expanded/ tree is NOT created when an output dir is given.
    assert not (root / "expanded").exists()


def test_expand_command_unknown_name_errors(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)

    result = runner.invoke(specs_app, ["expand", "unitysvc/nope", "-d", str(root)])

    assert result.exit_code != 0


def test_expand_command_rejects_non_param_file(tmp_path: Path) -> None:
    """Pointing expand at a real spec file (not a param file) is a clear error."""
    root = _make_repo(tmp_path)
    (root / "specs" / "unitysvc" / "provider.json").write_text(PROVIDER + "\n")

    result = runner.invoke(specs_app, ["expand", "unitysvc/provider", "-d", str(root)])

    assert result.exit_code != 0


def test_pipeline_ignores_expanded_tree_end_to_end(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """After ``expand`` materializes ``expanded/<name>/``, a real ``list`` (which
    walks the repo via the wrapped discovery) still reports only the formal
    services — the inspection tree is neither counted nor cleaned up."""
    from unitysvc_sellers.cli import app as cli_app

    root = _make_repo(
        tmp_path,
        params={"resp200": {"status": 200, "label": "OK"}, "resp404": {"status": 404, "label": "NF"}},
    )
    monkeypatch.chdir(root)

    expanded = CliRunner().invoke(cli_app, ["specs", "expand", "unitysvc/resp200"])
    assert expanded.exit_code == 0, expanded.output
    inspect_listing = root / "expanded" / "unitysvc" / "resp200" / "listing.json"
    assert inspect_listing.is_file()

    listed = CliRunner().invoke(cli_app, ["specs", "list", "services"])
    assert listed.exit_code == 0, listed.output
    # Exactly the two formal services — resp200 is NOT double-counted via expanded/.
    assert "2 service(s)" in listed.output
    # The pipeline left the inspection tree alone.
    assert inspect_listing.is_file()
