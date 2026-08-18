"""Tests for local param-file rendering (``params_render``).

A param file ``specs/<provider>/<name>.json`` ({template, parameters}) is
rendered, via a local template directory, into an ephemeral service folder that
the normal ``specs`` pipeline consumes; the folder is cleaned up afterwards and
any backend ``service_id`` is synced to the ``<name>.service.json`` sidecar.
"""

import json
from pathlib import Path

import pytest

from unitysvc_sellers.params_render import (
    ParamRenderError,
    materialized_param_specs,
    write_params_from_iterator,
)

PROVIDER = json.dumps(
    {
        "name": "unitysvc",
        "display_name": "UnitySVC",
        "homepage": "https://unitysvc.com/",
        "contact_email": "service@unitysvc.com",
        "status": "ready",
        "time_created": "2026-05-31T00:00:00Z",
    }
)
OFFERING_J2 = """{
  "name": "resp{{ status }}",
  "service_type": "gateway",
  "capabilities": ["http_relay"],
  "summary": "Returns HTTP {{ status }} ({{ label }}).",
  "description": "Returns HTTP {{ status }} ({{ label }}).\\n\\nA test gateway that always returns this HTTP status.",
  "status": "ready",
  "tags": ["gateway", "test"],
  "time_created": "2026-05-31T00:00:00Z",
  "upstream_access_config": {"direct_response": {"access_method": "http", "base_url": "resp://{{ status }}"}}
}
"""
LISTING_J2 = """{
  "name": "{{ service_name }}",
  "display_name": "Direct Response {{ status }}",
  "currency": "USD",
  "status": "ready",
  "list_price": {"type": "constant", "price": "0", "description": "Free"},
  "user_access_interfaces": {
    "direct_response": {
      "access_method": "http",
      "base_url": "${API_GATEWAY_BASE_URL}/{{ service_name }}"
    }
  },
  "documents": {
    "Connectivity test": {
      "category": "connectivity_test",
      "description": "x",
      "file_path": "connectivity.sh.j2",
      "is_active": true,
      "is_public": false,
      "meta": {"output_contains": "ok"},
      "mime_type": "bash"
    }
  }
}
"""


def _make_repo(tmp_path: Path, *, params: dict[str, dict] | None = None) -> Path:
    """Build a repo with a `resp` template and the given param files; return root."""
    tdir = tmp_path / "templates" / "resp"
    tdir.mkdir(parents=True)
    (tdir / "provider.json").write_text(PROVIDER + "\n")
    (tdir / "offering.json.j2").write_text(OFFERING_J2)
    (tdir / "listing.json.j2").write_text(LISTING_J2)
    (tdir / "connectivity.sh.j2").write_text("echo ok\n")
    specs = tmp_path / "specs" / "unitysvc"
    specs.mkdir(parents=True)
    for name, params_dict in (params or {"resp200": {"status": 200, "label": "OK"}}).items():
        (specs / f"{name}.json").write_text(json.dumps({"template": "resp", "parameters": params_dict}) + "\n")
    return tmp_path


def test_renders_into_isolated_temp_not_in_place(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, params={"resp200": {"status": 200, "label": "OK"}})
    in_place = root / "specs" / "unitysvc" / "resp200"
    outer_cwd = Path.cwd()

    with materialized_param_specs(root) as rendered:
        assert len(rendered) == 1
        folder = rendered[0]
        # Rendered into an isolated temp copy, NOT the real tree — so a second
        # session can render/upload/test concurrently without colliding.
        assert not folder.is_relative_to(root), folder
        assert not in_place.exists(), "must not render in-place under real specs/"
        # cwd is redirected into the copy so the whole pipeline scans it.
        assert Path.cwd() != outer_cwd
        # self-contained: offering + listing + provider + bundled connectivity
        for f in ("offering.json", "listing.json", "provider.json", "connectivity.sh.j2"):
            assert (folder / f).exists(), f
        offering = json.loads((folder / "offering.json").read_text())
        listing = json.loads((folder / "listing.json").read_text())
        assert offering["name"] == "resp200"
        assert offering["upstream_access_config"]["direct_response"]["base_url"] == "resp://200"
        # listing.name == folder path under specs/ (from {{ service_name }})
        assert listing["name"] == "unitysvc/resp200"

    # cwd restored; copy gone; real repo never touched (param file intact).
    assert Path.cwd() == outer_cwd
    assert not folder.exists()
    assert not in_place.exists()
    assert (root / "specs" / "unitysvc" / "resp200.json").exists()


