"""Publishing platform services and the member-services rename (unitysvc/unitysvc#2569)."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
import respx

from unitysvc_sellers import Client
from unitysvc_sellers.params_render import service_name_for_param, validate_system_param_file
from unitysvc_sellers.platform_services import (
    build_platform_service_payload,
    find_platform_service_folders,
    load_member_template,
)
from unitysvc_sellers.specs_layout import find_service_folders
from unitysvc_sellers.upload import upload_directory
from unitysvc_sellers.utils import find_files_by_pattern

BASE_URL = "https://seller.staging.unitysvc.test"
SERVICE_ID = "98fc91f6-cb84-4cef-9c97-35b23e3f5c47"
TEMPLATE_ID = "0499bf65-978c-4c27-b615-28215c1b0d3b"


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def _platform_service(root: Path, *, service_id: str | None = None, template_id: str | None = None) -> Path:
    """``platform-services/labs/llm-fast/`` with its member template."""
    folder = root / "platform-services" / "labs" / "llm-fast"
    _write(
        folder / "provider.json",
        {
            "name": "labs",
            "display_name": "UnitySVC Labs",
            "contact_email": "labs@unitysvc.com",
            "homepage": "https://unitysvc.com",
            "status": "ready",
        },
    )
    _write(
        folder / "offering.json",
        {
            "name": "labs/llm-fast",
            "service_type": "llm",
            "summary": "Fast chat.",
            "description": "Fast chat routed across providers.",
            "details": {"context_length": None, "parameter_count": None},
            "status": "ready",
        },
    )
    _write(
        folder / "listing.json",
        {
            "name": "labs/llm-fast",
            "status": "ready",
            "list_price": {"type": "one_million_tokens", "input": "0.2", "output": "0.4"},
            "user_access_interfaces": {
                "default": {
                    "access_method": "http",
                    "base_url": "${API_GATEWAY_BASE_URL}/p/llm",
                    "routing_key": {"model": "fast"},
                }
            },
        },
    )
    if service_id:
        _write(folder / "llm-fast.service.json", {"service_id": service_id})
    template = folder / "member-template"
    _write(
        template / "template.json",
        {
            "name": "llm-fast",
            "version": "v1",
            "display_name": "Fast LLM Platform Member",
            "service_type": "llm",
            "status": "active",
            "parameter_schema": {"type": "object", "properties": {}},
        },
    )
    for body in ("offering", "listing", "provider"):
        (template / f"{body}.json.j2").write_text("{}\n")
    if template_id:
        _write(template / "template_id.json", {"id": template_id, "name": "llm-fast"})
    return folder


# --- discovery ----------------------------------------------------------------


def test_platform_service_folders_are_found_and_kept_out_of_ordinary_discovery(tmp_path: Path) -> None:
    folder = _platform_service(tmp_path)
    regular = tmp_path / "specs" / "acme" / "svc1"
    _write(regular / "listing.json", {"name": "acme/svc1"})

    assert find_platform_service_folders(tmp_path) == [folder]
    ordinary = [p for p, _, _ in find_files_by_pattern(tmp_path, "listing_v1")]
    assert ordinary == [regular / "listing.json"]
    assert find_service_folders(tmp_path) == [regular]


# --- payload ------------------------------------------------------------------


def test_member_template_is_named_after_its_platform_service(tmp_path: Path) -> None:
    folder = _platform_service(tmp_path, template_id=TEMPLATE_ID)

    body = load_member_template(folder)

    assert body["name"] == "llm-fast"
    assert body["id"] == TEMPLATE_ID
    assert body["offering_template"] == "{}\n"
    assert {"listing_template", "provider_template"} <= body.keys()


def test_a_member_template_named_differently_is_refused(tmp_path: Path) -> None:
    folder = _platform_service(tmp_path)
    meta = folder / "member-template" / "template.json"
    data = json.loads(meta.read_text())
    data["name"] = "something-else"
    meta.write_text(json.dumps(data))

    with pytest.raises(ValueError, match="does not match the platform service folder"):
        load_member_template(folder)


def test_ids_are_optional(tmp_path: Path) -> None:
    folder = _platform_service(tmp_path)

    payload = build_platform_service_payload(folder)

    assert "service_status" not in payload
    assert "id" not in payload["member_template"]
    assert payload["service_data"]["listing_data"]["name"] == "labs/llm-fast"


def test_the_service_id_sidecar_targets_the_existing_platform_service(tmp_path: Path) -> None:
    folder = _platform_service(tmp_path, service_id=SERVICE_ID)

    payload = build_platform_service_payload(folder)

    assert payload["service_status"] == {"service_id": SERVICE_ID}


# --- upload -------------------------------------------------------------------


@respx.mock
def test_upload_publishes_through_its_own_endpoint_and_writes_both_ids_back(tmp_path: Path) -> None:
    folder = _platform_service(tmp_path)
    ordinary = respx.post(f"{BASE_URL}/services").mock(return_value=httpx.Response(500))
    publish = respx.post(f"{BASE_URL}/platform-services").mock(
        return_value=httpx.Response(202, json={"task_id": "task-ps", "status": "queued", "message": "queued"})
    )
    respx.get(url__startswith=f"{BASE_URL}/tasks/").mock(
        return_value=httpx.Response(
            200,
            json={
                "task-ps": {
                    "task_id": "task-ps",
                    "state": "SUCCESS",
                    "status": "completed",
                    "message": "ok",
                    "result": {
                        "service_id": SERVICE_ID,
                        "name": "labs/llm-fast",
                        "status": "updated",
                        "member_template_id": TEMPLATE_ID,
                        "member_template": "updated",
                    },
                }
            },
        )
    )

    with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
        result = upload_directory(client, tmp_path, task_poll_interval=0.001, task_wait_timeout=5.0)

    assert result.services.total == 1
    assert result.services.success == 1, result.services.errors
    assert not ordinary.called
    body = json.loads(publish.calls.last.request.content)
    assert body["service_data"]["listing_data"]["name"] == "labs/llm-fast"
    assert body["member_template"]["name"] == "llm-fast"
    assert json.loads((folder / "llm-fast.service.json").read_text()) == {"service_id": SERVICE_ID}
    assert json.loads((folder / "member-template" / "template_id.json").read_text()) == {
        "id": TEMPLATE_ID,
        "name": "llm-fast",
    }


@respx.mock
def test_upload_by_name_selects_a_platform_service(tmp_path: Path) -> None:
    _platform_service(tmp_path)
    publish = respx.post(f"{BASE_URL}/platform-services").mock(
        return_value=httpx.Response(202, json={"task_id": "task-ps", "status": "queued", "message": "queued"})
    )
    respx.get(url__startswith=f"{BASE_URL}/tasks/").mock(
        return_value=httpx.Response(200, json={"task-ps": {"task_id": "task-ps", "status": "completed", "result": {}}})
    )

    with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
        result = upload_directory(
            client, tmp_path, name="labs/llm-fast", task_poll_interval=0.001, task_wait_timeout=5.0
        )

    assert result.services.total == 1
    assert publish.called


# --- member-services ------------------------------------------------------------


@pytest.mark.parametrize("dirname", ["member-services", "platform_services"])
def test_member_param_service_name_comes_from_the_member_services_path(tmp_path: Path, dirname: str) -> None:
    """``member-services/`` is the name; the pre-#2569 ``platform_services/`` still works."""
    (tmp_path / "services" / "templates").mkdir(parents=True)
    param = tmp_path / dirname / "llm-fast" / "parasail" / "glm-5.2.json"
    _write(
        param,
        {"template": "llm-fast", "parameters": {"model": "glm-5.2", "service_name": "llm-fast/parasail/glm-5.2"}},
    )

    assert service_name_for_param(param) == "llm-fast/parasail/glm-5.2"
    assert validate_system_param_file(param) == []


def test_a_member_service_name_must_match_its_member_services_path(tmp_path: Path) -> None:
    (tmp_path / "services" / "templates").mkdir(parents=True)
    param = tmp_path / "member-services" / "llm-fast" / "parasail" / "glm-5.2.json"
    _write(param, {"template": "llm-fast", "parameters": {"service_name": "llm-fast/parasail/other"}})

    errors = validate_system_param_file(param)

    assert errors and "must match the path under member-services" in errors[0]
