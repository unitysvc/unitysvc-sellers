"""Container specs use the existing upload API and document transport."""

import json

import httpx
import respx

from unitysvc_sellers import Client


@respx.mock
def test_existing_upload_preserves_container_spec_and_channel_fields() -> None:
    channel = {
        "access_method": "container",
        "resources": "nano",
        "entries": [{"name": "api", "service": "web", "port": 8080, "auth": "app"}],
    }
    document = {
        "category": "instance_spec",
        "mime_type": "text",
        "meta": {"format": "compose"},
        "file_content": "services:\n  web:\n    image: example/web@sha256:" + "a" * 64 + "\n",
    }
    payload = {
        "data": {
            "provider_data": {
                "name": "example",
                "contact_email": "seller@example.com",
                "homepage": "https://example.com",
                "status": "ready",
            },
            "offering_data": {
                "name": "web",
                "summary": "One container per enrollment",
                "description": "A container service uploaded through the existing service API.",
                "service_type": "container",
                "status": "ready",
                "documents": {"Application": document},
                "upstream_access_config": {"base": channel},
            },
            "listing_data": {"name": "example/web", "status": "ready"},
        }
    }
    route = respx.post("https://seller.test/v1/services").mock(
        return_value=httpx.Response(
            202,
            json={"status": "queued", "message": "Queued", "task_id": "container-upload"},
        )
    )

    with Client(api_key="svcpass_test_key", base_url="https://seller.test/v1") as client:
        assert client.services.upload(payload).task_id == "container-upload"

    sent = json.loads(route.calls[0].request.content)["data"]["offering_data"]
    assert sent["service_type"] == "container"
    assert sent["upstream_access_config"]["base"] == channel
    assert sent["documents"]["Application"] == document
