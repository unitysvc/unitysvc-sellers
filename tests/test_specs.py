"""Tests for ``usvc_seller specs validate`` (the flat ``specs/`` layout)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from unitysvc_sellers.specs import app

EXAMPLE_DATA = Path(__file__).parent / "example_data"
runner = CliRunner()


def _strip_schema(path: Path) -> None:
    data = json.loads(path.read_text())
    data.pop("schema", None)
    path.write_text(json.dumps(data, indent=2) + "\n")


@pytest.fixture
def specs_repo(tmp_path: Path) -> Path:
    """Build a valid one-service ``specs/`` repo from the preset-free
    ``provider2/service2`` example fixture.

    Layout::

        <tmp>/specs/provider2/service2/{provider,offering,listing}.json
    """
    folder = tmp_path / "specs" / "provider2" / "service2"
    folder.mkdir(parents=True)

    src = EXAMPLE_DATA / "provider2" / "services" / "service2"
    for f in src.iterdir():
        if f.is_file():
            shutil.copy2(f, folder / f.name)
    shutil.copy2(EXAMPLE_DATA / "provider2" / "provider.json", folder / "provider.json")

    for name in ("provider.json", "offering.json", "listing.json"):
        _strip_schema(folder / name)

    # listing.name is already "provider2/service2" == folder path under specs/.
    return tmp_path


def _run(target: Path, *args: str):
    # ``app`` has a single command, so it is invoked without a command name.
    return runner.invoke(app, [str(target), *args])


def _norm(output: str) -> str:
    """Collapse whitespace so assertions survive rich's line wrapping."""
    return " ".join(output.split())


def test_valid_specs_repo_passes(specs_repo: Path) -> None:
    result = _run(specs_repo)
    assert result.exit_code == 0, result.output
    assert "valid" in result.output.lower()


def test_resolves_specs_subdir_or_root(specs_repo: Path) -> None:
    # Pointing at the repo root and at specs/ directly both work.
    assert _run(specs_repo).exit_code == 0
    assert _run(specs_repo / "specs").exit_code == 0


def test_schema_field_is_rejected(specs_repo: Path) -> None:
    listing = specs_repo / "specs" / "provider2" / "service2" / "listing.json"
    data = json.loads(listing.read_text())
    data["schema"] = "listing_v1"
    listing.write_text(json.dumps(data, indent=2) + "\n")

    result = _run(specs_repo)
    assert result.exit_code == 1
    assert "remove the 'schema' field" in _norm(result.output)


def test_missing_required_file_is_rejected(specs_repo: Path) -> None:
    (specs_repo / "specs" / "provider2" / "service2" / "offering.json").unlink()
    result = _run(specs_repo)
    assert result.exit_code == 1
    assert "missing required offering file" in _norm(result.output)


def test_name_must_match_folder_path(specs_repo: Path) -> None:
    folder = specs_repo / "specs" / "provider2" / "service2"
    renamed = folder.parent / "renamed"
    folder.rename(renamed)  # folder path now provider2/renamed, name still provider2/service2

    result = _run(specs_repo)
    assert result.exit_code == 1
    assert "does not match the folder path" in _norm(result.output)


def test_legacy_override_file_is_rejected(specs_repo: Path) -> None:
    folder = specs_repo / "specs" / "provider2" / "service2"
    (folder / "listing.override.json").write_text('{"service_id": "x"}\n')

    result = _run(specs_repo)
    assert result.exit_code == 1
    assert "legacy override file" in _norm(result.output)


def test_no_service_folders_errors(tmp_path: Path) -> None:
    (tmp_path / "specs").mkdir()
    result = _run(tmp_path)
    assert result.exit_code == 1
    assert "no service folders" in _norm(result.output).lower()


def test_has_service_id_flag(specs_repo: Path) -> None:
    folder = specs_repo / "specs" / "provider2" / "service2"
    # Without service.json, --has-service-id fails.
    result = _run(specs_repo, "--has-service-id")
    assert result.exit_code == 1
    assert "missing service_id" in _norm(result.output)

    # With a service.json carrying a service_id, it passes.
    (folder / "service.json").write_text('{"service_id": "abc-123"}\n')
    result = _run(specs_repo, "--has-service-id")
    assert result.exit_code == 0, result.output
