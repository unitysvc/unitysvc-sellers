"""``specs upload --since REF``: send only what changed since the branch left ``REF``.

A real git repository is built for each test (a base commit, a branch, and a base that moves on), the
fingerprints of the merge base are taken from it, and ``upload_directory`` runs against the fake client of
the state tests.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from unitysvc_sellers.since import SinceError, fingerprints_since
from unitysvc_sellers.state import KIND_SERVICE
from unitysvc_sellers.upload import catalog_fingerprints, upload_directory

from .test_upload_state import _FakeClient, _write_service


def _clear_caches() -> None:
    # A real run is one process; here several scans share one, and core caches its scans of the catalog.
    import unitysvc_core.utils as core_utils

    for cached in vars(core_utils).values():
        if hasattr(cached, "cache_clear"):
            cached.cache_clear()


def _git(repo: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
    }
    done = subprocess.run(["git", *args], cwd=repo, env=env, capture_output=True, text=True, check=True)
    return done.stdout.strip()


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """``main`` with services a, b and c under ``services/``; the working tree is on ``main``."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    for svc in ("a", "b", "c"):
        _write_service(root / "services" / "acme", svc)
    _commit(root, "three services")
    return root


def _upload(repo: Path, ref: str, **kwargs: Any) -> tuple[_FakeClient, Any]:
    catalog = repo / "services"
    _clear_caches()
    baseline, _ = fingerprints_since(ref, catalog)
    _clear_caches()
    client = _FakeClient()
    result = upload_directory(
        client,  # type: ignore[arg-type]
        catalog,
        baseline=baseline,
        baseline_label=ref,
        task_poll_interval=0.001,
        task_wait_timeout=5.0,
        **kwargs,
    )
    return client, result


class TestFingerprints:
    def test_a_catalog_is_fingerprinted_by_service_name(self, repo: Path) -> None:
        _clear_caches()
        prints = catalog_fingerprints(repo / "services")
        assert sorted(prints) == ["acme/a", "acme/b", "acme/c"]
        assert {kind for kind, _ in prints.values()} == {KIND_SERVICE}

    def test_the_baseline_is_the_merge_base_not_the_tip_of_the_ref(self, repo: Path) -> None:
        base = _git(repo, "rev-parse", "HEAD")
        _git(repo, "checkout", "-q", "-b", "feature")
        _write_service(repo / "services" / "acme", "d")
        _commit(repo, "add d")
        _git(repo, "checkout", "-q", "main")
        _write_service(repo / "services" / "acme", "b", price="9.00")
        _commit(repo, "main changes b")
        _git(repo, "checkout", "-q", "feature")

        _clear_caches()
        at_base = catalog_fingerprints(repo / "services")  # the branch still has the old b
        _clear_caches()
        baseline, commit = fingerprints_since("main", repo / "services")

        assert commit == base
        assert baseline["acme/b"] == at_base["acme/b"] and "acme/d" not in baseline

    def test_the_working_directory_is_put_back(self, repo: Path) -> None:
        before = Path.cwd()
        fingerprints_since("main", repo / "services")
        assert Path.cwd() == before

    def test_a_catalog_folder_that_did_not_exist_then_has_no_fingerprints(self, repo: Path) -> None:
        _git(repo, "checkout", "-q", "-b", "feature")
        _write_service(repo / "more" / "acme", "x")
        _commit(repo, "a second catalog")
        baseline, _ = fingerprints_since("main", repo / "more")
        assert baseline == {}

    def test_an_unknown_ref_is_an_error(self, repo: Path) -> None:
        with pytest.raises(SinceError, match="is not a commit"):
            fingerprints_since("origin/nope", repo / "services")

    def test_outside_a_repository_is_an_error(self, tmp_path: Path) -> None:
        with pytest.raises(SinceError, match="needs a git repository"):
            fingerprints_since("main", tmp_path)

    def test_unrelated_histories_are_an_error(self, repo: Path) -> None:
        _git(repo, "checkout", "-q", "--orphan", "island")
        _commit(repo, "no parent")
        with pytest.raises(SinceError, match="no common commit"):
            fingerprints_since("main", repo / "services")


