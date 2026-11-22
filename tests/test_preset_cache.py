"""Missing-preset refresh through the real core walker and CLI, without network."""

from __future__ import annotations

import importlib.metadata
import json
import logging
import os
import shutil
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock

import pytest
import unitysvc_core
import unitysvc_data
from filelock import FileLock
from typer.testing import CliRunner
from unitysvc_core.utils import DEFAULT_PRESET_FNS, load_data_file
from unitysvc_core.validator import DataValidator

from unitysvc_sellers import preset_cache
from unitysvc_sellers.cli import app
from unitysvc_sellers.preset_cache import CachedRelease, PresetResolver, refreshing_presets
from unitysvc_sellers.upload import _resolve_file_references


@pytest.fixture
def resolver(tmp_path):
    return PresetResolver(tmp_path / "cache", refresh_timeout=10, replay_timeout=30)


@pytest.fixture
def future_package(tmp_path):
    target = tmp_path / "future-data"
    distribution = importlib.metadata.distribution("unitysvc-data")
    for file in distribution.files or []:
        source = Path(str(distribution.locate_file(file)))
        if file.parts[0] != "unitysvc_data" and not file.parts[0].endswith(".dist-info"):
            continue
        if source.is_file():
            destination = target / file
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    manifest_path = target / "unitysvc_data" / "_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    record = dict(manifest["presets"]["container_connectivity_v1"], preset_name="future_container")
    manifest["presets"]["future_container_v1"] = record
    manifest["aliases"]["future_container"] = "future_container_v1"
    manifest_path.write_text(json.dumps(manifest))
    metadata = next(target.glob("*.dist-info/METADATA"))
    metadata.write_text(metadata.read_text().replace(f"Version: {unitysvc_data.__version__}\n", "Version: 99.0.0\n"))
    return target


@pytest.fixture
def download(resolver, future_package, monkeypatch):
    run = subprocess.run
    calls = []

    def install_or_helper(command, **kwargs):
        if "--target" not in command:
            assert "UNITYSVC_SELLER_API_KEY" not in kwargs["env"]
            return run(command, **kwargs)
        calls.append(command)
        assert command[command.index("--index-url") + 1] == "https://pypi.org/simple"
        assert "--only-binary" in command and "--no-deps" in command
        assert all(
            not name.startswith(("PIP_", "UV_", "PYTHON")) or name in preset_cache._INSTALL_ENV_KEYS
            for name in kwargs["env"]
        )
        assert 0 < kwargs["timeout"] <= resolver.refresh_timeout
        shutil.copytree(future_package, command[command.index("--target") + 1])
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "must-not-reach-helper")
    monkeypatch.setenv("UV_EXTRA_INDEX_URL", "https://untrusted.example/simple")
    monkeypatch.setattr(preset_cache.subprocess, "run", install_or_helper)
    return calls


def test_known_presets_work_offline_without_a_cache(resolver, monkeypatch):
    install = Mock(side_effect=AssertionError("unexpected refresh"))
    monkeypatch.setattr(resolver, "_install", install)
    result = resolver.call("doc_preset", "container_connectivity")
    assert Path(result["file_path"]).is_file()
    assert result["meta"]["preset"]["data_version"] == unitysvc_data.__version__
    assert not resolver.cache_dir.exists()
    install.assert_not_called()


@pytest.mark.parametrize(
    "source",
    [
        {"name": "container_connectivity", "probe_path": None},
        {"name": "container_connectivity", "unknown_parameter": "x"},
        {"not_a_recipe": "x"},
    ],
)
def test_invalid_parameters_do_not_refresh(resolver, monkeypatch, source):
    install = Mock(side_effect=AssertionError("invalid input triggered download"))
    monkeypatch.setattr(resolver, "_install", install)
    with pytest.raises(ValueError):
        resolver.call("doc_preset", source)
    install.assert_not_called()


def test_unknown_preset_refreshes_once_retries_once_and_obeys_cooldown(resolver, monkeypatch):
    install = Mock(return_value=None)
    bundled = Mock(wraps=resolver._bundled)
    monkeypatch.setattr(resolver, "_install", install)
    monkeypatch.setattr(resolver, "_bundled", bundled)
    with pytest.raises(ValueError, match="after refreshing"):
        resolver.call("doc_preset", "future_container_v1")
    assert bundled.call_count == 2
    with pytest.raises(ValueError, match="cooldown"):
        resolver.call("doc_preset", "another_future_v1")
    install.assert_called_once()
    os.utime(resolver.cache_dir / ".last-refresh", (0, 0))
    with pytest.raises(ValueError):
        resolver.call("doc_preset", "another_future_v1")
    assert install.call_count == 2


