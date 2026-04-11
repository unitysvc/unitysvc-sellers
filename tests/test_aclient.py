"""Tests for the async seller SDK and the CLI command groups it powers.

These exercise :class:`unitysvc_sellers.AsyncClient` directly and via
the Typer ``CliRunner``, mocking httpx with ``respx``.
"""

from __future__ import annotations

import json
import uuid

import httpx
import pytest
import respx
from typer.testing import CliRunner

from unitysvc_sellers import AsyncClient, NotFoundError
from unitysvc_sellers.cli import app as cli_app

BASE_URL = "https://seller.staging.unitysvc.test"


def _service_public(**overrides) -> dict:
    """Build a fully-populated ServicePublic dict for mocked list responses.

    The generated ``ServicePublic.from_dict`` requires id / seller_id /
    offering_id / listing_id / status / created_at and rejects bare
    payloads, so this fixture provides defaults that callers can
    override.
    """
    base = {
        "id": str(uuid.uuid4()),
        "seller_id": str(uuid.uuid4()),
        "offering_id": str(uuid.uuid4()),
        "listing_id": str(uuid.uuid4()),
        "status": "active",
        "created_at": "2026-01-01T00:00:00Z",
        "name": "svc",
        "provider_name": "acme",
        "service_type": "llm",
    }
    base.update(overrides)
    return base


def _price_rule_public(**overrides) -> dict:
    """Build a PriceRulePublic dict for mocked promotion responses."""
    base = {
        "id": str(uuid.uuid4()),
        "name": "promo",
        "source": "seller_code",
        "code": "PROMO",
        "scope": None,
        "pricing": {"type": "constant", "price": "1.00"},
        "apply_at": "request",
        "priority": 0,
        "status": "active",
        "created_by_id": str(uuid.uuid4()),
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


def _service_group_public(**overrides) -> dict:
    """Build a ServiceGroupPublic dict for mocked group responses."""
    base = {
        "id": str(uuid.uuid4()),
        "owner_id": str(uuid.uuid4()),
        "owner_type": "seller",
        "name": "group",
        "display_name": "group",
        "status": "active",
        "created_at": "2026-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


def _service_status_update_response(**overrides) -> dict:
    base = {
        "id": str(uuid.uuid4()),
        "status": "active",
        "message": "ok",
    }
    base.update(overrides)
    return base


def _document_execute_response(**overrides) -> dict:
    base = {
        "document_id": str(uuid.uuid4()),
        "status": "queued",
        "message": "queued",
    }
    base.update(overrides)
    return base


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "svcpass_test_key")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", BASE_URL)


# ---------------------------------------------------------------------------
# AsyncClient direct
# ---------------------------------------------------------------------------
class TestAsyncClient:
    @pytest.mark.asyncio
    @respx.mock
    async def test_services_list_returns_typed_payload(self) -> None:
        respx.get(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(
                200,
                json={"data": [_service_public(name="svc1")], "has_more": False},
            )
        )

        async with AsyncClient(api_key="svcpass_test", base_url=BASE_URL) as client:
            result = await client.services.list(limit=10)

        assert len(result.data) == 1
        assert result.data[0].name == "svc1"

    @pytest.mark.asyncio
    @respx.mock
    async def test_services_set_status_sends_body(self) -> None:
        sid = uuid.uuid4()
        route = respx.patch(f"{BASE_URL}/services/{sid}").mock(
            return_value=httpx.Response(
                200,
                json=_service_status_update_response(id=str(sid), status="deprecated"),
            )
        )

        async with AsyncClient(api_key="svcpass_test", base_url=BASE_URL) as client:
            await client.services.set_status(sid, {"status": "deprecated"})

        body = json.loads(route.calls.last.request.content.decode())
        assert body["status"] == "deprecated"

    @pytest.mark.asyncio
    @respx.mock
    async def test_promotions_list_async(self) -> None:
        respx.get(f"{BASE_URL}/promotions").mock(return_value=httpx.Response(200, json={"data": [], "has_more": False}))

        async with AsyncClient(api_key="svcpass_test", base_url=BASE_URL) as client:
            result = await client.promotions.list()

        assert result.data == []

    # NOTE: ``test_groups_refresh_calls_post`` was deleted — the
    # backend no longer exposes ``POST /service-groups/{id}/refresh``
    # (membership refresh is automatic on mutation, via a background
    # worker). ``client.groups.refresh()`` was removed accordingly.

    @pytest.mark.asyncio
    @respx.mock
    async def test_documents_execute_passes_force(self) -> None:
        did = uuid.uuid4()
        route = respx.post(f"{BASE_URL}/documents/{did}/execute").mock(
            return_value=httpx.Response(
                200,
                json=_document_execute_response(document_id=str(did)),
            )
        )

        async with AsyncClient(api_key="svcpass_test", base_url=BASE_URL) as client:
            await client.documents.execute(did, force=True)

        assert route.calls.last.request.url.params["force"] == "true"

    @pytest.mark.asyncio
    @respx.mock
    async def test_404_raises_not_found_async(self) -> None:
        sid = uuid.uuid4()
        respx.get(f"{BASE_URL}/services/{sid}").mock(return_value=httpx.Response(404, json={"detail": "missing"}))

        async with AsyncClient(api_key="svcpass_test", base_url=BASE_URL) as client:
            with pytest.raises(NotFoundError):
                await client.services.get(sid)


# ---------------------------------------------------------------------------
# CLI: services list / show
# ---------------------------------------------------------------------------
class TestServicesCommands:
    @respx.mock
    def test_list_renders_table(self, runner: CliRunner, env: None) -> None:
        respx.get(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        _service_public(
                            id="12345678-1234-1234-1234-123456789abc",
                            name="my-service",
                            provider_name="acme",
                            service_type="llm",
                            status="active",
                        )
                    ],
                    "count": 1,
                },
            )
        )

        result = runner.invoke(cli_app, ["services", "list"])

        assert result.exit_code == 0
        assert "my-service" in result.stdout
        assert "acme" in result.stdout

    @respx.mock
    def test_list_json_output(self, runner: CliRunner, env: None) -> None:
        respx.get(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(
                200,
                json={"data": [_service_public(name="svc1")], "count": 1},
            )
        )

        result = runner.invoke(cli_app, ["services", "list", "--format", "json"])
        assert result.exit_code == 0
        assert "svc1" in result.stdout

    @respx.mock
    def test_show_404(self, runner: CliRunner, env: None) -> None:
        respx.get(f"{BASE_URL}/services/abcdef12").mock(
            return_value=httpx.Response(404, json={"detail": "Service not found"})
        )

        result = runner.invoke(cli_app, ["services", "show", "abcdef12"])
        assert result.exit_code == 1
        assert "Failed to show service" in result.stdout

    @respx.mock
    def test_deprecate_calls_set_status(self, runner: CliRunner, env: None) -> None:
        sid = "12345678-1234-1234-1234-123456789abc"
        route = respx.patch(f"{BASE_URL}/services/{sid}").mock(
            return_value=httpx.Response(200, json={"id": sid, "status": "deprecated"})
        )

        result = runner.invoke(cli_app, ["services", "deprecate", sid, "--yes"])
        assert result.exit_code == 0
        body = json.loads(route.calls.last.request.content.decode())
        assert body["status"] == "deprecated"


