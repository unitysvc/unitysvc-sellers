"""The offering-level ``instance_spec`` shortcut (unitysvc/unitysvc-core#107).

Covers expansion on upload (path and URL), validation of both forms, the local URL fetch rules, ``meta.sha256``,
``specs format`` leaving a remote file alone and ``run-tests`` using the
offering's single spec. No real network: https is mocked with respx.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx
from typer.testing import CliRunner

from unitysvc_sellers import container_testing as runner_module
from unitysvc_sellers.format_data import format_data_files
from unitysvc_sellers.instance_spec_source import (
    InstanceSpecFetchError,
    check_remote_instance_spec,
    fetch_instance_spec,
    find_instance_spec,
)
from unitysvc_sellers.specs_layout import app
from unitysvc_sellers.upload import _build_service_payload as prepare_service_data
from unitysvc_sellers.utils import convert_convenience_fields_to_documents

COMPOSE = """services:
  web:
    image: docker.io/example/web@sha256:{digest}
    ports: ["8080"]
""".format(digest="a" * 64)
SHA = hashlib.sha256(COMPOSE.encode()).hexdigest()
URL = "https://raw.githubusercontent.com/acme/stacks/" + "c" * 40 + "/compose.yaml"
TIME = "2026-01-01T00:00:00Z"

CHANNEL = {
    "access_method": "container",
    "resources": {"limits": {"cpu": "250m", "memory": "256Mi", "ephemeral-storage": "1Gi"}},
    "entries": [{"name": "web", "service": "web", "port": 8080, "auth": "key"}],
    "customer_access_requests": [
        {
            "object": "resource:container",
            "permissions": ["create"],
            "required": True,
            "justification": "Run a disposable application instance for this enrollment",
        }
    ],
}


def make_service(root: Path, offering_extra: dict[str, Any], channel: dict[str, Any] | None = None) -> Path:
    folder = root / "specs" / "acme" / "web"
    folder.mkdir(parents=True)
    (folder / "provider.json").write_text(
        json.dumps(
            {
                "name": "acme",
                "homepage": "https://acme.example.com",
                "contact_email": "a@acme.example.com",
                "time_created": TIME,
            }
        )
    )
    offering = {
        "name": "web",
        "service_type": "container",
        "summary": "A container",
        "description": "A disposable container per enrollment.",
        "upstream_access_config": {"base": channel or CHANNEL},
        "time_created": TIME,
        **offering_extra,
    }
    (folder / "offering.json").write_text(json.dumps(offering))
    (folder / "listing.json").write_text(
        json.dumps(
            {
                "name": "acme/web",
                "time_created": TIME,
                "list_price": {
                    "type": "channel",
                    "default": "base",
                    "description": "$1 / hour",
                    "channels": {"base": {"type": "one_hour", "price": "1", "description": "$1 / hour"}},
                },
                "service_options": {"default_visibility": "private", "enrollment": {"required": True}},
            }
        )
    )
    (folder / "compose.yaml").write_text(COMPOSE)
    return folder


def validate(root: Path) -> Any:
    return CliRunner().invoke(app, [str(root)], terminal_width=200)


# --- expansion on upload ---------------------------------------------------


def test_path_shortcut_expands_to_a_file_path_document(tmp_path: Path) -> None:
    data = {"name": "web", "instance_spec": "compose.yaml"}
    out = convert_convenience_fields_to_documents(data, tmp_path, instance_spec_field="instance_spec")
    assert "instance_spec" not in out
    assert out["documents"]["Instance spec"] == {
        "category": "instance_spec",
        "mime_type": "text",
        "meta": {"format": "compose"},
        "is_public": False,
        "file_path": "compose.yaml",
    }


def test_url_shortcut_expands_to_an_untouched_external_url(tmp_path: Path) -> None:
    out = convert_convenience_fields_to_documents({"instance_spec": URL}, tmp_path, instance_spec_field="instance_spec")
    document = out["documents"]["Instance spec"]
    assert document["external_url"] == URL
    assert "file_path" not in document and "file_content" not in document
    assert "source" not in document["meta"]


def test_shortcut_is_left_alone_unless_asked(tmp_path: Path) -> None:
    out = convert_convenience_fields_to_documents({"instance_spec": "compose.yaml"}, tmp_path)
    assert out["instance_spec"] == "compose.yaml"


def test_shortcut_beside_a_document_is_refused(tmp_path: Path) -> None:
    data = {"instance_spec": "a.yaml", "documents": {"X": {"category": "instance_spec", "file_path": "b.yaml"}}}
    with pytest.raises(ValueError, match="one instance spec"):
        convert_convenience_fields_to_documents(data, tmp_path, instance_spec_field="instance_spec")


def test_prepare_inlines_a_path_spec_and_never_downloads_a_url(tmp_path: Path) -> None:
    local = make_service(tmp_path / "local", {"instance_spec": "compose.yaml"})
    remote = make_service(tmp_path / "remote", {"instance_spec": URL})
    with respx.mock(assert_all_called=False) as mock:  # any request at all would be a download
        _, offering, _, _ = prepare_service_data(local / "listing.json", client=None)
        assert offering["documents"]["Instance spec"]["file_content"] == COMPOSE
        _, offering, _, _ = prepare_service_data(remote / "listing.json", client=None)
        assert mock.calls.call_count == 0
    document = offering["documents"]["Instance spec"]
    assert document["external_url"] == URL
    assert "file_content" not in document and "instance_spec" not in offering


# --- validation: both forms and the old one --------------------------------


def test_path_shortcut_validates(tmp_path: Path) -> None:
    make_service(tmp_path, {"instance_spec": "compose.yaml"})
    result = validate(tmp_path)
    assert result.exit_code == 0, result.output


def test_path_shortcut_errors_are_reported(tmp_path: Path) -> None:
    folder = make_service(tmp_path, {"instance_spec": "compose.yaml"})
    (folder / "compose.yaml").write_text(COMPOSE + "    privileged: true\n")
    result = validate(tmp_path)
    assert result.exit_code == 1
    assert "privileged" in result.output


@respx.mock
def test_url_shortcut_validates_against_the_downloaded_file(tmp_path: Path) -> None:
    make_service(tmp_path, {"instance_spec": URL})
    route = respx.get(URL).mock(return_value=httpx.Response(200, text=COMPOSE))
    result = validate(tmp_path)
    assert result.exit_code == 0, result.output
    assert route.call_count == 1
    assert not list((tmp_path / "specs" / "acme" / "web").glob("*.yaml.*"))  # nothing written to the tree


@respx.mock
def test_url_shortcut_reports_errors_in_the_downloaded_file(tmp_path: Path) -> None:
    make_service(tmp_path, {"instance_spec": URL})
    respx.get(URL).mock(return_value=httpx.Response(200, text=COMPOSE + "    privileged: true\n"))
    result = validate(tmp_path)
    assert result.exit_code == 1
    assert "privileged" in result.output


@respx.mock
def test_url_shortcut_warns_about_a_branch_ref(tmp_path: Path) -> None:
    branch = "https://github.com/acme/stacks/blob/main/compose.yaml"
    make_service(tmp_path, {"instance_spec": branch})
    respx.get("https://raw.githubusercontent.com/acme/stacks/main/compose.yaml").mock(
        return_value=httpx.Response(200, text=COMPOSE)
    )
    result = validate(tmp_path)
    assert result.exit_code == 0, result.output
    assert "branch" in result.output


# --- meta.sha256 ----------------------------------------------------------


@respx.mock
def test_sha256_mismatch_on_a_url_spec_is_an_error() -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, text=COMPOSE))
    offering = {
        "upstream_access_config": {"base": CHANNEL},
        "documents": {
            "Instance spec": {"category": "instance_spec", "external_url": URL, "meta": {"sha256": "0" * 64}}
        },
    }
    errors, _ = check_remote_instance_spec(offering)
    assert errors and "meta.sha256" in errors[0]


@respx.mock
def test_sha256_match_passes() -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, text=COMPOSE))
    offering = {
        "upstream_access_config": {"base": CHANNEL},
        "documents": {"Instance spec": {"category": "instance_spec", "external_url": URL, "meta": {"sha256": SHA}}},
    }
    assert check_remote_instance_spec(offering) == ([], [])


# --- download rules -------------------------------------------------------


def test_http_url_is_refused() -> None:
    with pytest.raises(InstanceSpecFetchError, match="https"):
        fetch_instance_spec("http://example.com/compose.yaml")


@respx.mock
def test_redirect_to_http_is_refused() -> None:
    respx.get("https://example.com/a").mock(
        return_value=httpx.Response(301, headers={"location": "http://example.com/b"})
    )
    with pytest.raises(InstanceSpecFetchError, match="https"):
        fetch_instance_spec("https://example.com/a")


@respx.mock
def test_redirects_are_limited_and_https_redirects_are_followed() -> None:
    respx.get("https://example.com/a").mock(return_value=httpx.Response(302, headers={"location": "/b"}))
    respx.get("https://example.com/b").mock(return_value=httpx.Response(200, text=COMPOSE))
    assert fetch_instance_spec("https://example.com/a")[0] == COMPOSE
    respx.get("https://example.com/loop").mock(return_value=httpx.Response(302, headers={"location": "/loop"}))
    with pytest.raises(InstanceSpecFetchError, match="redirected more than"):
        fetch_instance_spec("https://example.com/loop")


@respx.mock
def test_size_cap_applies_to_declared_and_streamed_bodies() -> None:
    respx.get("https://example.com/big").mock(return_value=httpx.Response(200, content=b"x" * 2000))
    with pytest.raises(InstanceSpecFetchError, match="larger than 1000 bytes"):
        fetch_instance_spec("https://example.com/big", max_bytes=1000)


@respx.mock
def test_timeout_and_http_errors_are_reported() -> None:
    respx.get("https://example.com/slow").mock(side_effect=httpx.ConnectTimeout("slow"))
    with pytest.raises(InstanceSpecFetchError, match="cannot download"):
        fetch_instance_spec("https://example.com/slow")
    respx.get("https://example.com/missing").mock(return_value=httpx.Response(404))
    with pytest.raises(InstanceSpecFetchError, match="HTTP 404"):
        fetch_instance_spec("https://example.com/missing")


@respx.mock
def test_github_blob_pages_are_rewritten_to_raw() -> None:
    sha = "d" * 40
    route = respx.get(f"https://raw.githubusercontent.com/o/r/{sha}/dir/compose.yaml").mock(
        return_value=httpx.Response(200, text=COMPOSE)
    )
    text, warnings = fetch_instance_spec(f"https://github.com/o/r/blob/{sha}/dir/compose.yaml")
    assert text == COMPOSE and route.called and warnings == []


# --- specs format leaves a remote file alone ------------------------------


def test_format_leaves_a_url_spec_alone(tmp_path: Path) -> None:
    folder = make_service(tmp_path, {"instance_spec": URL})
    before = {p.name: p.read_text() for p in folder.iterdir() if p.suffix != ".json"}
    with respx.mock(assert_all_called=False) as mock:
        assert format_data_files(tmp_path, check_only=False)
        assert mock.calls.call_count == 0
    assert json.loads((folder / "offering.json").read_text())["instance_spec"] == URL
    assert {p.name: p.read_text() for p in folder.iterdir() if p.suffix != ".json"} == before


# --- run-tests uses the one spec ------------------------------------------


@pytest.mark.parametrize("document_form", [False, True])
def test_run_tests_uses_the_offerings_single_spec(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, document_form: bool
) -> None:
    if document_form:
        document = {"category": "instance_spec", "mime_type": "text", "file_path": "compose.yaml"}
        make_service(tmp_path, {"documents": {"Application": document}})
    else:
        make_service(tmp_path, {"instance_spec": "compose.yaml"})
    seen: list[str] = []
    monkeypatch.setattr(
        runner_module, "test_container", lambda source, channel, probes=None: seen.append(source) or ["ok"]
    )
    (row,) = runner_module.run_container_tests(tmp_path, None)
    assert row["result"]["success"], row["result"]
    assert seen == [COMPOSE]
    assert row["result"]["warnings"] == []


@respx.mock
def test_run_tests_downloads_a_url_spec(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    make_service(tmp_path, {"instance_spec": URL})
    respx.get(URL).mock(return_value=httpx.Response(200, text=COMPOSE))
    seen: list[str] = []
    monkeypatch.setattr(
        runner_module, "test_container", lambda source, channel, probes=None: seen.append(source) or ["ok"]
    )
    (row,) = runner_module.run_container_tests(tmp_path, None)
    assert row["result"]["success"], row["result"]
    assert seen == [COMPOSE]


def test_find_instance_spec_needs_exactly_one() -> None:
    assert find_instance_spec({}) is None
    two = {"instance_spec": "a.yaml", "documents": {"X": {"category": "instance_spec", "file_path": "b.yaml"}}}
    assert find_instance_spec(two) is None
