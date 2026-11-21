"""``specs upload --state``: skip what has not changed since its ingest last completed.

The state file keeps, per service, the fingerprint of the EXPANDED content last sent and the result of its
ingest task. These tests cover the file (`unitysvc_sellers.state`), the side-effect-free fingerprint
(`ContentHasher`, `_service_digest`) and `upload_directory` driven by a fake client, so the outcome of each
ingest and the target's list of services can be chosen.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from unitysvc_sellers.state import (
    KIND_SERVICE,
    STATE_VERSION,
    ServiceRecord,
    UploadState,
    canonical_digest,
)
from unitysvc_sellers.storage import ContentHasher, upload_file
from unitysvc_sellers.upload import _service_digest, upload_directory

TARGET = "https://seller.test/v1"


# ---------------------------------------------------------------------------
# A catalog on disk and a client that is not one
# ---------------------------------------------------------------------------


def _write_service(
    provider_dir: Path, svc: str, *, price: str = "1.00", extra_listing: dict[str, Any] | None = None
) -> Path:
    service_dir = provider_dir / svc
    service_dir.mkdir(parents=True, exist_ok=True)
    (service_dir / "provider.json").write_text(
        json.dumps(
            {
                "name": provider_dir.name,
                "display_name": "Acme",
                "contact_email": "ops@acme.example",
                "homepage": "https://acme.example",
                "status": "ready",
            }
        )
    )
    (service_dir / "offering.json").write_text(
        json.dumps(
            {
                "name": svc,
                "display_name": svc,
                "service_type": "llm",
                "summary": "Test offering summary.",
                "description": "Test offering description.",
                "status": "ready",
                "upstream_access_config": {
                    "default": {"access_method": "http", "base_url": "https://api.acme.example"}
                },
            }
        )
    )
    listing = {
        "name": f"{provider_dir.name}/{svc}",
        "display_name": svc,
        "status": "ready",
        "list_price": {"type": "constant", "price": price},
        **(extra_listing or {}),
    }
    (service_dir / "listing.json").write_text(json.dumps(listing))
    return service_dir


class _FakeServices:
    def __init__(self, owner: _FakeClient) -> None:
        self._owner = owner

    def upload(self, payload: dict[str, Any], auto_submit: bool = False) -> SimpleNamespace:
        name = payload["data"]["listing_data"]["name"]
        self._owner.uploads.append((name, auto_submit))
        task_id = f"task-{len(self._owner.uploads)}"
        self._owner.tasks_by_id[task_id] = name
        return SimpleNamespace(task_id=task_id)

    def create_from_template(
        self, template_id: str, *, parameters: dict[str, Any], name: str, auto_submit: bool, service_id: str | None
    ) -> SimpleNamespace:
        self._owner.uploads.append((name, auto_submit))
        task_id = f"task-{len(self._owner.uploads)}"
        self._owner.tasks_by_id[task_id] = name
        return SimpleNamespace(task_id=task_id)

    def iter_all(self, limit: int = 200) -> list[SimpleNamespace]:
        if self._owner.list_fails:
            raise RuntimeError("listing is down")
        return [SimpleNamespace(name=n) for n in sorted(self._owner.remote_names)]


class _FakeTasks:
    def __init__(self, owner: _FakeClient) -> None:
        self._owner = owner

    def wait(self, *task_ids: str, **_: Any) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for task_id in task_ids:
            name = self._owner.tasks_by_id[task_id]
            if name in self._owner.failing:
                out[task_id] = {"status": "failed", "error": "ValueError: refused by ingest"}
            else:
                self._owner.remote_names.add(name)
                out[task_id] = {
                    "status": "completed",
                    "result": {"service_id": f"id-{name}", "status": "created"},
                }
        return out


class _FakeTemplates:
    def list(self, limit: int = 500) -> dict[str, Any]:
        return {"data": [{"id": "11111111-1111-1111-1111-111111111111", "name": "llm-fast"}]}


class _FakeClient:
    """Just what ``upload_directory`` uses: ``services.upload``, ``services.iter_all``, ``tasks.wait``."""

    def __init__(self) -> None:
        self._base_url = TARGET
        self._client = object()
        self.uploads: list[tuple[str, bool]] = []
        self.tasks_by_id: dict[str, str] = {}
        self.remote_names: set[str] = set()
        self.failing: set[str] = set()
        self.list_fails = False
        self.services = _FakeServices(self)
        self.tasks = _FakeTasks(self)
        self.templates = _FakeTemplates()

    @property
    def sent(self) -> list[str]:
        return [name for name, _ in self.uploads]


def _run(client: _FakeClient, root: Path, state: Path, **kwargs: Any) -> Any:
    # A real run is one process; here several runs share one, and core caches its scans of the catalog.
    import unitysvc_core.utils as core_utils

    for cached in vars(core_utils).values():
        if hasattr(cached, "cache_clear"):
            cached.cache_clear()
    return upload_directory(client, root, state_path=state, task_poll_interval=0.001, task_wait_timeout=5.0, **kwargs)  # type: ignore[arg-type]


@pytest.fixture
def catalog(tmp_path: Path) -> Path:
    provider = tmp_path / "acme"
    for svc in ("a", "b", "c"):
        _write_service(provider, svc)
    return tmp_path


# ---------------------------------------------------------------------------
# The state file
# ---------------------------------------------------------------------------


class TestStateFile:
    def _record(self, **kw: Any) -> ServiceRecord:
        base: dict[str, Any] = {
            "kind": KIND_SERVICE,
            "payload_sha256": "d1",
            "submitted": False,
            "ingest": {"status": "completed", "outcome": "created"},
            "service_id": "id-1",
        }
        base.update(kw)
        return ServiceRecord(**base)

    def test_a_missing_file_is_a_first_run(self, tmp_path: Path) -> None:
        state, ignored = UploadState.load(tmp_path / "state.json", TARGET)
        assert state.services == {} and ignored is None

    def test_round_trip_and_atomic_write(self, tmp_path: Path) -> None:
        path = tmp_path / "sub" / "state.json"
        state = UploadState(target=TARGET)
        state.services["acme/a"] = self._record()
        state.save(path)

        loaded, ignored = UploadState.load(path, TARGET + "/")  # a trailing slash is the same target
        assert ignored is None
        assert loaded.services["acme/a"].payload_sha256 == "d1"
        assert [p.name for p in path.parent.iterdir()] == ["state.json"], "no temp file left behind"
        document = json.loads(path.read_text())
        assert document["version"] == STATE_VERSION and document["target"] == TARGET

    @pytest.mark.parametrize(
        "content, why",
        [
            ("not json", "cannot be read"),
            ('["a list"]', "cannot be read"),
            (json.dumps({"version": 99, "target": TARGET, "services": {}}), "version"),
            (json.dumps({"version": STATE_VERSION, "target": "https://other/v1", "services": {}}), "not"),
        ],
    )
    def test_an_unusable_file_is_ignored_not_trusted(self, tmp_path: Path, content: str, why: str) -> None:
        path = tmp_path / "state.json"
        path.write_text(content)
        state, ignored = UploadState.load(path, TARGET)
        assert state.services == {}
        assert ignored is not None and why in ignored

    def test_is_current_needs_every_condition(self) -> None:
        state = UploadState(target=TARGET, services={"s": self._record()})

        def current(**kw: Any) -> bool:
            args: dict[str, Any] = {"kind": KIND_SERVICE, "digest": "d1", "sidecar_id": None, "submit": False}
            args.update(kw)
            return state.is_current("s", **args)

        assert current()
        assert not current(digest="d2"), "the content changed"
        assert not current(kind="system"), "another kind of upload"
        assert not state.is_current("unknown", kind=KIND_SERVICE, digest="d1", sidecar_id=None, submit=False)
        assert not current(submit=True), "left as a draft by a run that did not submit"
        assert current(sidecar_id="id-1"), "the sidecar agrees"
        assert not current(sidecar_id="id-other"), "the sidecar names another service"
        assert current(sidecar_id=None), "no sidecar (a CI run) is not a difference"

    def test_a_failed_ingest_is_never_current(self) -> None:
        state = UploadState(target=TARGET)
        state.record_failed("s", kind=KIND_SERVICE, digest="d1", submitted=False, error="boom " * 200)
        assert not state.is_current("s", kind=KIND_SERVICE, digest="d1", sidecar_id=None, submit=False)
        assert len(state.services["s"].ingest["error"]) <= 400

    def test_a_failure_keeps_the_known_service_id(self) -> None:
        state = UploadState(target=TARGET, services={"s": self._record()})
        state.record_failed("s", kind=KIND_SERVICE, digest="d2", submitted=False, error="x")
        assert state.services["s"].service_id == "id-1"

    def test_prune_drops_only_what_left_the_catalog(self) -> None:
        state = UploadState(target=TARGET, services={"keep": self._record(), "gone": self._record()})
        assert state.prune({"keep"}) == 1
        assert list(state.services) == ["keep"]

    def test_digest_is_canonical(self) -> None:
        assert canonical_digest({"a": 1, "b": [1, 2]}) == canonical_digest({"b": [1, 2], "a": 1})
        assert canonical_digest({"a": 1}) != canonical_digest({"a": 2})


# ---------------------------------------------------------------------------
# The fingerprint: expanded content, no requests
# ---------------------------------------------------------------------------


class TestFingerprint:
    def test_hasher_keys_are_content_hashes_and_make_no_request(self, tmp_path: Path) -> None:
        f = tmp_path / "probe.sh"
        f.write_bytes(b"echo ok\n")
        key = upload_file(ContentHasher(), f)  # type: ignore[arg-type]
        assert key == upload_file(ContentHasher(), f)  # type: ignore[arg-type]
        f.write_bytes(b"echo changed\n")
        assert upload_file(ContentHasher(), f) != key  # type: ignore[arg-type]
        assert key.endswith(".sh")

    def test_markdown_key_covers_the_assets_it_links(self, tmp_path: Path) -> None:
        image = tmp_path / "shot.png"
        image.write_bytes(b"\x89PNG one")
        doc = tmp_path / "guide.md"
        doc.write_text("# Guide\n\n![shot](shot.png)\n")
        before = upload_file(ContentHasher(), doc)  # type: ignore[arg-type]
        image.write_bytes(b"\x89PNG two")
        after = upload_file(ContentHasher(), doc)  # type: ignore[arg-type]
        assert before != after, "a changed image changes the document that links it"

    def test_service_digest_follows_content_not_files(self, tmp_path: Path) -> None:
        service_dir = _write_service(
            tmp_path / "acme",
            "a",
            extra_listing={
                "documents": {
                    "Guide": {
                        "category": "getting_started",
                        "mime_type": "markdown",
                        "file_path": "guide.md",
                        "is_public": True,
                    }
                }
            },
        )
        (service_dir / "guide.md").write_text("# one\n")
        listing = service_dir / "listing.json"

        name, first = _service_digest(listing)
        assert name == "acme/a"
        assert _service_digest(listing)[1] == first, "stable between calls"

        (service_dir / "service.json").write_text(json.dumps({"service_id": "id-1"}))
        assert _service_digest(listing)[1] == first, "the sidecar is identity, not content"

        # Rendering a param file stamps ``time_created`` with the current time when the template has none, so
        # it differs on every render: it must not count as a change.
        offering = json.loads((service_dir / "offering.json").read_text())
        offering["time_created"] = "2026-11-21T15:36:07Z"
        (service_dir / "offering.json").write_text(json.dumps(offering))
        listing_doc = json.loads(listing.read_text())
        listing_doc["time_created"] = "2026-11-21T15:36:10Z"
        listing.write_text(json.dumps(listing_doc))
        assert _service_digest(listing)[1] == first, "time_created is not content"
        offering["time_created"] = "2030-01-01T00:00:00Z"
        (service_dir / "offering.json").write_text(json.dumps(offering))
        assert _service_digest(listing)[1] == first

        (service_dir / "guide.md").write_text("# two\n")
        second = _service_digest(listing)[1]
        assert second != first, "a referenced file changed"

        _write_service(
            tmp_path / "acme",
            "a",
            price="2.00",
            extra_listing={
                "documents": {
                    "Guide": {
                        "category": "getting_started",
                        "mime_type": "markdown",
                        "file_path": "guide.md",
                        "is_public": True,
                    }
                }
            },
        )
        assert _service_digest(listing)[1] != second, "a field changed"


# ---------------------------------------------------------------------------
# upload_directory with a state file
# ---------------------------------------------------------------------------


class TestUploadWithState:
    def test_a_first_run_sends_everything_and_records_it(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "state" / "up.json"
        result = _run(client, catalog, state_file)

        assert sorted(client.sent) == ["acme/a", "acme/b", "acme/c"]
        assert result.services.success == 3 and result.services.skipped == 0
        document = json.loads(state_file.read_text())
        record = document["services"]["acme/a"]
        assert record["kind"] == KIND_SERVICE and len(record["payload_sha256"]) == 64
        assert record["ingest"]["status"] == "completed" and record["ingest"]["outcome"] == "created"
        assert record["service_id"] == "id-acme/a"
        assert document["summary"] == {"total": 3, "sent": 3, "skipped": 0, "failed": 0}

    def test_an_unchanged_catalog_is_skipped_and_its_records_untouched(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        _run(client, catalog, state_file)
        records = json.loads(state_file.read_text())["services"]
        client.uploads.clear()

        result = _run(client, catalog, state_file)

        assert client.uploads == []
        assert result.services.skipped == 3 and result.services.success == 0
        assert json.loads(state_file.read_text())["services"] == records
        assert json.loads(state_file.read_text())["summary"]["skipped"] == 3

    def test_only_the_changed_service_is_sent(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        _run(client, catalog, state_file)
        before = json.loads(state_file.read_text())["services"]
        client.uploads.clear()

        _write_service(catalog / "acme", "b", price="9.99")
        result = _run(client, catalog, state_file)

        assert client.sent == ["acme/b"]
        assert result.services.success == 1 and result.services.skipped == 2
        after = json.loads(state_file.read_text())["services"]
        assert after["acme/b"]["payload_sha256"] != before["acme/b"]["payload_sha256"]
        assert after["acme/a"] == before["acme/a"] and after["acme/c"] == before["acme/c"]

    def test_a_failed_ingest_is_retried_next_run(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        client.failing = {"acme/b"}
        result = _run(client, catalog, state_file)
        assert result.services.failed == 1
        record = json.loads(state_file.read_text())["services"]["acme/b"]
        assert record["ingest"]["status"] == "failed" and "refused by ingest" in record["ingest"]["error"]

        client.uploads.clear()
        client.failing = set()
        result = _run(client, catalog, state_file)

        assert client.sent == ["acme/b"], "the failed one is sent again; the others are not"
        assert result.services.skipped == 2
        assert json.loads(state_file.read_text())["services"]["acme/b"]["ingest"]["status"] == "completed"

    def test_a_service_missing_from_the_target_is_sent_again(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        _run(client, catalog, state_file)
        client.uploads.clear()
        client.remote_names.discard("acme/c")  # the target was reset

        _run(client, catalog, state_file)

        assert client.sent == ["acme/c"]

    def test_no_verify_remote_trusts_the_file(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        _run(client, catalog, state_file)
        client.uploads.clear()
        client.remote_names.clear()

        result = _run(client, catalog, state_file, verify_remote=False)

        assert client.uploads == [] and result.services.skipped == 3

    def test_when_the_target_cannot_be_listed_nothing_is_skipped(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        _run(client, catalog, state_file)
        client.uploads.clear()
        client.list_fails = True

        result = _run(client, catalog, state_file)

        assert sorted(client.sent) == ["acme/a", "acme/b", "acme/c"]
        assert any("Could not list" in note for note in result.notes)

    def test_force_sends_everything_and_rewrites_the_file(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        _run(client, catalog, state_file)
        client.uploads.clear()

        result = _run(client, catalog, state_file, force=True)

        assert sorted(client.sent) == ["acme/a", "acme/b", "acme/c"] and result.services.skipped == 0
        assert json.loads(state_file.read_text())["services"]["acme/a"]["ingest"]["status"] == "completed"

    def test_a_draft_left_without_submit_is_submitted_by_a_later_run(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        _run(client, catalog, state_file)
        client.uploads.clear()

        _run(client, catalog, state_file, auto_submit=True)
        assert sorted(client.uploads) == [("acme/a", True), ("acme/b", True), ("acme/c", True)]

        client.uploads.clear()
        result = _run(client, catalog, state_file, auto_submit=True)
        assert client.uploads == [] and result.services.skipped == 3, "submitted once, then unchanged"

    def test_a_sidecar_naming_another_service_is_sent_again(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        _run(client, catalog, state_file)
        client.uploads.clear()
        (catalog / "acme" / "a" / "service.json").write_text(json.dumps({"service_id": "id-somewhere-else"}))

        _run(client, catalog, state_file)

        assert client.sent == ["acme/a"]

    def test_a_selector_keeps_the_other_records_and_a_full_run_drops_gone_services(
        self, catalog: Path, tmp_path: Path
    ) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        _run(client, catalog, state_file)

        # A partial upload leaves the records of everything else alone, even a service no longer on disk.
        import shutil

        shutil.rmtree(catalog / "acme" / "c")
        client.uploads.clear()
        _write_service(catalog / "acme", "a", price="3.00")
        _run(client, catalog, state_file, name="acme/a")
        assert client.sent == ["acme/a"]
        assert set(json.loads(state_file.read_text())["services"]) == {"acme/a", "acme/b", "acme/c"}

        # A full run forgets the service that left the catalog.
        _run(client, catalog, state_file)
        assert set(json.loads(state_file.read_text())["services"]) == {"acme/a", "acme/b"}

    def test_a_state_file_for_another_target_is_ignored(self, catalog: Path, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        _run(client, catalog, state_file)
        client.uploads.clear()
        client._base_url = "https://seller.production.test/v1"

        result = _run(client, catalog, state_file)

        assert sorted(client.sent) == ["acme/a", "acme/b", "acme/c"]
        assert any("not" in note and "seller.test" in note for note in result.notes)
        assert json.loads(state_file.read_text())["target"] == "https://seller.production.test/v1"

    def test_without_a_state_file_nothing_changes(self, catalog: Path) -> None:
        client = _FakeClient()
        result = upload_directory(client, catalog, task_poll_interval=0.001, task_wait_timeout=5.0)  # type: ignore[arg-type]
        assert sorted(client.sent) == ["acme/a", "acme/b", "acme/c"] and result.services.skipped == 0


# ---------------------------------------------------------------------------
# The command
# ---------------------------------------------------------------------------


class TestCommand:
    def _invoke(self, monkeypatch: pytest.MonkeyPatch, args: list[str], invocation: Path) -> dict[str, Any]:
        import typer
        from typer.testing import CliRunner

        from unitysvc_sellers import _cli_upload, params_render
        from unitysvc_sellers.upload import UploadCounts, UploadResult

        captured: dict[str, Any] = {}

        class _Client:
            def __init__(self, **_: Any) -> None:
                pass

            def __enter__(self) -> _Client:
                return self

            def __exit__(self, *_: Any) -> None:
                return None

            def upload(self, data_dir: Path, **kwargs: Any) -> UploadResult:
                captured.update(kwargs)
                return UploadResult(services=UploadCounts(total=2, success=1, skipped=1), notes=["a note"])

        monkeypatch.setattr(_cli_upload, "Client", _Client)
        monkeypatch.setattr(params_render, "_invocation_cwd", invocation)
        app = typer.Typer()
        app.command("upload")(_cli_upload.upload)
        result = CliRunner().invoke(app, ["--api-key", "svcpass_x", *args])
        captured["output"] = result.output
        captured["exit_code"] = result.exit_code
        return captured

    def test_a_relative_state_path_is_the_users_not_the_render_copys(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        # ``specs`` runs inside a copy of the repo that is deleted afterwards; the file must outlive it.
        captured = self._invoke(monkeypatch, ["--state", "up.json"], invocation=tmp_path)
        assert captured["state"] == tmp_path / "up.json"
        assert captured["exit_code"] == 0

    def test_an_absolute_state_path_is_used_as_given(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        captured = self._invoke(monkeypatch, ["--state", str(tmp_path / "abs.json")], invocation=tmp_path / "elsewhere")
        assert captured["state"] == tmp_path / "abs.json"

    def test_flags_reach_the_upload_and_the_summary_says_what_was_skipped(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        captured = self._invoke(
            monkeypatch, ["--state", "up.json", "--force", "--no-verify-remote", "--submit"], invocation=tmp_path
        )
        assert captured["force"] is True and captured["verify_remote"] is False and captured["auto_submit"] is True
        assert "a note" in captured["output"]
        assert "skipped 1 unchanged since the last upload" in captured["output"]

    def test_without_state_nothing_is_passed(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        captured = self._invoke(monkeypatch, [], invocation=tmp_path)
        assert captured["state"] is None and captured["force"] is False and captured["verify_remote"] is True


class TestSystemTemplateParamFiles:
    """A param file naming a system template is sent as a template instantiation; its fingerprint is the
    template and its parameters."""

    def _param(self, root: Path, **parameters: str) -> Path:
        specs = root / "specs" / "crofai"
        specs.mkdir(parents=True, exist_ok=True)
        path = specs / "deepseek-v3.2.json"
        path.write_text(json.dumps({"template": "llm-fast", "parameters": {"model": "deepseek-v3.2", **parameters}}))
        return path

    def test_unchanged_parameters_are_skipped_and_changed_ones_sent(self, tmp_path: Path) -> None:
        client, state_file = _FakeClient(), tmp_path / "up.json"
        self._param(tmp_path, base_url="https://one.example/v1")
        _run(client, tmp_path, state_file)
        assert client.sent == ["crofai/deepseek-v3.2"]
        record = json.loads(state_file.read_text())["services"]["crofai/deepseek-v3.2"]
        assert record["kind"] == "system" and record["ingest"]["status"] == "completed"

        client.uploads.clear()
        result = _run(client, tmp_path, state_file)
        assert client.uploads == [] and result.services.skipped == 1

        self._param(tmp_path, base_url="https://two.example/v1")
        _run(client, tmp_path, state_file)
        assert client.sent == ["crofai/deepseek-v3.2"]
