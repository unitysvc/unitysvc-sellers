"""Tests for ``client.enrollments`` (sync and async): cursor iteration and key leases."""

from __future__ import annotations

import json
import uuid

import httpx
import pytest
import respx

from unitysvc_sellers import AsyncClient, Client, ConflictError, NotFoundError

BASE_URL = "https://seller.staging.unitysvc.test"
SERVICE_ID = str(uuid.uuid4())
ENROLLMENT_ID = str(uuid.uuid4())


def _enrollment(**overrides: object) -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "service_id": SERVICE_ID,
        "channel": "default",
        "code": "ABC123",
        "status": "active",
        "parameters": {"city": "Houston"},
        "created_at": "2026-10-27T00:00:00Z",
        "updated_at": None,
        "expires_at": None,
    }
    row.update(overrides)
    return row


LEASE = {
    "key_id": str(uuid.uuid4()),
    "apikey_identifier": "abcdefgh12345678",
    "apikey": "svcpass_leased",
    "expires_at": "2026-10-27T01:00:00Z",
}


def _mock_two_pages() -> respx.Route:
    first, second = _enrollment(), _enrollment()

    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.params.get("cursor") is None:
            return httpx.Response(200, json={"data": [first], "next_cursor": "c1", "has_more": True})
        assert request.url.params["cursor"] == "c1"
        return httpx.Response(200, json={"data": [second], "next_cursor": None, "has_more": False})

    route = respx.get(f"{BASE_URL}/enrollments").mock(side_effect=respond)
    route.ids = [first["id"], second["id"]]  # type: ignore[attr-defined]
    return route


def _mock_lease() -> tuple[respx.Route, respx.Route]:
    lease = respx.post(f"{BASE_URL}/enrollments/{ENROLLMENT_ID}/lease").mock(
        return_value=httpx.Response(200, json=LEASE)
    )
    ret = respx.post(f"{BASE_URL}/enrollments/{ENROLLMENT_ID}/lease/return").mock(return_value=httpx.Response(204))
    return lease, ret


class TestSyncEnrollments:
    @respx.mock
    def test_iter_all_follows_cursor_and_passes_filters(self) -> None:
        route = _mock_two_pages()
        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            ids = [str(e.id) for e in client.enrollments.iter_all(service_id=SERVICE_ID, status="active", limit=1)]

        assert ids == route.ids  # type: ignore[attr-defined]
        params = route.calls[0].request.url.params
        assert params["service_id"] == SERVICE_ID
        assert params["status"] == "active"
        assert params["limit"] == "1"

    @respx.mock
    def test_list_returns_one_page(self) -> None:
        _mock_two_pages()
        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            page = client.enrollments.list()

        assert len(page.data) == 1
        assert page.has_more is True
        assert page.next_cursor == "c1"
        assert page.data[0].parameters.to_dict() == {"city": "Houston"}

    def test_list_rejects_unknown_status(self) -> None:
        with Client(api_key="svcpass_test", base_url=BASE_URL) as client, pytest.raises(TypeError):
            client.enrollments.list(status="bogus")

    @respx.mock
    def test_lease_key_releases_the_same_secret(self) -> None:
        lease, ret = _mock_lease()
        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            with client.enrollments.lease_key(ENROLLMENT_ID) as credential:
                assert credential.apikey == "svcpass_leased"
                assert ret.call_count == 0

        assert lease.call_count == 1
        assert json.loads(ret.calls[0].request.content) == {"apikey": "svcpass_leased"}

    @respx.mock
    def test_lease_key_releases_when_the_block_raises(self) -> None:
        _, ret = _mock_lease()
        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            with pytest.raises(RuntimeError, match="work failed"):
                with client.enrollments.lease_key(ENROLLMENT_ID):
                    raise RuntimeError("work failed")

        assert ret.call_count == 1

    @respx.mock
    def test_failed_release_does_not_mask_the_block_error(self) -> None:
        respx.post(f"{BASE_URL}/enrollments/{ENROLLMENT_ID}/lease").mock(return_value=httpx.Response(200, json=LEASE))
        respx.post(f"{BASE_URL}/enrollments/{ENROLLMENT_ID}/lease/return").mock(
            return_value=httpx.Response(500, json={"detail": "boom"})
        )
        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            with pytest.raises(RuntimeError, match="work failed"):
                with client.enrollments.lease_key(ENROLLMENT_ID):
                    raise RuntimeError("work failed")

    @respx.mock
    def test_acquire_errors_map_to_sdk_exceptions(self) -> None:
        route = respx.post(f"{BASE_URL}/enrollments/{ENROLLMENT_ID}/lease")
        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            route.mock(return_value=httpx.Response(404, json={"detail": "Enrollment not found"}))
            with pytest.raises(NotFoundError):
                client.enrollments.acquire_key(ENROLLMENT_ID)
            route.mock(return_value=httpx.Response(409, json={"detail": "Too many live keys"}))
            with pytest.raises(ConflictError):
                client.enrollments.acquire_key(ENROLLMENT_ID)


class TestAsyncEnrollments:
    @pytest.mark.asyncio
    @respx.mock
    async def test_iter_all_follows_cursor(self) -> None:
        route = _mock_two_pages()
        async with AsyncClient(api_key="svcpass_test", base_url=BASE_URL) as client:
            ids = [str(e.id) async for e in client.enrollments.iter_all(status="active")]

        assert ids == route.ids  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    @respx.mock
    async def test_lease_key_releases_when_the_block_raises(self) -> None:
        lease, ret = _mock_lease()
        async with AsyncClient(api_key="svcpass_test", base_url=BASE_URL) as client:
            with pytest.raises(RuntimeError):
                async with client.enrollments.lease_key(ENROLLMENT_ID) as credential:
                    assert credential.apikey == "svcpass_leased"
                    raise RuntimeError("work failed")

        assert lease.call_count == 1
        assert json.loads(ret.calls[0].request.content) == {"apikey": "svcpass_leased"}
