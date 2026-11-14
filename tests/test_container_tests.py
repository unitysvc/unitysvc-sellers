"""Required container connectivity documents reuse the local test workflow."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from unitysvc_sellers import example
from unitysvc_sellers.cli import app


@pytest.fixture
def service(tmp_path):
    folder = tmp_path / "specs" / "example" / "echo"
    folder.mkdir(parents=True)
    channels = {}
    for name, cpu in (("base", "250m"), ("medium", "1")):
        channels[name] = {
            "access_method": "container",
            "type": "enrollable",
            "customer_access_requests": [{"object": "resource:container", "permissions": ["create"], "required": True}],
            "spec": "Application",
            "resources": {"web": {"limits": {"cpu": cpu, "memory": "256Mi", "ephemeral-storage": "1Gi"}}},
            "entries": [{"name": "web", "service": "web", "port": 5678}],
        }
    channels["http"] = {"base_url": "https://example.com"}
    offering = {
        "name": "echo",
        "summary": "Container example",
        "description": "Container example",
        "time_created": "2026-11-14T00:00:00Z",
        "upstream_access_config": channels,
        "documents": {"Application": {"category": "container_spec", "mime_type": "json", "file_path": "compose.json"}},
    }
    listing = {
        "name": "example/echo",
        "time_created": "2026-11-14T00:00:00Z",
        "documents": {
            "Local startup": {
                "category": "connectivity_test",
                "mime_type": "python",
                "file_path": "startup.py",
                "meta": {"runtime": "docker", "container_timeout_seconds": 60},
            }
        },
    }
    source = {"services": {"web": {"image": "example/echo@sha256:" + "a" * 64, "expose": [5678]}}}
    for name, payload in (
        ("offering.json", offering),
        ("listing.json", listing),
        ("provider.json", {"name": "example"}),
        ("compose.json", source),
    ):
        (folder / name).write_text(json.dumps(payload))
    (folder / "startup.py").write_text("print('local startup test')\n")
    return folder


def test_runs_every_container_tier_without_credentials_or_cached_skips(service, monkeypatch):
    monkeypatch.chdir(service.parents[2])
    calls = []

    def execute(**kwargs):
        manifest = json.loads(kwargs["env_vars"]["USVC_CONTAINER_MANIFEST_JSON"])
        calls.append(manifest["services"][0]["resources"]["limits"]["cpu"])
        assert kwargs["timeout"] == 105  # 60s test plus cleanup allowance
        assert kwargs["env_vars"]["USVC_CONTAINER_TIMEOUT_SECONDS"] == "60"
        assert "UNITYSVC_API_KEY" not in kwargs["env_vars"]
        return {"status": "success", "exit_code": 0, "stdout": "ready", "stderr": None, "error": None}

    monkeypatch.setattr(example, "execute_script_content", execute)
    runner = CliRunner()
    for _ in range(2):
        result = runner.invoke(
            app, ["specs", "run-tests", "example/echo", "--category", "connectivity_test", "--skip-links"]
        )
        assert result.exit_code == 0, result.output
    assert calls == ["250m", "1", "250m", "1"]
    assert json.loads((service / "service.json").read_text())["upstream_test_status"] == "pass"


def test_missing_connectivity_document_is_rejected_by_validation(service, monkeypatch):
    monkeypatch.chdir(service.parents[2])
    listing = json.loads((service / "listing.json").read_text())
    listing.pop("documents")
    (service / "listing.json").write_text(json.dumps(listing))
    import unitysvc_core
    from unitysvc_core.validator import DataValidator

    offering = json.loads((service / "offering.json").read_text())
    schemas = Path(unitysvc_core.__file__).parent / "schema"
    errors = DataValidator(service, schemas).validate_connectivity_test_exists(listing, "listing_v1", offering=offering)
    assert errors and "connectivity_test" in errors[0]


def test_connectivity_failure_is_recorded_normally(service, monkeypatch):
    monkeypatch.chdir(service.parents[2])
    monkeypatch.setattr(
        example,
        "execute_script_content",
        lambda **_: {
            "status": "script_failed",
            "exit_code": 1,
            "stdout": None,
            "stderr": "health failed",
            "error": "health failed",
        },
    )
    result = CliRunner().invoke(app, ["specs", "run-tests", "--category", "connectivity_test", "--skip-links"])
    assert result.exit_code == 1
    assert json.loads((service / "service.json").read_text())["upstream_test_status"] == "fail"


def test_container_documents_are_only_discovered_for_container_channels(service):
    examples = example.discover_code_examples(service)
    assert {item[0]["upstream_channel_name"] for item in examples} == {"base", "medium"}