class TestUploadSince:
    def test_only_the_service_the_branch_added_is_sent(self, repo: Path) -> None:
        _git(repo, "checkout", "-q", "-b", "feature")
        _write_service(repo / "services" / "acme", "d")
        _commit(repo, "add d")

        client, result = _upload(repo, "main")

        assert client.sent == ["acme/d"]
        assert result.services.success == 1 and result.services.skipped == 3

    def test_a_branch_behind_its_base_does_not_send_what_the_base_changed(self, repo: Path) -> None:
        # The fault this replaces: the pull request's branch has the OLD b, and must not send it.
        _git(repo, "checkout", "-q", "-b", "feature")
        _write_service(repo / "services" / "acme", "d")
        _commit(repo, "add d")
        _git(repo, "checkout", "-q", "main")
        _write_service(repo / "services" / "acme", "b", price="9.00")
        _commit(repo, "main changes b")
        _git(repo, "checkout", "-q", "feature")

        client, _ = _upload(repo, "main")

        assert client.sent == ["acme/d"]

    def test_a_changed_service_is_sent_and_an_uncommitted_change_counts(self, repo: Path) -> None:
        _git(repo, "checkout", "-q", "-b", "feature")
        _write_service(repo / "services" / "acme", "a", price="2.00")
        _commit(repo, "change a")
        _write_service(repo / "services" / "acme", "c", price="3.00")  # not committed

        client, _ = _upload(repo, "main")

        assert sorted(client.sent) == ["acme/a", "acme/c"]

    def test_a_changed_file_a_service_refers_to_sends_that_service_only(self, repo: Path) -> None:
        doc = repo / "services" / "acme" / "a" / "usage.md"
        doc.write_text("before\n")
        _write_service(
            repo / "services" / "acme",
            "a",
            extra_listing={
                "documents": {
                    "Usage": {"category": "getting_started", "file_path": "usage.md", "mime_type": "markdown"}
                }
            },
        )
        _commit(repo, "a has a document")
        _git(repo, "checkout", "-q", "-b", "feature")
        doc.write_text("after\n")
        _commit(repo, "reword the document")

        _, result = _upload(repo, "main")

        # The fake client cannot store a file, so the attempt on a ends in an error; b and c are not attempted.
        assert result.services.skipped == 2
        assert [Path(error["file"]).parent.name for error in result.services.errors] == ["a"]

    def test_nothing_changed_sends_nothing(self, repo: Path) -> None:
        _git(repo, "checkout", "-q", "-b", "feature")
        (repo / "README.md").write_text("notes\n")
        _commit(repo, "a file that is no service")

        client, result = _upload(repo, "main")

        assert client.sent == [] and result.services.skipped == 3 and result.total_failed == 0

    def test_a_sidecar_alone_is_not_a_change(self, repo: Path) -> None:
        # The check commits the service ids it was given; that commit must not send the service again.
        _git(repo, "checkout", "-q", "-b", "feature")
        (repo / "services" / "acme" / "a" / "service.json").write_text('{"service_id": "svc-a"}')
        _commit(repo, "record the id")

        client, _ = _upload(repo, "main")

        assert client.sent == []

    def test_only_what_was_sent_is_waited_for(self, repo: Path) -> None:
        _git(repo, "checkout", "-q", "-b", "feature")
        _write_service(repo / "services" / "acme", "d")
        _commit(repo, "add d")

        client, result = _upload(repo, "main", auto_submit=True, wait_for_test=5.0)

        assert client.waited_tests == ["acme/d"] and client.retested == []
        assert [t.name for t in result.tests] == ["acme/d"]

    def test_a_baseline_and_a_state_file_are_refused_together(self, repo: Path, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="cannot be combined"):
            upload_directory(_FakeClient(), repo / "services", baseline={}, state_path=tmp_path / "s.json")  # type: ignore[arg-type]


class TestCli:
    def _invoke(self, monkeypatch: pytest.MonkeyPatch, repo: Path, args: list[str]) -> dict[str, Any]:
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
                return UploadResult(services=UploadCounts(total=4, success=1, skipped=3))

        monkeypatch.setattr(_cli_upload, "Client", _Client)
        monkeypatch.setattr(params_render, "_invocation_cwd", repo / "services")
        app = typer.Typer()
        app.command("upload")(_cli_upload.upload)
        invoked = CliRunner().invoke(app, ["--api-key", "svcpass_x", *args])
        captured["output"] = invoked.output
        captured["exit_code"] = invoked.exit_code
        return captured

    def test_since_passes_the_fingerprints_of_the_merge_base(self, monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
        base = _git(repo, "rev-parse", "HEAD")
        _git(repo, "checkout", "-q", "-b", "feature")
        _write_service(repo / "services" / "acme", "d")
        _commit(repo, "add d")
        _clear_caches()

        captured = self._invoke(monkeypatch, repo, ["--since", "main", "--submit"])

        assert captured["exit_code"] == 0, captured["output"]
        assert sorted(captured["baseline"]) == ["acme/a", "acme/b", "acme/c"]
        assert captured["baseline_label"] == f"main ({base[:9]})"
        assert "skipped 3 unchanged since main" in captured["output"]

    def test_since_and_state_are_refused_together(self, monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
        captured = self._invoke(monkeypatch, repo, ["--since", "main", "--state", "up.json"])
        assert captured["exit_code"] == 1 and "cannot be combined with --state" in captured["output"]

    def test_an_unknown_ref_fails_before_anything_is_sent(self, monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
        captured = self._invoke(monkeypatch, repo, ["--since", "origin/nope"])
        assert captured["exit_code"] == 1 and "baseline" not in captured
        assert "is not a commit" in captured["output"]

    def test_without_since_no_baseline_is_passed(self, monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
        captured = self._invoke(monkeypatch, repo, [])
        assert captured["baseline"] is None and captured["exit_code"] == 0
