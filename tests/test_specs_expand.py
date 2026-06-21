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


def test_expand_resolves_presets_by_default(tmp_path: Path) -> None:
    """Expand resolves ``$doc_preset`` by default — no flag needed."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_preset_repo(tmp_path)
    folder = expand_param_file(root / "specs" / "unitysvc" / "p1.json")

    record = json.loads((folder / "listing.json").read_text())["documents"]["Connectivity"]
    assert "$doc_preset" not in json.dumps(record)


def test_expand_materializes_preset_doc_locally(tmp_path: Path) -> None:
    """The resolved preset doc is copied in with a folder-local ``file_path`` so the
    render is self-contained."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_preset_repo(tmp_path)
    folder = expand_param_file(root / "specs" / "unitysvc" / "p1.json")

    listing = json.loads((folder / "listing.json").read_text())
    record = listing["documents"]["Connectivity"]

    # Sentinel resolved away, file_path now points at a local sibling that exists.
    assert "$doc_preset" not in json.dumps(record)
    assert not Path(record["file_path"]).is_absolute()
    assert (folder / record["file_path"]).is_file()


# A connectivity probe that branches on local_testing: local mode hits the
# upstream (Jinja `service_base_url`), gateway mode hits the gateway (shell env).
_CONNECTIVITY_BRANCHING_J2 = (
    "{% if local_testing %}curl {{ service_base_url }}/healthz"
    "{% else %}curl ${SERVICE_BASE_URL}/healthz{% endif %}\n"
)


