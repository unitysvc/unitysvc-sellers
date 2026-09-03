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
    UpstreamEnumerationError,
    discover_system_param_files,
    materialized_param_specs,
    service_name_for_param,
    validate_system_param_file,
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
    assert discover_system_param_files(root) == [root / "specs" / "unitysvc" / "bad.json"]
    with materialized_param_specs(root) as rendered:
        assert len(rendered) == 1


def test_folder_and_param_file_conflict_raises(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    (root / "specs" / "unitysvc" / "resp200").mkdir()  # a folder at the same path
    with pytest.raises(ParamRenderError, match="a service is one or the other"):
        with materialized_param_specs(root):
            pass


def test_system_template_param_repo_materializes_without_local_renders(tmp_path: Path) -> None:
    (tmp_path / "templates").mkdir()
    specs = tmp_path / "specs" / "crofai"
    specs.mkdir(parents=True)
    param = specs / "deepseek-v3.2.json"
    param.write_text(json.dumps({"template": "llm-fast", "parameters": {"model": "deepseek-v3.2"}}) + "\n")
    outer_cwd = Path.cwd()

    with materialized_param_specs(tmp_path) as rendered:
        assert rendered == []
        assert Path.cwd() != outer_cwd

    assert Path.cwd() == outer_cwd
    assert discover_system_param_files(tmp_path) == [param]


def test_platform_param_service_name_comes_from_platform_services_path(tmp_path: Path) -> None:
    (tmp_path / "services" / "templates").mkdir(parents=True)
    param = tmp_path / "platform_services" / "llm-fast" / "crofai" / "deepseek-v3.2.json"
    param.parent.mkdir(parents=True)
    param.write_text(
        json.dumps(
            {
                "template": "llm-fast",
                "parameters": {"model": "deepseek-v3.2", "service_name": "llm-fast/crofai/deepseek-v3.2"},
            }
        )
        + "\n"
    )

    assert service_name_for_param(param) == "llm-fast/crofai/deepseek-v3.2"
    assert validate_system_param_file(param) == []


def test_platform_param_requires_service_name_to_match_path(tmp_path: Path) -> None:
    (tmp_path / "services" / "templates").mkdir(parents=True)
    param = tmp_path / "platform_services" / "llm-fast" / "crofai" / "deepseek-v3.2.json"
    param.parent.mkdir(parents=True)
    param.write_text(
        json.dumps(
            {
                "template": "llm-fast",
                "parameters": {"model": "deepseek-v3.2", "service_name": "crofai/deepseek-v3.2"},
            }
        )
        + "\n"
    )

    errors = validate_system_param_file(param)
    assert len(errors) == 1
    assert "parameters.service_name" in errors[0]
    assert "llm-fast/crofai/deepseek-v3.2" in errors[0]


def test_system_only_repo_materializes_for_sidecar_roundtrip(tmp_path: Path) -> None:
    (tmp_path / "services" / "templates").mkdir(parents=True)
    param = tmp_path / "platform_services" / "llm-fast" / "crofai" / "deepseek-v3.2.json"
    param.parent.mkdir(parents=True)
    param.write_text(
        json.dumps(
            {
                "template": "llm-fast",
                "parameters": {"model": "deepseek-v3.2", "service_name": "llm-fast/crofai/deepseek-v3.2"},
            }
        )
        + "\n"
    )
    outer_cwd = Path.cwd()

    with materialized_param_specs(tmp_path) as rendered:
        assert rendered == []
        assert Path.cwd() != outer_cwd
        sidecar = Path.cwd() / "platform_services" / "llm-fast" / "crofai" / "deepseek-v3.2.service.json"
        sidecar.write_text(json.dumps({"service_id": "new-id"}) + "\n")

    assert Path.cwd() == outer_cwd
    real_sidecar = tmp_path / "platform_services" / "llm-fast" / "crofai" / "deepseek-v3.2.service.json"
    assert json.loads(real_sidecar.read_text())["service_id"] == "new-id"


def test_write_params_replaces_expanded_folders(tmp_path: Path) -> None:
    """write_params_from_iterator turns rendered folders into param files,
    preserves service_id via the sidecar, and deprecates models the iterator
    no longer yields."""
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

    assert stats == {
        "total": 1,
        "written": 1,
        "new": 0,
        "preserved": 0,
        "errors": 0,
        "deprecated": 1,
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
    # The stale model is marked, never deleted: its service_id must survive so
    # the upload can retire the REMOTE service rather than orphaning it.
    assert stale.exists()
    assert json.loads((stale / "offering.json").read_text())["status"] == "deprecated"
    # Keys are sorted with a trailing newline (format-clean).
    assert param.read_text().endswith("}\n")


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
# The set of committed services is read from output_dir up front and drained as
# the iterator yields; whatever remains never appeared this run. Nothing is
# passed in: a model the script filters out is filtered on EVERY run, so it was
# never committed and cannot be in the remainder.
# ---------------------------------------------------------------------------


def _seed(specs: Path, names: list[str]) -> None:
    """Commit a param file per name, as a previous populate would have."""
    for n in names:
        p = specs / f"{n}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"parameters": {"offering_name": n.split("/", 1)[1], "status": "ready"}}) + "\n")


def _status_of(specs: Path, name: str) -> str | None:
    return json.loads((specs / f"{name}.json").read_text())["parameters"].get("status")


def _constants_of(path: Path) -> dict:
    return json.loads(path.read_text()).get("constants", {})


def _platform_param(root: Path, platform: str, regular_name: str, *, deprecated: bool = False) -> Path:
    p = root / "platform_services" / platform / f"{regular_name}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "parameters": {
            "model": regular_name.rsplit("/", 1)[-1],
            "payout_input": "1",
            "payout_output": "2",
            "service_name": f"{platform}/{regular_name}",
        },
        "template": platform,
    }
    if deprecated:
        payload["constants"] = {"status": "deprecated"}
    p.write_text(json.dumps(payload) + "\n")
    return p


