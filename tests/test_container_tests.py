"""Required container connectivity documents reuse the local test workflow."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from unitysvc_sellers import example
from unitysvc_sellers.cli import app
from unitysvc_sellers.upload import _build_service_payload


@pytest.fixture
def service(tmp_path):
    folder = tmp_path / "specs" / "example" / "echo"
    folder.mkdir(parents=True)
    channels = {}
    for name, cpu in (("base", "250m"), ("medium", "1")):
        channels[name] = {
            "access_method": "container",
            "type": "enrollable",
            "customer_access_requests": [
                {
                    "object": "resource:container",
                    "permissions": ["create"],
                    "required": True,
                    "justification": "Run a disposable instance for this enrollment",
                }
            ],
            "spec": "Application",
            "resources": {"cpu": cpu, "memory": "256Mi", "ephemeral_disk": "1Gi"},
            "entries": [{"name": "web", "service": "web", "port": 5678, "auth": "enrollment_key", "path": "/"}],
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
        (
            "provider.json",
            {
                "name": "example",
                "contact_email": "owner@example.com",
                "homepage": "https://example.com",
                "time_created": "2026-11-14T00:00:00Z",
            },
        ),
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


def test_complete_container_service_uses_the_existing_folder_validator(service):
    result = CliRunner().invoke(app, ["specs", "validate", str(service.parents[2])])
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize("with_client", [False, True])
def test_compose_and_connectivity_use_normal_document_uploads(service, monkeypatch, with_client):
    from unitysvc_sellers import upload

    uploaded = {}

    def store(_client, path):
        uploaded[path.name] = path.read_bytes()
        return f"documents/{path.name}"

    monkeypatch.setattr(upload, "_upload_file_deduped", store)
    client = SimpleNamespace(_client=object()) if with_client else None
    provider, offering, listing, identity = _build_service_payload(service / "listing.json", client=client)
    assert provider["name"] == "example" and offering["name"] == "echo" and listing["name"] == "example/echo"
    assert identity is None
    compose = offering["documents"]["Application"]
    assert compose["category"] == "container_spec" and compose["file_path"] == "compose.json"
    for channel in ("base", "medium"):
        assert offering["upstream_access_config"][channel]["spec"] == "Application"
        assert "ephemeral_disk" in offering["upstream_access_config"][channel]["resources"]
    test = listing["documents"]["Local startup"]
    assert test["category"] == "connectivity_test"
    if with_client:
        assert uploaded["compose.json"] == (service / "compose.json").read_bytes()
        assert uploaded["startup.py"] == (service / "startup.py").read_bytes()
        assert compose["external_url"] == "${UNITYSVC_S3_BASE_URL}/documents/compose.json"
    else:
        assert compose["file_content"] == (service / "compose.json").read_text()
        assert test["file_content"] == (service / "startup.py").read_text()