def test_render_tests_writes_local_and_gateway_variants(tmp_path: Path) -> None:
    """expand renders each test .j2 in both modes as suffix siblings."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_repo(tmp_path)
    (root / "templates" / "resp" / "connectivity.sh.j2").write_text(_CONNECTIVITY_BRANCHING_J2)

    folder = expand_param_file(root / "specs" / "unitysvc" / "resp200.json")

    # Raw template is kept; both variants are rendered beside it.
    assert (folder / "connectivity.sh.j2").is_file()
    local = (folder / "connectivity.local.sh").read_text()
    gateway = (folder / "connectivity.gateway.sh").read_text()
    # Local mode resolves the upstream base_url from the offering; gateway mode
    # keeps the shell placeholder the real gateway test uses.
    assert local.strip() == "curl resp://200/healthz"
    assert gateway.strip() == "curl ${SERVICE_BASE_URL}/healthz"


def test_render_tests_always_writes_both_variants(tmp_path: Path) -> None:
    """Both .local and .gateway are always written — even for a static test with no
    mode difference — so the two are predictable and never collapsed away."""
    from unitysvc_sellers.params_render import expand_param_file

    root = _make_repo(tmp_path)
    (root / "templates" / "resp" / "connectivity.sh.j2").write_text("echo ok\n")

    folder = expand_param_file(root / "specs" / "unitysvc" / "resp200.json")

    assert (folder / "connectivity.local.sh").read_text().strip() == "echo ok"
    assert (folder / "connectivity.gateway.sh").read_text().strip() == "echo ok"


def test_render_tests_local_vs_gateway_service_base_url(tmp_path: Path) -> None:
    """`service_base_url` differs by mode: local = the offering's upstream, gateway =
    the listing's user_access_interface (with {{ service_name }} resolved) — matching
    how the backend renders gateway tests."""
    from unitysvc_sellers.params_render import expand_service_folder

    root = _make_folder_service(tmp_path)
    svc = root / "specs" / "labs" / "svc1"
    listing = json.loads((svc / "listing.json").read_text())
    listing["user_access_interfaces"] = {
        "canonical": {"access_method": "http", "base_url": "${API_GATEWAY_BASE_URL}/{{ service_name }}"}
    }
    listing["documents"] = {"C": {"category": "connectivity_test", "file_path": "connectivity.sh.j2"}}
    (svc / "listing.json").write_text(json.dumps(listing))
    (svc / "connectivity.sh.j2").write_text("curl {{ service_base_url }}/health\n")

    folder = expand_service_folder(svc)

    # local → the offering's upstream base_url; gateway → the gateway URL, service_name resolved.
    assert (folder / "connectivity.local.sh").read_text().strip() == "curl https://up.labs.test/health"
    assert (folder / "connectivity.gateway.sh").read_text().strip() == "curl ${API_GATEWAY_BASE_URL}/labs/svc1/health"


def _make_folder_service(tmp_path: Path) -> Path:
    """A hand-authored flat service folder (specs/<name>/), no param/template."""
    svc = tmp_path / "specs" / "labs" / "svc1"
    svc.mkdir(parents=True)
    (svc / "provider.json").write_text(
        json.dumps(
            {
                "name": "labs",
                "display_name": "Labs",
                "homepage": "https://labs.test/",
                "contact_email": "x@labs.test",
                "status": "ready",
                "time_created": "2026-05-31T00:00:00Z",
            }
        )
        + "\n"
    )
    (svc / "offering.json").write_text(
        json.dumps(
            {
                "name": "labs/svc1",
                "service_type": "gateway",
                "capabilities": ["http_relay"],
                "description": "d",
                "status": "ready",
                "tags": ["t"],
                "time_created": "2026-05-31T00:00:00Z",
                "upstream_access_config": {"direct": {"access_method": "http", "base_url": "https://up.labs.test"}},
            }
        )
        + "\n"
    )
    (svc / "listing.json").write_text(
        json.dumps(
            {
                "name": "labs/svc1",
                "display_name": "Svc1",
                "currency": "USD",
                "status": "ready",
                "list_price": {"type": "constant", "price": "0", "description": "F"},
                "user_access_interfaces": {
                    "direct": {"access_method": "http", "base_url": "${API_GATEWAY_BASE_URL}/labs/svc1"}
                },
            }
        )
        + "\n"
    )
    return tmp_path


def test_expand_service_folder_copies_to_expanded_tree(tmp_path: Path) -> None:
    """expand also works on a hand-authored specs/<name>/ folder (not a param file)."""
    from unitysvc_sellers.params_render import expand_service_folder

    root = _make_folder_service(tmp_path)

    folder = expand_service_folder(root / "specs" / "labs" / "svc1")

    assert folder == root / "expanded" / "labs" / "svc1"
    for f in ("provider.json", "offering.json", "listing.json"):
        assert (folder / f).is_file()
    assert json.loads((folder / "listing.json").read_text())["name"] == "labs/svc1"
    # Source folder untouched; no identity record leaks into the inspection tree.
    assert (root / "specs" / "labs" / "svc1" / "listing.json").is_file()
    assert not (folder / "service.json").exists()


def test_expand_service_folder_renders_tests(tmp_path: Path) -> None:
    """Folder services get the same local/gateway test rendering."""
    from unitysvc_sellers.params_render import expand_service_folder

    root = _make_folder_service(tmp_path)
    (root / "specs" / "labs" / "svc1" / "connectivity.sh.j2").write_text(_CONNECTIVITY_BRANCHING_J2)

    folder = expand_service_folder(root / "specs" / "labs" / "svc1")

    assert (folder / "connectivity.local.sh").read_text().strip() == "curl https://up.labs.test/healthz"
    assert (folder / "connectivity.gateway.sh").read_text().strip() == "curl ${SERVICE_BASE_URL}/healthz"


def test_expand_inlines_shared_relative_docs(tmp_path: Path) -> None:
    """Base expand pulls a doc referenced by a relative path *outside* the service
    dir into the folder and rewrites the ref to its basename — self-contained."""
    from unitysvc_sellers.params_render import expand_service_folder

    root = _make_folder_service(tmp_path)
    shared = root / "specs" / "labs" / "_docs"
    shared.mkdir()
    (shared / "connectivity.sh.j2").write_text("echo shared\n")
    listing_path = root / "specs" / "labs" / "svc1" / "listing.json"
    listing = json.loads(listing_path.read_text())
    listing["documents"] = {
        "C": {"category": "connectivity_test", "file_path": "../_docs/connectivity.sh.j2", "mime_type": "bash"}
    }
    listing_path.write_text(json.dumps(listing))

    folder = expand_service_folder(root / "specs" / "labs" / "svc1")  # no flags

    assert (folder / "connectivity.sh.j2").read_text() == "echo shared\n"
    rec = json.loads((folder / "listing.json").read_text())["documents"]["C"]
    assert rec["file_path"] == "connectivity.sh.j2"
    # Source is untouched.
    assert (shared / "connectivity.sh.j2").is_file()


def test_expand_tests_renders_inlined_shared_doc(tmp_path: Path) -> None:
    """A shared relative doc is a *local* test — expand inlines it and renders
    both variants from it."""
    from unitysvc_sellers.params_render import expand_service_folder

    root = _make_folder_service(tmp_path)
    shared = root / "specs" / "labs" / "_docs"
    shared.mkdir()
    (shared / "connectivity.sh.j2").write_text(_CONNECTIVITY_BRANCHING_J2)
    listing_path = root / "specs" / "labs" / "svc1" / "listing.json"
    listing = json.loads(listing_path.read_text())
    listing["documents"] = {"C": {"category": "connectivity_test", "file_path": "../_docs/connectivity.sh.j2"}}
    listing_path.write_text(json.dumps(listing))

    folder = expand_service_folder(root / "specs" / "labs" / "svc1")

    assert (folder / "connectivity.local.sh").read_text().strip() == "curl https://up.labs.test/healthz"
    assert (folder / "connectivity.gateway.sh").read_text().strip() == "curl ${SERVICE_BASE_URL}/healthz"


def test_local_variant_rewrites_secret_refs_to_env_form(tmp_path: Path) -> None:
    """The local variant must not leak ``${ customer_secrets.X }`` — local run-tests
    pulls secrets from env vars, so rewrite to env-var form (``${X}`` / ``${X:-default}``).
    The gateway variant keeps them (the gateway resolves them server-side)."""
    from unitysvc_sellers.params_render import expand_service_folder

    root = _make_folder_service(tmp_path)
    svc = root / "specs" / "labs" / "svc1"
    offering = json.loads((svc / "offering.json").read_text())
    offering["upstream_access_config"] = {
        "apprise": {
            "access_method": "http",
            "base_url": "${ customer_secrets.APPRISE_BASE ?? https://apprise.unitysvc.dev }/notify",
        }
    }
    (svc / "offering.json").write_text(json.dumps(offering))
    listing = json.loads((svc / "listing.json").read_text())
    listing["documents"] = {"C": {"category": "connectivity_test", "file_path": "connectivity.sh.j2"}}
    (svc / "listing.json").write_text(json.dumps(listing))
    (svc / "connectivity.sh.j2").write_text(
        'curl "{{ service_base_url }}" -H "X-Token: ${ customer_secrets.TOKEN }"\n'
    )

    folder = expand_service_folder(svc)

    local = (folder / "connectivity.local.sh").read_text()
    assert "customer_secrets" not in local
    assert "${APPRISE_BASE:-https://apprise.unitysvc.dev}/notify" in local  # ?? default → shell default
    assert "${TOKEN}" in local  # no default → plain env var
    # Gateway keeps the reference — the gateway injects customer secrets at request time.
    assert "${ customer_secrets.TOKEN }" in (folder / "connectivity.gateway.sh").read_text()


def test_expand_service_folder_with_presets(tmp_path: Path) -> None:
    """A folder service that uses a $doc_preset gets it resolved + localized too."""
    from unitysvc_sellers.params_render import expand_service_folder

    root = _make_folder_service(tmp_path)
    listing_path = root / "specs" / "labs" / "svc1" / "listing.json"
    listing = json.loads(listing_path.read_text())
    listing["documents"] = {"Connectivity": {"$doc_preset": "s3_connectivity_v1"}}
    listing_path.write_text(json.dumps(listing))

    folder = expand_service_folder(root / "specs" / "labs" / "svc1")  # presets resolve by default

    record = json.loads((folder / "listing.json").read_text())["documents"]["Connectivity"]
    assert "$doc_preset" not in json.dumps(record)
    assert (folder / record["file_path"]).is_file()


def test_expand_unknown_preset_is_best_effort(tmp_path: Path) -> None:
    """An unknown $doc_preset is best-effort: warn and leave the sentinel as-authored,
    never fail — so a plain expand still gives you an inspection view."""
    from unitysvc_sellers.params_render import expand_service_folder

    root = _make_folder_service(tmp_path)
    listing_path = root / "specs" / "labs" / "svc1" / "listing.json"
    listing = json.loads(listing_path.read_text())
    listing["documents"] = {"C": {"$doc_preset": "nonexistent_preset_xyz"}}
    listing_path.write_text(json.dumps(listing))

    folder = expand_service_folder(root / "specs" / "labs" / "svc1")  # does not raise

    record = json.loads((folder / "listing.json").read_text())["documents"]["C"]
    assert record == {"$doc_preset": "nonexistent_preset_xyz"}  # left as authored


def test_expand_command_unknown_preset_warns_but_succeeds(tmp_path: Path) -> None:
    root = _make_folder_service(tmp_path)
    listing_path = root / "specs" / "labs" / "svc1" / "listing.json"
    listing = json.loads(listing_path.read_text())
    listing["documents"] = {"C": {"$doc_preset": "nonexistent_preset_xyz"}}
    listing_path.write_text(json.dumps(listing))

    result = runner.invoke(specs_app, ["expand", "labs/svc1", "-d", str(root)])

    assert result.exit_code == 0, result.output
    assert "Traceback" not in result.output
    assert "could not resolve presets" in result.output


def test_expand_command_works_on_folder_service(tmp_path: Path) -> None:
    root = _make_folder_service(tmp_path)

    result = runner.invoke(specs_app, ["expand", "labs/svc1", "-d", str(root)])

    assert result.exit_code == 0, result.output
    assert (root / "expanded" / "labs" / "svc1" / "listing.json").is_file()


def test_expand_command_renders_tests_by_default(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    (root / "templates" / "resp" / "connectivity.sh.j2").write_text(_CONNECTIVITY_BRANCHING_J2)

    result = runner.invoke(specs_app, ["expand", "unitysvc/resp200", "-d", str(root)])  # no flags

    assert result.exit_code == 0, result.output
    folder = root / "expanded" / "unitysvc" / "resp200"
    assert (folder / "connectivity.local.sh").is_file()
    assert (folder / "connectivity.gateway.sh").is_file()


def test_expand_command_renders_and_reports(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)

    result = runner.invoke(specs_app, ["expand", "unitysvc/resp200", "-d", str(root)])

    assert result.exit_code == 0, result.output
    folder = root / "expanded" / "unitysvc" / "resp200"
    assert (folder / "listing.json").is_file()
    # The folder path is reported (rich may soft-wrap it, so compare whitespace-free).
    assert str(folder) in "".join(result.output.split())


def test_expand_command_resolves_presets(tmp_path: Path) -> None:
    root = _make_preset_repo(tmp_path)

    result = runner.invoke(specs_app, ["expand", "unitysvc/p1", "-d", str(root)])  # no flags

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
