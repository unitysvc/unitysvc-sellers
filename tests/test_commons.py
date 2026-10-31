"""Commons authoring and upload through the real CLI and generated SDK."""

import json
import shutil
from pathlib import Path

import httpx
import pytest
import respx
from typer.testing import CliRunner

from unitysvc_sellers import Client
from unitysvc_sellers.specs_layout import app
from unitysvc_sellers.upload import upload_directory

EXAMPLE = Path(__file__).parent / "fixtures" / "commons"
BASE = "https://seller.example/v1/seller"


@pytest.fixture
def commons(tmp_path):
    folder = tmp_path / "services" / "specs" / "commons"
    shutil.copytree(EXAMPLE, folder)
    return folder


@pytest.mark.parametrize("service_type", ["communication", "buy_and_sell", None])
@respx.mock
def test_resource_only_app_validates_and_uploads(commons, service_type):
    offering_path = commons / "offering.json"
    offering = json.loads(offering_path.read_text())
    if service_type is None:
        offering.pop("service_type")
    else:
        offering["service_type"] = service_type
    offering_path.write_text(json.dumps(offering))

    result = CliRunner().invoke(app, [str(commons.parents[2])])
    assert result.exit_code == 0, result.output

    respx.post(f"{BASE}/upload").mock(
        return_value=httpx.Response(
            200,
            json={
                "object_key": "docs/commons",
                "filename": "commons",
                "mime_type": "text/plain",
                "size": 1,
                "uploaded": True,
            },
        )
    )
    uploaded = respx.post(f"{BASE}/services").mock(
        return_value=httpx.Response(202, json={"task_id": "commons", "status": "queued", "message": "queued"})
    )
    respx.get(url__startswith=f"{BASE}/tasks/").mock(
        return_value=httpx.Response(
            200,
            json={
                "commons": {
                    "task_id": "commons",
                    "state": "SUCCESS",
                    "status": "completed",
                    "result": {"service_id": "commons-id"},
                }
            },
        )
    )
    with Client(api_key="svcpass_test", base_url=BASE) as client:
        outcome = upload_directory(client, commons.parents[2], task_poll_interval=0.001, task_wait_timeout=5)
    assert outcome.services.failed == 0, outcome.services.errors
    assert outcome.services.success == 1
    sent = json.loads(uploaded.calls[0].request.content)["data"]
    assert sent["offering_data"].get("service_type") == service_type
    free = sent["offering_data"]["upstream_access_config"]["free"]
    assert "base_url" not in free
    assert "access_method" not in free
    assert free["customer_access_requests"] == offering["upstream_access_config"]["free"]["customer_access_requests"]
    assert sent["listing_data"].get("user_access_interfaces") is None
    assert sent["listing_data"]["service_options"]["enrollment"]["limit_per_customer"] == 10


def test_unknown_room_kind_is_refused(commons):
    path = commons / "offering.json"
    offering = json.loads(path.read_text())
    offering["upstream_access_config"]["free"]["customer_access_requests"][0]["options"] = "kind=unknown"
    path.write_text(json.dumps(offering))
    result = CliRunner().invoke(app, [str(commons.parents[2])])
    assert result.exit_code == 1
    assert "kind" in result.output
