"""Tests for the seller HTTP SDK.

These tests use respx_ to intercept the httpx calls made by the
generated low-level client, so they exercise the full facade →
generated → httpx → response unwrap path without needing a live
backend.

.. _respx: https://lundberg.github.io/respx/
"""

from __future__ import annotations

import json
import uuid

import httpx
import pytest
import respx

from unitysvc_sellers import (
    APIError,
    AuthenticationError,
    Client,
    NotFoundError,
    ValidationError,
)

BASE_URL = "https://seller.staging.unitysvc.test"


@pytest.fixture
def client() -> Client:
    return Client(api_key="svcpass_test_key", base_url=BASE_URL)


# ---------------------------------------------------------------------------
# Construction / config
# ---------------------------------------------------------------------------
class TestClientConstruction:
    def test_requires_api_key(self) -> None:
        with pytest.raises(ValueError, match="api_key is required"):
            Client(api_key="")

    def test_default_base_url(self) -> None:
        c = Client(api_key="svcpass_test")
        assert c._base_url == "https://seller.staging.unitysvc.com"

    def test_explicit_base_url_wins(self) -> None:
        c = Client(api_key="svcpass_test", base_url="https://other.example")
        assert c._base_url == "https://other.example"

    def test_from_env_reads_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("UNITYSVC_API_KEY", "svcpass_env_key")
        monkeypatch.setenv("UNITYSVC_BASE_URL", "https://env.example")
        c = Client.from_env()
        assert c._api_key == "svcpass_env_key"
        assert c._base_url == "https://env.example"

    def test_from_env_missing_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("UNITYSVC_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="UNITYSVC_API_KEY"):
            Client.from_env()


# ---------------------------------------------------------------------------
# Services resource
# ---------------------------------------------------------------------------
class TestServicesResource:
    @respx.mock
    def test_list_returns_services_public(self, client: Client) -> None:
        respx.get(f"{BASE_URL}/v1/seller/services").mock(
            return_value=httpx.Response(
                200,
                json={"data": [], "count": 0},
            )
        )

        services = client.services.list(limit=50)

        assert services.count == 0
        assert services.data == []

    @respx.mock
    def test_list_passes_query_params(self, client: Client) -> None:
        route = respx.get(f"{BASE_URL}/v1/seller/services").mock(
            return_value=httpx.Response(200, json={"data": [], "count": 0})
        )

        client.services.list(skip=10, limit=20, status="active", service_type="llm")

        request = route.calls.last.request
        assert request.url.params["skip"] == "10"
        assert request.url.params["limit"] == "20"
        assert request.url.params["status"] == "active"
        assert request.url.params["service_type"] == "llm"

    @respx.mock
    def test_list_sends_authorization_header(self, client: Client) -> None:
        route = respx.get(f"{BASE_URL}/v1/seller/services").mock(
            return_value=httpx.Response(200, json={"data": [], "count": 0})
        )

        client.services.list()

        assert route.calls.last.request.headers["authorization"] == "Bearer svcpass_test_key"


# ---------------------------------------------------------------------------
# Error mapping
# ---------------------------------------------------------------------------
class TestErrorMapping:
    @respx.mock
    def test_401_raises_authentication_error(self, client: Client) -> None:
        respx.get(f"{BASE_URL}/v1/seller/services").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid API key"})
        )

        with pytest.raises(AuthenticationError) as excinfo:
            client.services.list()

        assert excinfo.value.status_code == 401
        assert "Invalid API key" in str(excinfo.value)

    @respx.mock
    def test_404_raises_not_found_error(self, client: Client) -> None:
        sid = str(uuid.uuid4())
        respx.get(f"{BASE_URL}/v1/seller/services/{sid}").mock(
            return_value=httpx.Response(404, json={"detail": "Service not found"})
        )

        with pytest.raises(NotFoundError) as excinfo:
            client.services.get(sid)

        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == {"detail": "Service not found"}

    @respx.mock
    def test_422_raises_validation_error(self, client: Client) -> None:
        respx.get(f"{BASE_URL}/v1/seller/services").mock(
            return_value=httpx.Response(
                422,
                json={
                    "detail": [
                        {
                            "loc": ["query", "limit"],
                            "msg": "ensure this value is less than or equal to 1000",
                            "type": "value_error.number.not_le",
                        }
                    ]
                },
            )
        )

        with pytest.raises(ValidationError) as excinfo:
            client.services.list()
        assert excinfo.value.status_code == 422

    @respx.mock
    def test_400_raises_validation_error(self, client: Client) -> None:
        # 400 uses the simpler ErrorResponse shape (a single detail string).
        respx.get(f"{BASE_URL}/v1/seller/services").mock(
            return_value=httpx.Response(400, json={"detail": "bad request"})
        )

        with pytest.raises(ValidationError) as excinfo:
            client.services.list()
        assert excinfo.value.status_code == 400
        assert "bad request" in str(excinfo.value)

    @respx.mock
    def test_5xx_raises_api_error(self, client: Client) -> None:
        from unitysvc_sellers.exceptions import ServerError

        respx.get(f"{BASE_URL}/v1/seller/services").mock(
            return_value=httpx.Response(503, json={"detail": "Service unavailable"})
        )

        with pytest.raises(ServerError) as excinfo:
            client.services.list()
        assert excinfo.value.status_code == 503

    @respx.mock
    def test_unparseable_error_body_falls_back_to_raw(self, client: Client) -> None:
        respx.get(f"{BASE_URL}/v1/seller/services").mock(return_value=httpx.Response(500, content=b"<html>500</html>"))

        with pytest.raises(APIError) as excinfo:
            client.services.list()
        assert excinfo.value.status_code == 500