def _iter(*names: str):
    def it():
        for n in names:
            yield {"service_name": n, "offering_name": n.split("/", 1)[1], "service_type": "llm"}

    return it()


def test_service_not_yielded_is_deprecated(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    _seed(specs, ["p/live", "p/retired"])

    stats = write_params_from_iterator(_iter("p/live"), specs)

    assert _status_of(specs, "p/retired") == "deprecated"
    assert _status_of(specs, "p/live") != "deprecated"
    assert stats["deprecated"] == 1
    assert stats["new"] == 0


def test_platform_params_are_drained_by_regular_service_path(tmp_path: Path) -> None:
    specs = tmp_path / "services" / "specs"
    _seed(specs, ["p/modelA"])
    fast = _platform_param(tmp_path, "llm-fast", "p/modelA", deprecated=True)
    mode_a = _platform_param(tmp_path, "llm-modeA", "p/modelA", deprecated=True)

    stats = write_params_from_iterator(_iter("p/modelA"), specs)

    assert stats["deprecated"] == 0
    assert _constants_of(fast) == {}
    assert _constants_of(mode_a) == {}
    assert json.loads(fast.read_text())["parameters"]["service_name"] == "llm-fast/p/modelA"
    assert json.loads(mode_a.read_text())["parameters"]["service_name"] == "llm-modeA/p/modelA"


def test_matching_platform_params_refresh_payout_from_payout_price(tmp_path: Path) -> None:
    specs = tmp_path / "services" / "specs"
    _seed(specs, ["p/modelA"])
    fast = _platform_param(tmp_path, "llm-fast", "p/modelA", deprecated=True)
    data = json.loads(fast.read_text())
    data["parameters"]["api_base_url"] = "https://platform.example/v1"
    fast.write_text(json.dumps(data) + "\n")

    def it():
        yield {
            "service_name": "p/modelA",
            "api_base_url": "https://regular.example",
            "offering_name": "modelA",
            "payout_price": {"input": "0.12", "output": "0.34"},
            "service_type": "llm",
        }

    stats = write_params_from_iterator(it(), specs)

    data = json.loads(fast.read_text())
    assert data["parameters"]["api_base_url"] == "https://platform.example/v1"
    assert data["parameters"]["payout_input"] == "0.12"
    assert data["parameters"]["payout_output"] == "0.34"
    assert data["parameters"]["service_name"] == "llm-fast/p/modelA"
    assert data.get("constants") is None
    assert stats["deprecated"] == 0


def test_matching_platform_params_refresh_payout_from_pricing(tmp_path: Path) -> None:
    specs = tmp_path / "services" / "specs"
    _seed(specs, ["p/modelA"])
    fast = _platform_param(tmp_path, "llm-fast", "p/modelA")

    def it():
        yield {
            "service_name": "p/modelA",
            "offering_name": "modelA",
            "pricing": {"cached_input": "0.02", "input": "0.20", "output": "0.80"},
            "service_type": "llm",
        }

    write_params_from_iterator(it(), specs)

    data = json.loads(fast.read_text())
    assert data["parameters"]["payout_input"] == "0.20"
    assert data["parameters"]["payout_output"] == "0.80"
    assert "payout_cached_input" not in data["parameters"]


def test_matching_platform_params_preserve_payout_when_new_price_unknown(tmp_path: Path) -> None:
    specs = tmp_path / "services" / "specs"
    _seed(specs, ["p/modelA"])
    fast = _platform_param(tmp_path, "llm-fast", "p/modelA")

    def it():
        yield {
            "service_name": "p/modelA",
            "offering_name": "modelA",
            "payout_price": {"input": None, "output": "0.34"},
            "service_type": "llm",
        }

    stats = write_params_from_iterator(it(), specs)

    data = json.loads(fast.read_text())
    assert data["parameters"]["payout_input"] == "1"
    assert data["parameters"]["payout_output"] == "0.34"
    assert stats["preserved"] == 1


def test_missing_platform_params_are_deprecated_in_constants(tmp_path: Path) -> None:
    specs = tmp_path / "services" / "specs"
    _seed(specs, ["p/modelA"])
    fast = _platform_param(tmp_path, "llm-fast", "p/modelB")
    mode_a = _platform_param(tmp_path, "llm-modeA", "p/modelB")

    stats = write_params_from_iterator(_iter("p/modelA"), specs)

    fast_data = json.loads(fast.read_text())
    mode_a_data = json.loads(mode_a.read_text())
    assert fast_data["constants"]["status"] == "deprecated"
    assert mode_a_data["constants"]["status"] == "deprecated"
    assert "status" not in fast_data["parameters"]
    assert "status" not in mode_a_data["parameters"]
    assert stats["deprecated"] == 2


def test_matching_no_committed_platform_params_raises(tmp_path: Path) -> None:
    specs = tmp_path / "services" / "specs"
    specs.mkdir(parents=True)
    _platform_param(tmp_path, "llm-fast", "p/modelA")

    with pytest.raises(UpstreamEnumerationError, match="failed populate"):
        write_params_from_iterator(_iter("q/modelB"), specs)


def test_a_brand_new_service_counts_as_new_not_deprecated(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    _seed(specs, ["p/live"])

    stats = write_params_from_iterator(_iter("p/live", "p/fresh"), specs)

    assert stats["new"] == 1
    assert stats["deprecated"] == 0


def test_matching_nothing_committed_raises(tmp_path: Path) -> None:
    """A populate that errored, authenticated wrongly, or hit an endpoint
    serving nobody's models looks exactly like a catalog that retired all at
    once. Only one of those is real."""
    from unitysvc_sellers.params_render import UpstreamEnumerationError

    specs = tmp_path / "specs"
    _seed(specs, ["p/a", "p/b"])

    with pytest.raises(UpstreamEnumerationError, match="failed populate"):
        write_params_from_iterator(_iter("q/x"), specs)


def test_yielding_nothing_at_all_raises(tmp_path: Path) -> None:
    from unitysvc_sellers.params_render import UpstreamEnumerationError

    specs = tmp_path / "specs"
    _seed(specs, ["p/a"])

    def empty():
        return
        yield  # pragma: no cover

    with pytest.raises(UpstreamEnumerationError):
        write_params_from_iterator(empty(), specs)


def test_first_run_on_an_empty_repo_is_not_a_failure(tmp_path: Path) -> None:
    """Nothing committed means nothing to explain — the guard must not fire."""
    specs = tmp_path / "specs"
    specs.mkdir()

    stats = write_params_from_iterator(_iter("p/first"), specs)

    assert stats["new"] == 1
    assert stats["deprecated"] == 0


def test_sidecars_and_override_companions_are_not_services(tmp_path: Path) -> None:
    """36 ``<name>.override.json`` companions exist across six repos; counting
    one as a service would deprecate it every run."""
    specs = tmp_path / "specs"
    _seed(specs, ["p/live"])
    (specs / "p" / "live.service.json").write_text(json.dumps({"service_id": "sid"}) + "\n")
    (specs / "p" / "live.override.json").write_text(json.dumps({"tool_calling": False}) + "\n")

    stats = write_params_from_iterator(_iter("p/live"), specs)

    assert stats["deprecated"] == 0
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

    write_params_from_iterator(_iter("p/live"), specs)

    assert json.loads((folder / "offering.json").read_text())["status"] == "deprecated"
    assert json.loads((folder / "listing.json").read_text())["status"] == "deprecated"


def test_deprecation_is_idempotent(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    _seed(specs, ["p/live", "p/retired"])

    first = write_params_from_iterator(_iter("p/live"), specs)
    before = (specs / "p" / "retired.json").read_text()
    second = write_params_from_iterator(_iter("p/live"), specs)

    assert first["deprecated"] == 1
    assert second["deprecated"] == 0
    assert second["already_deprecated"] == 1
    assert (specs / "p" / "retired.json").read_text() == before


def test_deprecate_missing_can_be_switched_off(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    _seed(specs, ["p/live", "p/retired"])

    stats = write_params_from_iterator(_iter("p/live"), specs, deprecate_missing=False)

    assert _status_of(specs, "p/retired") == "ready"
    assert stats["deprecated"] == 0


def test_name_that_would_be_sanitised_is_rejected(tmp_path: Path) -> None:
    """Silent sanitisation is what breaks name-to-path matching later: a future
    ``llama3:8b`` would land at ``llama3_8b`` and every comparison would miss."""
    specs = tmp_path / "specs"

    def it():
        yield {"service_name": "p/llama3:8b", "offering_name": "llama3:8b"}

    with pytest.raises(ParamRenderError, match="llama3:8b"):
        write_params_from_iterator(it(), specs)


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


# ---------------------------------------------------------------------------
# A null must never overwrite a value we already have.
#
# Enrichment metadata is fetched from third-party APIs over the network, and by
# the time a value reaches the iterator the reason for a None is gone: the HF
# lookup keeps only `status_code == 200`, so a 429, a timeout and a genuine 404
# all arrive as the same None. 45 parasail services had `parameter_count`
# silently nulled this way in one run, from values HuggingFace still serves.
#
# Since "unknown" cannot be told from "definitively nothing", the known value
# wins: it is strictly more informative than either.
# ---------------------------------------------------------------------------


def _committed(specs: Path, name: str, params: dict) -> Path:
    p = specs / f"{name}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"parameters": params}) + "\n")
    return p


def _params_of(specs: Path, name: str) -> dict:
    return json.loads((specs / f"{name}.json").read_text())["parameters"]


def test_null_does_not_overwrite_a_committed_value(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    _committed(specs, "p/m", {"offering_name": "m", "parameter_count": 27432406640})

    def it():
        yield {"service_name": "p/m", "offering_name": "m", "parameter_count": None}

    stats = write_params_from_iterator(it(), specs)

    assert _params_of(specs, "p/m")["parameter_count"] == 27432406640
    assert stats["preserved"] == 1


def test_null_preservation_reaches_nested_values(tmp_path: Path) -> None:
    """The enrichment that actually broke lives under `details`."""
    specs = tmp_path / "specs"
    _committed(
        specs,
        "p/m",
        {"offering_name": "m", "details": {"parameter_count": 27432406640, "context_length": 262144}},
    )

    def it():
        yield {
            "service_name": "p/m",
            "offering_name": "m",
            "details": {"parameter_count": None, "context_length": 131072},
        }

    write_params_from_iterator(it(), specs)

    d = _params_of(specs, "p/m")["details"]
    assert d["parameter_count"] == 27432406640, "unknown must not clobber known"
    assert d["context_length"] == 131072, "a real new value still wins"


def test_a_real_value_always_wins(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    _committed(specs, "p/m", {"offering_name": "m", "parameter_count": 1})

    def it():
        yield {"service_name": "p/m", "offering_name": "m", "parameter_count": 2}

    stats = write_params_from_iterator(it(), specs)

    assert _params_of(specs, "p/m")["parameter_count"] == 2
    assert stats["preserved"] == 0


def test_null_over_null_is_not_counted_as_preserved(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    _committed(specs, "p/m", {"offering_name": "m", "parameter_count": None})

    def it():
        yield {"service_name": "p/m", "offering_name": "m", "parameter_count": None}

    stats = write_params_from_iterator(it(), specs)

    assert _params_of(specs, "p/m")["parameter_count"] is None
    assert stats["preserved"] == 0


def test_a_new_service_keeps_its_nulls(tmp_path: Path) -> None:
    """Nothing committed means nothing to preserve — null is the value."""
    specs = tmp_path / "specs"

    def it():
        yield {"service_name": "p/fresh", "offering_name": "fresh", "parameter_count": None}

    stats = write_params_from_iterator(it(), specs)

    assert _params_of(specs, "p/fresh")["parameter_count"] is None
    assert stats["preserved"] == 0


def test_the_override_companion_is_not_consulted(tmp_path: Path) -> None:
    """Overrides are merged at RENDER time, not baked into the param file; if a
    value came from the override the param file must not silently absorb it."""
    specs = tmp_path / "specs"
    _committed(specs, "p/m", {"offering_name": "m", "parameter_count": None})
    (specs / "p" / "m.override.json").write_text(json.dumps({"parameters": {"parameter_count": 999}}) + "\n")

    def it():
        yield {"service_name": "p/m", "offering_name": "m", "parameter_count": None}

    write_params_from_iterator(it(), specs)

    assert _params_of(specs, "p/m")["parameter_count"] is None