def test_core_loader_validator_bundles_and_upload_keep_generated_files(resolver, download, tmp_path):
    listing = tmp_path / "listing.json"
    listing.write_text(
        json.dumps(
            {
                "documents": {
                    "Connectivity": {
                        "$doc_preset": {"name": "future_container", "probe_path": "/new"},
                    }
                }
            }
        )
    )
    original = listing.read_bytes()
    registry = dict(DEFAULT_PRESET_FNS)
    with refreshing_presets(resolver):
        data, _ = load_data_file(listing)
        record = data["documents"]["Connectivity"]
        generated = Path(record["file_path"])
        assert generated.is_relative_to(resolver.cache_dir / "assets")
        assert generated.is_file() and "/new" in generated.read_text()
        assert record["meta"]["preset"]["name"] == "future_container_v1"
        assert record["meta"]["preset"]["data_version"] == "99.0.0"
        assert not list(resolver.cache_dir.glob(".request-*"))
        validator = DataValidator(tmp_path, Path(unitysvc_core.__file__).parent / "schema")
        assert validator.load_data_file(listing) == (data, [])
        body = resolver.call("file_preset", {"name": "future_container", "probe_path": "/file"})
        assert "/file" in body
        bundle = resolver.call(
            "llm_example_collection",
            {
                "capabilities": ["chat"],
                "formats": [{"formats": ["openai"], "channels": ["base"], "interface": "canonical"}],
            },
        )
        assert len(bundle) > 1
        assert all(Path(doc["file_path"]).is_file() for doc in bundle.values())
        assert all(doc["meta"]["preset"]["data_version"] == "99.0.0" for doc in bundle.values())
        resolved = _resolve_file_references(data, tmp_path)
        assert resolved["documents"]["Connectivity"]["file_content"] == generated.read_text()
    assert dict(DEFAULT_PRESET_FNS) == registry
    assert listing.read_bytes() == original
    assert generated.is_file()  # helper and registry context are already closed
    assert len(download) == 1
    assert unitysvc_data.__version__ != "99.0.0"


def _service(root):
    folder = root / "specs" / "acme" / "demo"
    folder.mkdir(parents=True)
    (folder / "provider.json").write_text(json.dumps({"name": "acme"}))
    (folder / "offering.json").write_text(json.dumps({"name": "demo"}))
    (folder / "listing.json").write_text(
        json.dumps(
            {
                "name": "acme/demo",
                "documents": {"Connectivity": {"$doc_preset": "future_container"}},
            }
        )
    )
    return folder