# ---------------------------------------------------------------------------
# CLI: promotions
# ---------------------------------------------------------------------------
class TestPromotionsCommands:
    @respx.mock
    def test_list(self, runner: CliRunner, env: None) -> None:
        respx.get(f"{BASE_URL}/promotions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        _price_rule_public(
                            id="11111111-1111-1111-1111-111111111111",
                            name="promo1",
                            code="PROMO1",
                            status="active",
                            priority=5,
                        )
                    ],
                    "count": 1,
                },
            )
        )

        result = runner.invoke(cli_app, ["promotions", "list"])
        assert result.exit_code == 0
        assert "promo1" in result.stdout

    @respx.mock
    def test_activate_resolves_by_name_then_patches(self, runner: CliRunner, env: None) -> None:
        promo_id = "22222222-2222-2222-2222-222222222222"
        respx.get(f"{BASE_URL}/promotions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [_price_rule_public(id=promo_id, name="summer", status="draft")],
                    "count": 1,
                },
            )
        )
        patch_route = respx.patch(f"{BASE_URL}/promotions/{promo_id}").mock(
            return_value=httpx.Response(
                200,
                json=_price_rule_public(id=promo_id, name="summer", status="active"),
            )
        )

        result = runner.invoke(cli_app, ["promotions", "activate", "summer"])
        assert result.exit_code == 0
        body = json.loads(patch_route.calls.last.request.content.decode())
        assert body["status"] == "active"


# ---------------------------------------------------------------------------
# CLI: groups
# ---------------------------------------------------------------------------
class TestGroupsCommands:
    @respx.mock
    def test_list(self, runner: CliRunner, env: None) -> None:
        respx.get(f"{BASE_URL}/service-groups").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        _service_group_public(
                            id="33333333-3333-3333-3333-333333333333",
                            name="premium",
                            status="active",
                        )
                    ],
                    "count": 1,
                },
            )
        )

        result = runner.invoke(cli_app, ["groups", "list"])
        assert result.exit_code == 0
        assert "premium" in result.stdout

    # NOTE: ``test_refresh_resolves_by_name`` was deleted along with
    # the ``usvc_seller groups refresh`` CLI command. Group membership
    # refresh is now handled automatically by a background worker
    # whenever a group is mutated, so there is no manual refresh path
    # for sellers to invoke.


# ---------------------------------------------------------------------------
# CLI: services run-tests (polls Celery task status)
# ---------------------------------------------------------------------------
def _service_detail_with_docs(service_id: str, doc_ids: list[str]) -> dict:
    """Build a ServiceDetailResponse-shaped payload.

    The generated ``ServiceDetailResponse.from_dict`` requires
    ``service_id`` / ``status`` / ``documents`` / ``interfaces``;
    anything else is optional. Documents need ``id`` + ``category`` so
    ``_is_executable_doc`` treats them as runnable.
    """
    return {
        "service_id": service_id,
        "service_name": "svc1",
        "status": "active",
        "documents": [
            {
                "id": did,
                "title": f"Example {i}",
                "category": "code_example",
                "mime_type": "python",
                "test_status": "pending",
            }
            for i, did in enumerate(doc_ids)
        ],
        "interfaces": [],
    }