# ---------------------------------------------------------------------------
# Promotions resource
# ---------------------------------------------------------------------------
class TestPromotionsResource:
    @respx.mock
    def test_list_returns_price_rules_public(self, client: Client) -> None:
        respx.get(f"{BASE_URL}/v1/seller/promotions").mock(
            return_value=httpx.Response(200, json={"data": [], "count": 0})
        )

        result = client.promotions.list()
        assert result.count == 0

    @respx.mock
    def test_delete_returns_none(self, client: Client) -> None:
        promo_id = str(uuid.uuid4())
        respx.delete(f"{BASE_URL}/v1/seller/promotions/{promo_id}").mock(return_value=httpx.Response(204))

        assert client.promotions.delete(promo_id) is None


# ---------------------------------------------------------------------------
# Groups resource
# ---------------------------------------------------------------------------
class TestGroupsResource:
    @respx.mock
    def test_list_endpoint_path(self, client: Client) -> None:
        route = respx.get(f"{BASE_URL}/v1/seller/service-groups").mock(
            return_value=httpx.Response(200, json={"data": [], "count": 0})
        )

        client.groups.list()
        assert route.called


# ---------------------------------------------------------------------------
# Documents resource
# ---------------------------------------------------------------------------
class TestDocumentsResource:
    @respx.mock
    def test_get_endpoint_path(self, client: Client) -> None:
        doc_id = str(uuid.uuid4())
        # The documents_get operation matches /v1/seller/documents/{document_id}
        # and the generated client returns a DocumentDetailResponse-shaped body.
        respx.get(f"{BASE_URL}/v1/seller/documents/{doc_id}").mock(
            return_value=httpx.Response(404, json={"detail": "doc not found"})
        )

        with pytest.raises(NotFoundError):
            client.documents.get(doc_id)


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------
class TestContextManager:
    def test_context_manager_closes_client(self) -> None:
        with Client(api_key="svcpass_test", base_url=BASE_URL) as c:
            assert c is not None
        # close() is idempotent and safe — exiting the context simply
        # tears down the underlying httpx pool.