def test_cli_show_and_expand_use_the_same_resolver(resolver, download, monkeypatch, tmp_path):
    monkeypatch.setattr(preset_cache, "resolver_from_environment", lambda: resolver)
    _service(tmp_path)
    registry = dict(DEFAULT_PRESET_FNS)
    runner = CliRunner()
    result = runner.invoke(app, ["specs", "show", "acme/demo", "-d", str(tmp_path), "--listing", "-f", "text"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["documents"]["Connectivity"]["meta"]["preset"]["data_version"] == "99.0.0"
    result = runner.invoke(app, ["specs", "expand", "acme/demo", "-d", str(tmp_path)])
    assert result.exit_code == 0, result.output
    record = json.loads((tmp_path / "expanded/acme/demo/listing.json").read_text())["documents"]["Connectivity"]
    assert not Path(record["file_path"]).is_absolute()
    assert (tmp_path / "expanded/acme/demo" / record["file_path"]).is_file()
    assert len(download) == 1
    assert dict(DEFAULT_PRESET_FNS) == registry


def test_cached_results_are_copied_and_shared_within_one_command(resolver, monkeypatch):
    current = CachedRelease(resolver.cache_dir / "release", "99.0.0")
    monkeypatch.setattr(resolver, "_active", lambda: current)
    helper = Mock(return_value={"meta": {"source": "approved"}})
    monkeypatch.setattr(resolver, "_helper", helper)
    first = resolver.call("doc_preset", "future_container")
    first["meta"]["source"] = "changed"
    assert resolver.call("doc_preset", "future_container")["meta"]["source"] == "approved"
    helper.assert_called_once()


def test_failed_install_keeps_previous_cache_and_known_presets(resolver, future_package, monkeypatch):
    resolver.cache_dir.mkdir()
    directory = resolver.cache_dir / ("release-" + "a" * 32)
    shutil.copytree(future_package, directory)
    pointer = resolver.cache_dir / "active.json"
    pointer.write_text(json.dumps({"directory": directory.name, "version": "99.0.0"}))
    before = pointer.read_bytes()
    install = Mock(side_effect=OSError("offline"))
    monkeypatch.setattr(resolver, "_install", install)
    with pytest.raises(ValueError, match="Could not refresh"):
        resolver.call("doc_preset", "not_published_v1")
    assert pointer.read_bytes() == before
    assert Path(resolver.call("doc_preset", "future_container")["file_path"]).is_file()
    install.assert_called_once()


@pytest.mark.parametrize(
    "pointer",
    [
        "broken json",
        "[]",
        '{"directory":"../outside","version":"99.0.0"}',
        '{"directory":"release-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","version":"99.0.0"}',
    ],
)
def test_corrupt_or_dangling_cache_falls_back_to_bundled(resolver, pointer):
    resolver.cache_dir.mkdir()
    (resolver.cache_dir / "active.json").write_text(pointer)
    assert Path(resolver.call("doc_preset", "container_connectivity")["file_path"]).is_file()


@pytest.mark.parametrize("stdout", ["[]", "{}", '{"status":"ok"}', "not json"])
def test_bad_helper_output_falls_back_without_install(resolver, monkeypatch, stdout):
    monkeypatch.setattr(resolver, "_active", lambda: CachedRelease(resolver.cache_dir, "99.0.0"))
    monkeypatch.setattr(preset_cache.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout))
    install = Mock(side_effect=AssertionError("known preset must remain offline"))
    monkeypatch.setattr(resolver, "_install", install)
    assert Path(resolver.call("doc_preset", "container_connectivity")["file_path"]).is_file()
    install.assert_not_called()


def test_concurrent_commands_share_one_refresh(resolver, monkeypatch):
    peer = PresetResolver(resolver.cache_dir, cooldown=60)
    entered, finish = threading.Event(), threading.Event()

    def install(*args, **kwargs):
        entered.set()
        assert finish.wait(5)

    mock = Mock(side_effect=install)
    monkeypatch.setattr(resolver, "_install", mock)
    monkeypatch.setattr(peer, "_install", mock)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(resolver._refresh, None)
        assert entered.wait(5)
        second = pool.submit(peer._refresh, None)
        finish.set()
        assert first.result(timeout=10) == (None, True)
        assert second.result(timeout=10) == (None, False)
    mock.assert_called_once()


def test_lock_wait_is_bounded(resolver):
    resolver.cache_dir.mkdir()
    resolver.refresh_timeout = 0.01
    with FileLock(str(resolver.cache_dir / ".refresh.lock")):
        with pytest.raises(ValueError, match="Could not refresh"):
            resolver.call("doc_preset", "future_container_v1")


def test_registry_restores_on_error_and_preserves_custom_functions(resolver):
    original = dict(DEFAULT_PRESET_FNS)

    def custom(value):
        return {"custom": value}

    DEFAULT_PRESET_FNS["custom"] = custom
    try:
        with pytest.raises(RuntimeError), refreshing_presets(resolver):
            assert DEFAULT_PRESET_FNS["custom"] is custom
            raise RuntimeError("command failed")
        assert DEFAULT_PRESET_FNS["custom"] is custom
    finally:
        DEFAULT_PRESET_FNS.clear()
        DEFAULT_PRESET_FNS.update(original)


def test_pip_fallback_is_isolated_and_never_changes_the_cli_environment(resolver, monkeypatch):
    resolver.cache_dir.mkdir()
    monkeypatch.setattr(preset_cache.shutil, "which", lambda name: None)
    seen = []

    def install(command, **kwargs):
        seen.append(command)
        assert command[1:3] == ["-m", "pip"]
        assert "--isolated" in command and "--target" in command
        assert kwargs["timeout"] <= 10
        Path(command[command.index("--target") + 1]).mkdir()
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(preset_cache.subprocess, "run", install)
    monkeypatch.setattr(resolver, "_helper", lambda *a: {"version": "99.0.0", "functions": list(resolver.bundled)})
    assert resolver._install(None, deadline=time.monotonic() + 10, repair=False).version == "99.0.0"
    assert len(seen) == 1


@pytest.mark.parametrize("use_uv", [True, False])
@pytest.mark.parametrize("certificate_variable", ["PIP_CERT", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"])
def test_install_forwards_network_settings_but_helper_does_not(resolver, monkeypatch, use_uv, certificate_variable):
    resolver.cache_dir.mkdir()
    proxy = "http://example-user:example-password@proxy.example:8080"
    for name in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.setenv(name, proxy)
    monkeypatch.setenv("NO_PROXY", "localhost")
    monkeypatch.setenv("no_proxy", "localhost")
    for name in ("PIP_CERT", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "SSL_CERT_FILE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(certificate_variable, "/custom/roots.pem")
    monkeypatch.setenv("SSL_CERT_DIR", "/custom/certs")
    monkeypatch.setenv("UV_NATIVE_TLS", "true")
    monkeypatch.setenv("UV_EXTRA_INDEX_URL", "https://untrusted.example/simple")
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "private-seller-key")
    monkeypatch.setattr(preset_cache.shutil, "which", lambda name: "/bin/uv" if use_uv else None)
    observed = []

    def run(command, **kwargs):
        observed.append(command)
        environment = kwargs["env"]
        if "--target" in command:
            assert environment["HTTPS_PROXY"] == environment["https_proxy"] == proxy
            assert environment["HTTP_PROXY"] == environment["http_proxy"] == proxy
            assert environment["ALL_PROXY"] == environment["all_proxy"] == proxy
            assert environment["NO_PROXY"] == environment["no_proxy"] == "localhost"
            assert environment[certificate_variable] == "/custom/roots.pem"
            assert environment["SSL_CERT_DIR"] == "/custom/certs"
            assert environment["UV_NATIVE_TLS"] == "true"
            assert "UV_EXTRA_INDEX_URL" not in environment
            assert "UNITYSVC_SELLER_API_KEY" not in environment
            if use_uv:
                assert environment["SSL_CERT_FILE"] == "/custom/roots.pem"
            else:
                assert "--isolated" in command
                assert command[command.index("--cert") + 1] == "/custom/roots.pem"
            Path(command[command.index("--target") + 1]).mkdir()
            return subprocess.CompletedProcess(command, 0)
        assert not set(preset_cache._INSTALL_ENV_KEYS).intersection(environment)
        assert "UNITYSVC_SELLER_API_KEY" not in environment
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps(
                {
                    "status": "ok",
                    "result": {"version": "99.0.0", "functions": list(resolver.bundled)},
                }
            ),
        )

    monkeypatch.setattr(preset_cache.subprocess, "run", run)
    assert resolver._install(None, deadline=time.monotonic() + 10, repair=False).version == "99.0.0"
    assert len(observed) == 2


@pytest.mark.parametrize("use_uv", [True, False])
def test_installer_diagnostics_are_visible_and_redact_proxy_credentials(resolver, monkeypatch, caplog, use_uv):
    monkeypatch.setattr(preset_cache.shutil, "which", lambda name: "/bin/uv" if use_uv else None)

    def fail(command, **kwargs):
        raise subprocess.CalledProcessError(
            1,
            command,
            stderr=(
                "Proxy connection to http://example-user:example-password@proxy.example:8080 failed\n"
                "ERROR: certificate verify failed\n"
            ),
        )

    monkeypatch.setattr(preset_cache.subprocess, "run", fail)
    with caplog.at_level(logging.DEBUG, logger="unitysvc_sellers.preset_cache"):
        message = "Could not refresh unitysvc-data: ERROR: certificate verify failed"
        with pytest.raises(ValueError, match=message) as error:
            resolver.call("doc_preset", "future_container_v1")
    assert "certificate verify failed" in caplog.text
    assert "http://***@proxy.example:8080" in caplog.text
    assert "example-user" not in caplog.text + str(error.value)
    assert "example-password" not in caplog.text + str(error.value)


def test_failed_install_probe_is_wrapped_and_does_not_loop(resolver, monkeypatch):
    install = Mock(side_effect=preset_cache.HelperFailure("Invalid unitysvc-data installation"))
    monkeypatch.setattr(resolver, "_install", install)
    with pytest.raises(ValueError, match="Could not refresh unitysvc-data: release validation failed"):
        resolver.call("doc_preset", "future_container_v1")
    with pytest.raises(ValueError, match="cooldown"):
        resolver.call("doc_preset", "future_container_v1")
    install.assert_called_once()


@pytest.mark.parametrize(
    "probe",
    [
        {},
        {"version": "broken", "functions": []},
        {"version": "99.0.0", "functions": None},
        {"version": "99.0.0", "functions": []},
    ],
)
def test_invalid_install_probe_keeps_cache_unactivated(resolver, monkeypatch, probe):
    def install(command, **kwargs):
        Path(command[command.index("--target") + 1]).mkdir()
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(preset_cache.subprocess, "run", install)
    monkeypatch.setattr(resolver, "_helper", lambda *a: probe)
    with pytest.raises(ValueError, match="Could not refresh unitysvc-data: release validation failed"):
        resolver.call("doc_preset", "future_container_v1")
    assert resolver._active() is None


def test_bundled_generation_and_later_reads_are_safe_for_concurrent_calls(resolver):
    # All writers enter the guard. The library writes once and reuses complete
    # entries, so reading a returned path outside the guard cannot see a writer.
    with ThreadPoolExecutor(max_workers=16) as pool:
        for iteration in range(10):
            barrier = threading.Barrier(16)
            probe = f"/concurrent-{time.monotonic_ns()}-{iteration}"

            def generate_and_read(barrier=barrier, probe=probe):
                barrier.wait(timeout=10)
                result = resolver.call("doc_preset", {"name": "container_connectivity", "probe_path": probe})
                return Path(result["file_path"]).read_text()

            results = [future.result(timeout=15) for future in [pool.submit(generate_and_read) for _ in range(16)]]
            assert all(results) and len(set(results)) == 1
            assert probe in results[0]
