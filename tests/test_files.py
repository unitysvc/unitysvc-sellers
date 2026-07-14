"""Unit tests for :class:`unitysvc_sellers.files.Files` (unitysvc#1533).

Exercises the seller account-files surface against mocked ``httpx``
transports. Two hosts are in play: the UnitySVC API (mint/list/presign —
mocked via the generated client's transport) and the storage endpoint
(upload POST / download GET — mocked by monkeypatching ``httpx.Client``,
since the facade deliberately uses a bare client so the storage host
never sees the API key).
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from unitysvc_sellers import Client

TICKET = {
    "key": "exports/result.json",
    "url": "https://storage.example/account-files",
    "fields": {
        "policy": "signed-policy",
        "key": "sellers/seller-id/exports/result.json",
    },
    "expires_in": 900,
    "max_bytes": 1073741824,
}


def _api_transport(payload: dict, captured: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json=payload)

    return httpx.MockTransport(handler)


def _patch_storage(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    """Make bare ``httpx.Client(...)`` calls hit a mock storage transport."""
    real_client = httpx.Client

    def fake_client(**kwargs):
        kwargs.pop("transport", None)
        return real_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr("unitysvc_sellers.files.httpx.Client", fake_client)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
def test_list_sends_path() -> None:
    payload = {
        "path": "exports/",
        "objects": [{"key": "exports/result.json", "size": 42, "last_modified": "2026-07-14T12:00:00"}],
        "common_prefixes": ["exports/2026/"],
        "is_truncated": False,
        "next_continuation_token": None,
    }
    captured: list[httpx.Request] = []
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _api_transport(payload, captured)
        resp = client.files.list("exports")

    assert captured[0].url.path.endswith("/files/list")
    assert captured[0].url.params["path"] == "exports"
    assert [o.key for o in resp.objects] == ["exports/result.json"]
    assert resp.common_prefixes == ["exports/2026/"]


# ---------------------------------------------------------------------------
# upload — mint via API, then multipart POST to storage
# ---------------------------------------------------------------------------
def test_upload_mints_then_posts_fields_before_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "result.json"
    src.write_bytes(b"hello")

    api_captured: list[httpx.Request] = []
    storage_captured: list[httpx.Request] = []

    def storage_handler(request: httpx.Request) -> httpx.Response:
        storage_captured.append(request)
        return httpx.Response(204)

    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _api_transport(TICKET, api_captured)
        _patch_storage(monkeypatch, storage_handler)
        key = client.files.upload(src, "exports")

    assert key == "exports/result.json"

    # Mint request: key parts only — never a full key or bucket.
    mint = json.loads(api_captured[0].content)
    assert mint["filename"] == "result.json"
    assert mint["size"] == 5
    assert mint["path"] == "exports"
    assert "scope" not in mint  # sellers have no scopes

    # Storage POST: multipart with every policy field, and the file LAST.
    body = storage_captured[0].content
    assert storage_captured[0].url == TICKET["url"]
    for field in TICKET["fields"]:
        assert f'name="{field}"'.encode() in body
    assert body.index(b'name="policy"') < body.index(b'name="file"')
    assert b"hello" in body
    # The API key must never reach the storage host.
    assert "authorization" not in {k.lower() for k in storage_captured[0].headers}
    assert "svcpass_test" not in str(storage_captured[0].headers)


def test_upload_storage_rejection_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from unitysvc_sellers.exceptions import APIError

    src = tmp_path / "big.bin"
    src.write_bytes(b"x" * 10)

    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _api_transport(TICKET, [])
        _patch_storage(
            monkeypatch,
            lambda request: httpx.Response(400, text="EntityTooLarge"),
        )
        with pytest.raises(APIError, match="EntityTooLarge"):
            client.files.upload(src)


# ---------------------------------------------------------------------------
# download — presign via API, then GET from storage
# ---------------------------------------------------------------------------
def test_download_streams_to_dest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    presign = {
        "key": "exports/result.json",
        "url": "https://storage.example/presigned?sig=abc",
        "expires_in": 900,
    }
    api_captured: list[httpx.Request] = []
    storage_captured: list[httpx.Request] = []

    def storage_handler(request: httpx.Request) -> httpx.Response:
        storage_captured.append(request)
        return httpx.Response(200, content=b"json-bytes")

    dest = tmp_path / "local.json"
    with Client(api_key="svcpass_test") as client:
        client._client.get_httpx_client()._transport = _api_transport(presign, api_captured)
        _patch_storage(monkeypatch, storage_handler)
        written = client.files.download("exports/result.json", dest)

    assert written == dest
    assert dest.read_bytes() == b"json-bytes"
    assert api_captured[0].url.path.endswith("/files/download")
    assert api_captured[0].url.params["key"] == "exports/result.json"
    assert str(storage_captured[0].url) == presign["url"]
    assert "authorization" not in {k.lower() for k in storage_captured[0].headers}
