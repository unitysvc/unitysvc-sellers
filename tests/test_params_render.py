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
            "service_name": "cohere/command-r",
            "provider_name": "cohere",  # path-derived — must be stripped
            "offering_name": "command-r",
            "service_type": "llm",
        }

    stats = write_params_from_iterator(it(), specs)

    # Default keeps stale services (never lose a service_id).
    assert stats == {
        "total": 1,
        "written": 1,
        "errors": 0,
        "pruned": 0,
        "kept": 1,
        # Reported unconditionally so the shape does not depend on whether
        # upstream_names was passed; both stay 0 without it.
        "deprecated": 0,
        "already_deprecated": 0,
    }
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


def test_failed_artifacts_land_in_invocation_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Debug artifacts from a failed test must survive the ephemeral render.

    ``specs run-tests`` writes failed_* (script/.out/.err/.env) "to the current
    directory" — but for a param repo the whole command runs chdir'd into the
    ephemeral copy, so relative writes landed in the temp dir and were deleted
    with it. They must land in the directory the user invoked the CLI from.
    """
    root = _make_repo(tmp_path, params={"resp200": {"status": 200, "label": "OK"}})
    # Make the connectivity test fail so the artifact block runs.
    (root / "templates" / "resp" / "connectivity.sh.j2").write_text("echo boom >&2\nexit 1\n")
    monkeypatch.chdir(root)
    from typer.testing import CliRunner

    from unitysvc_sellers.cli import app

    result = CliRunner().invoke(app, ["specs", "run-tests", "unitysvc/resp200"])
    # The command reports failure via its summary; artifacts must be in root.
    artifacts = sorted(p.name for p in root.glob("failed_*"))
    assert artifacts, f"no failed_* artifacts in invocation cwd; output:\n{result.output}"
    stems = {p.suffix for p in root.glob("failed_*")}
    assert {".out", ".err", ".env"} <= stems, artifacts


# ---------------------------------------------------------------------------
# Deprecating models the upstream no longer serves (#181).
#
# The comparison is committed local service names against the provider's RAW,
# pre-filter enumeration. What the iterator yielded is never consulted: it
# yields post-filter models, so matching on it would deprecate every family a
# script deliberately drops.
# ---------------------------------------------------------------------------


def _seed(specs: Path, names: list[str]) -> None:
    """Commit a param file per name, as a previous populate would have."""
    for n in names:
        p = specs / f"{n}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"parameters": {"offering_name": n.split("/", 1)[1], "status": "ready"}}) + "\n")


def _status_of(specs: Path, name: str) -> str | None:
    return json.loads((specs / f"{name}.json").read_text())["parameters"].get("status")


def _iter(*names: str):
    def it():
        for n in names:
            yield {"service_name": n, "offering_name": n.split("/", 1)[1], "service_type": "llm"}

    return it()


def test_absent_from_enumeration_is_deprecated(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    _seed(specs, ["p/live", "p/retired"])

    stats = write_params_from_iterator(
        _iter("p/live"),
        specs,
        upstream_names={"p/live"},  # p/retired is gone upstream
    )

    assert _status_of(specs, "p/retired") == "deprecated"
    assert _status_of(specs, "p/live") != "deprecated"
    assert stats["deprecated"] == 1


def test_filtered_but_still_upstream_is_untouched(tmp_path: Path) -> None:
    """The defect a naive fix ships: iterators yield POST-filter models.

    ``p/filtered`` is committed and still served upstream, but the script
    filters it out of what it yields. Comparing against the iterator would
    deprecate it; comparing against the enumeration must not.
    """
    specs = tmp_path / "specs"
    _seed(specs, ["p/live", "p/filtered"])

    stats = write_params_from_iterator(
        _iter("p/live"),  # yields only p/live
        specs,
        upstream_names={"p/live", "p/filtered"},  # but BOTH are served
    )

    assert _status_of(specs, "p/filtered") == "ready"
    assert stats["deprecated"] == 0


def test_disjoint_enumeration_raises_and_writes_nothing(tmp_path: Path) -> None:
    """Zero overlap is a broken call — wrong key, wrong tier, wholesale rename —
    not a catalog that retired all at once."""
    from unitysvc_sellers.params_render import UpstreamEnumerationError

    specs = tmp_path / "specs"
    _seed(specs, ["p/a", "p/b"])

    with pytest.raises(UpstreamEnumerationError):
        write_params_from_iterator(_iter("p/a"), specs, upstream_names={"q/x", "q/y"})

    assert _status_of(specs, "p/a") == "ready"
    assert _status_of(specs, "p/b") == "ready"


def test_empty_enumeration_raises(tmp_path: Path) -> None:
    from unitysvc_sellers.params_render import UpstreamEnumerationError

    specs = tmp_path / "specs"
    _seed(specs, ["p/a"])

    with pytest.raises(UpstreamEnumerationError):
        write_params_from_iterator(_iter("p/a"), specs, upstream_names=set())

    assert _status_of(specs, "p/a") == "ready"


def test_sidecars_and_override_companions_are_not_services(tmp_path: Path) -> None:
    """36 ``<name>.override.json`` companions exist across six repos; a naive
    ``*.json`` glob deprecates every one of them."""
    specs = tmp_path / "specs"
    _seed(specs, ["p/live"])
    (specs / "p" / "live.service.json").write_text(json.dumps({"service_id": "sid"}) + "\n")
    (specs / "p" / "live.override.json").write_text(json.dumps({"tool_calling": False}) + "\n")

    stats = write_params_from_iterator(_iter("p/live"), specs, upstream_names={"p/live"})

    assert stats["deprecated"] == 0
    # Companions untouched — no status injected, still valid JSON of their own shape.
    assert json.loads((specs / "p" / "live.service.json").read_text()) == {"service_id": "sid"}
    assert json.loads((specs / "p" / "live.override.json").read_text()) == {"tool_calling": False}


def test_expanded_folder_contributes_its_name(tmp_path: Path) -> None:
    """One repo (cohere) still holds an un-migrated expanded folder. It shares
    the service-name namespace, so it needs no special case."""
    specs = tmp_path / "specs"
    _seed(specs, ["p/live"])
    folder = specs / "p" / "old-shape"
    folder.mkdir(parents=True)
    (folder / "offering.json").write_text(json.dumps({"name": "old-shape", "status": "ready"}) + "\n")
    (folder / "listing.json").write_text(json.dumps({"name": "p/old-shape", "status": "ready"}) + "\n")

    write_params_from_iterator(_iter("p/live"), specs, upstream_names={"p/live"})

    assert json.loads((folder / "offering.json").read_text())["status"] == "deprecated"
    assert json.loads((folder / "listing.json").read_text())["status"] == "deprecated"


def test_deprecation_is_idempotent(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    _seed(specs, ["p/live", "p/retired"])

    first = write_params_from_iterator(_iter("p/live"), specs, upstream_names={"p/live"})
    before = (specs / "p" / "retired.json").read_text()
    second = write_params_from_iterator(_iter("p/live"), specs, upstream_names={"p/live"})

    assert first["deprecated"] == 1
    assert second["deprecated"] == 0
    assert second["already_deprecated"] == 1
    assert (specs / "p" / "retired.json").read_text() == before


def test_name_that_would_be_sanitised_is_rejected(tmp_path: Path) -> None:
    """Silent sanitisation is what breaks name-to-path matching later: a future
    ``llama3:8b`` would land at ``llama3_8b`` and every comparison would miss."""
    specs = tmp_path / "specs"

    def it():
        yield {"service_name": "p/llama3:8b", "offering_name": "llama3:8b"}

    with pytest.raises(ParamRenderError, match="llama3:8b"):
        write_params_from_iterator(it(), specs)


def test_no_upstream_names_leaves_behaviour_unchanged(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    _seed(specs, ["p/live", "p/retired"])

    stats = write_params_from_iterator(_iter("p/live"), specs)

    assert _status_of(specs, "p/retired") == "ready"
    assert stats["deprecated"] == 0


def test_service_name_is_required(tmp_path: Path) -> None:
    """No fallback key and no silent skip.

    A dropped service disappears from the catalog on the next upload, and now
    that absence drives deprecation, a populator that forgets the key could
    retire a live service for no other reason.
    """
    specs = tmp_path / "specs"

    def it():
        yield {"name": "p/legacy-key", "offering_name": "legacy-key"}

    with pytest.raises(ParamRenderError, match="service_name"):
        write_params_from_iterator(it(), specs)

    assert not (specs / "p" / "legacy-key.json").exists()