class TestRunTestsPolling:
    @respx.mock
    def test_reports_real_outcome_from_task_poll(self, runner: CliRunner, env: None) -> None:
        """run-tests must dispatch, then poll tasks until terminal.

        Previously the command walked away the instant the backend
        accepted the execute POST, so scripts that failed at runtime
        (wrong upstream key, 404, etc.) surfaced as "queued" and the
        overall run was reported as success. Now it polls
        ``/tasks/batch-status`` and prints the real per-document
        outcome.
        """
        service_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        ok_doc = "11111111-1111-1111-1111-111111111111"
        bad_doc = "22222222-2222-2222-2222-222222222222"

        respx.get(f"{BASE_URL}/services/{service_id}").mock(
            return_value=httpx.Response(
                200,
                json=_service_detail_with_docs(service_id, [ok_doc, bad_doc]),
            )
        )

        # Two executes → two queued responses, each with task_id == doc_id.
        respx.post(f"{BASE_URL}/documents/{ok_doc}/execute").mock(
            return_value=httpx.Response(
                200,
                json=_document_execute_response(
                    document_id=ok_doc,
                    status="queued",
                    task_id=ok_doc,
                ),
            )
        )
        respx.post(f"{BASE_URL}/documents/{bad_doc}/execute").mock(
            return_value=httpx.Response(
                200,
                json=_document_execute_response(
                    document_id=bad_doc,
                    status="queued",
                    task_id=bad_doc,
                ),
            )
        )

        respx.post(f"{BASE_URL}/tasks/batch-status").mock(
            return_value=httpx.Response(
                200,
                json={
                    ok_doc: {
                        "task_id": ok_doc,
                        "state": "SUCCESS",
                        "status": "completed",
                        "result": {
                            "status": "success",
                            "test": {"status": "success", "exit_code": 0},
                        },
                    },
                    bad_doc: {
                        "task_id": bad_doc,
                        "state": "SUCCESS",
                        "status": "completed",
                        "result": {
                            "status": "script_failed",
                            "test": {
                                "status": "script_failed",
                                "error": "Script exited with code 1",
                                "exit_code": 1,
                            },
                        },
                    },
                },
            )
        )

        result = runner.invoke(
            cli_app,
            [
                "services",
                "run-tests",
                service_id,
                "--force",
                "--poll-interval",
                "0.001",
                "--wait-timeout",
                "5.0",
            ],
        )

        # One doc passed, one failed → non-zero exit code.
        assert result.exit_code == 1
        # Per-doc status is printed — no silent "queued" for the failed one.
        assert "success" in result.stdout
        assert "script_failed" in result.stdout
        assert "Script exited with code 1" in result.stdout
        assert "Success: 1/2" in result.stdout
        assert "Failed: 1/2" in result.stdout

    @respx.mock
    def test_polling_404_surfaces_diagnostic(self, runner: CliRunner, env: None) -> None:
        """A 404 on /tasks/batch-status yields the composite-deployment hint."""
        service_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        doc_id = "33333333-3333-3333-3333-333333333333"

        respx.get(f"{BASE_URL}/services/{service_id}").mock(
            return_value=httpx.Response(
                200,
                json=_service_detail_with_docs(service_id, [doc_id]),
            )
        )
        respx.post(f"{BASE_URL}/documents/{doc_id}/execute").mock(
            return_value=httpx.Response(
                200,
                json=_document_execute_response(
                    document_id=doc_id,
                    status="queued",
                    task_id=doc_id,
                ),
            )
        )
        respx.post(f"{BASE_URL}/tasks/batch-status").mock(
            return_value=httpx.Response(404, json={"detail": "Not Found"})
        )

        result = runner.invoke(
            cli_app,
            [
                "services",
                "run-tests",
                service_id,
                "--poll-interval",
                "0.001",
                "--wait-timeout",
                "5.0",
            ],
        )

        assert result.exit_code == 1
        assert "task polling endpoint is missing" in result.stdout


# ---------------------------------------------------------------------------
# Auth env-fallback
# ---------------------------------------------------------------------------
class TestAuthEnvFallback:
    @respx.mock
    def test_missing_api_key_exits(self, runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("UNITYSVC_SELLER_API_KEY", raising=False)
        # Force the flag default to None
        result = runner.invoke(cli_app, ["services", "list"])
        assert result.exit_code == 1
        assert "Missing seller API key" in result.stdout

    @respx.mock
    def test_401_surfaces_authentication_error(self, runner: CliRunner, env: None) -> None:
        respx.get(f"{BASE_URL}/services").mock(return_value=httpx.Response(401, json={"detail": "Invalid API key"}))

        result = runner.invoke(cli_app, ["services", "list"])
        assert result.exit_code == 1
        assert "Invalid API key" in result.stdout