def test_no_param_files_is_noop(tmp_path: Path) -> None:
    # A concrete-only repo has nothing to render: no copy, no chdir.
    svc = tmp_path / "specs" / "unitysvc" / "svc"
    svc.mkdir(parents=True)
    (svc / "offering.json").write_text(json.dumps({"name": "svc"}) + "\n")
    (tmp_path / "templates").mkdir()
    outer_cwd = Path.cwd()

    with materialized_param_specs(tmp_path) as rendered:
        assert rendered == []
        assert Path.cwd() == outer_cwd  # no chdir for concrete-only repos
    assert Path.cwd() == outer_cwd


def test_service_id_sidecar_roundtrip(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    sidecar = root / "specs" / "unitysvc" / "resp200.service.json"
    sidecar.write_text(json.dumps({"service_id": "existing-id"}) + "\n")

    with materialized_param_specs(root) as rendered:
        folder = rendered[0]  # inside the isolated copy
        # seeded from the committed sidecar so the upload updates the same service
        assert json.loads((folder / "service.json").read_text())["service_id"] == "existing-id"
        # simulate the backend assigning/refreshing the id during upload
        (folder / "service.json").write_text(json.dumps({"service_id": "new-id"}) + "\n")

    # synced back to the committed (real) sidecar; copy cleaned up
    assert json.loads(sidecar.read_text())["service_id"] == "new-id"
    assert not (root / "specs" / "unitysvc" / "resp200").exists()


def test_bad_template_raises(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    (root / "specs" / "unitysvc" / "bad.json").write_text(json.dumps({"template": "nope", "parameters": {}}))
    with pytest.raises(ParamRenderError, match="local template 'nope' not found"):
        with materialized_param_specs(root):
            pass


def test_folder_and_param_file_conflict_raises(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    (root / "specs" / "unitysvc" / "resp200").mkdir()  # a folder at the same path
    with pytest.raises(ParamRenderError, match="a service is one or the other"):
        with materialized_param_specs(root):
            pass


def test_write_params_replaces_expanded_folders(tmp_path: Path) -> None:
    """write_params_from_iterator turns rendered folders into param files,
    preserves service_id via the sidecar, and prunes models the iterator drops."""
    specs = tmp_path / "specs"
    # An existing expanded render with an identity record (to be replaced).
    old = specs / "cohere" / "command-r"
    old.mkdir(parents=True)
    (old / "offering.json").write_text(json.dumps({"name": "command-r"}) + "\n")
    (old / "service.json").write_text(json.dumps({"service_id": "keep-me"}) + "\n")
    # A stale model the live iterator no longer yields.
    stale = specs / "cohere" / "gone"
    stale.mkdir(parents=True)
    (stale / "offering.json").write_text(json.dumps({"name": "gone"}) + "\n")

    def it():
        yield {
            "name": "cohere/command-r",
            "provider_name": "cohere",  # path-derived — must be stripped
            "offering_name": "command-r",
            "service_type": "llm",
        }

    stats = write_params_from_iterator(it(), specs)

    # Default keeps stale services (never lose a service_id).
    assert stats == {"total": 1, "written": 1, "errors": 0, "pruned": 0, "kept": 1}
    # Expanded folder replaced by a param file.
    assert not old.exists()
    param = specs / "cohere" / "command-r.json"
    payload = json.loads(param.read_text())
    assert "template" not in payload  # default templates/ root
    assert payload["parameters"] == {"offering_name": "command-r", "service_type": "llm"}
    assert "name" not in payload["parameters"] and "provider_name" not in payload["parameters"]
    # service_id lifted into the committed sidecar.
    sidecar = specs / "cohere" / "command-r.service.json"
    assert json.loads(sidecar.read_text())["service_id"] == "keep-me"
    # Stale model kept (curated / off-API) by default.
    assert stale.exists()
    # Keys are sorted with a trailing newline (format-clean).
    assert param.read_text().endswith("}\n")

    # Opt-in pruning deletes the stale folder.
    pruned = write_params_from_iterator(it(), specs, prune_missing=True)
    assert pruned["pruned"] == 1
    assert not stale.exists()


def test_validate_command_accepts_param_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _make_repo(
        tmp_path, params={"resp200": {"status": 200, "label": "OK"}, "resp404": {"status": 404, "label": "NF"}}
    )
    monkeypatch.chdir(root)
    from typer.testing import CliRunner

    from unitysvc_sellers.cli import app

    result = CliRunner().invoke(app, ["specs", "validate"])
    assert result.exit_code == 0, result.output
    assert "2 service folder(s) are valid" in result.output
    # no rendered folders left behind
    assert not (root / "specs" / "unitysvc" / "resp200").exists()
