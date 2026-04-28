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


def _service_update_response(**overrides) -> dict:
    base = {
        "id": str(uuid.uuid4()),
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
    async def test_services_update_sends_body(self) -> None:
        sid = uuid.uuid4()
        route = respx.patch(f"{BASE_URL}/services/{sid}").mock(
            return_value=httpx.Response(
                200,
                json=_service_update_response(id=str(sid), status="deprecated"),
            )
        )

        async with AsyncClient(api_key="svcpass_test", base_url=BASE_URL) as client:
            await client.services.update(sid, {"status": "deprecated"})

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
def _service_detail_with_docs(
    service_id: str,
    doc_ids: list[str],
    status: str = "active",
    base_url: str = "http://127.0.0.1:65535/p/svc",
    interface_id: str | None = None,
) -> dict:
    """Build a ServiceDetailResponse-shaped payload.

    The generated ``ServiceDetailResponse.from_dict`` requires
    ``service_id`` / ``status`` / ``documents`` / ``interfaces``.

    ``base_url`` on the stub interface defaults to an unreachable
    127.0.0.1:65535 so the bash script the CLI executes fails fast
    with an exit code we can assert on. Override if a test wants to
    hit a real mocked endpoint.

    ``interface_id`` lets the caller pin the access-interface UUID so
    the matching ``GET /documents/{id}/render?interface=<uuid>`` mock can
    be set up with the same id; defaults to a fresh random UUID.
    """
    iface_id = interface_id or str(uuid.uuid4())
    return {
        "service_id": service_id,
        "service_name": "svc1",
        "status": status,
        "documents": [
            {
                "id": did,
                "title": f"Example {i}",
                "category": "code_example",
                "mime_type": "bash",
                "test_status": "pending",
            }
            for i, did in enumerate(doc_ids)
        ],
        "interfaces": [
            {
                "id": iface_id,
                "service_id": service_id,
                "access_method": "http",
                "name": "default",
                "base_url": base_url,
                "is_active": True,
                "is_primary": True,
                "sort_order": 0,
                "has_api_key": False,
                "created_at": "2026-01-01T00:00:00Z",
            }
        ],
    }


def _document_render(
    document_id: str,
    *,
    content: str,
    mime_type: str = "bash",
    filename: str = "test.sh",
) -> dict:
    """Minimal ``DocumentRenderResponse``-shaped payload.

    ``GET /seller/documents/{id}/render?interface=<uuid>`` returns the
    Jinja2-expanded script body for a code-example / connectivity-test
    against a specific user access interface.  ``run-tests`` reads
    ``content`` and ``mime_type`` and runs the rest as the seller's
    subprocess — env-var injection beyond ``UNITYSVC_API_KEY`` is no
    longer needed because every interface-specific value (gateway URL,
    routing_key, …) is already inlined in ``content``.
    """
    return {
        "document_id": document_id,
        "filename": filename,
        "content": content,
        "mime_type": mime_type,
        "local_testing": False,
    }


def _document_detail(
    did: str,
    *,
    file_content: str,
    mime_type: str = "bash",
) -> dict:
    """Minimal DocumentDetailResponse-shaped payload for run-tests.

    run-tests issues ``GET /documents/{id}`` to pull the expanded
    ``file_content`` + ``mime_type`` before executing locally. Only
    the fields the command actually reads are populated.
    """
    return {
        "id": did,
        "title": "Connectivity test",
        "category": "code_example",
        "mime_type": mime_type,
        "filename": "test.sh",
        "is_active": True,
        "is_public": False,
        "context_type": "service_listing",
        "entity_id": str(uuid.uuid4()),
        "file_content": file_content,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }


class TestRunTestsLocalExecution:
    """run-tests runs scripts LOCALLY on the seller's machine.

    The legacy ``usvc services run-tests`` flow (in
    ``unitysvc-services``) pulls each document's expanded
    ``file_content`` from the backend, elevates draft/rejected
    services to pending so the gateway will route, runs the scripts
    with ``execute_script_content`` against the interface's
    resolved ``base_url``, and PATCHes the results back to
    ``/seller/documents/{id}``. These tests cover that flow end-to-end
    with the backend mocked out — the script itself runs for real via
    a subprocess so we can observe exit codes.
    """

    @respx.mock
    def test_runs_scripts_locally_and_patches_results(
        self,
        runner: CliRunner,
        env: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A trivial success script runs, exits 0, and the CLI PATCHes it back."""
        service_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        doc_id = "11111111-1111-1111-1111-111111111111"
        iface_id = "ffffffff-ffff-ffff-ffff-ffffffffff01"

        monkeypatch.setenv("UNITYSVC_API_KEY", "svcpass_local_test")

        respx.get(f"{BASE_URL}/services/{service_id}").mock(
            return_value=httpx.Response(
                200,
                json=_service_detail_with_docs(service_id, [doc_id], status="active", interface_id=iface_id),
            )
        )

        # Doc-detail GET still happens once per doc (used for skip-state
        # logic and meta).  Body is otherwise unused now that the rendered
        # script comes from the render endpoint.
        respx.get(f"{BASE_URL}/documents/{doc_id}").mock(
            return_value=httpx.Response(
                200,
                json=_document_detail(doc_id, file_content="ignored"),
            )
        )

        # Script with the gateway URL already inlined — that's what the
        # backend's /render endpoint produces (no env-var read; only
        # ``UNITYSVC_API_KEY`` is consulted at execution time).
        success_script = 'echo "hit=https://gw.example.com/p/svc"\nexit 0\n'
        respx.get(
            f"{BASE_URL}/documents/{doc_id}/render",
            params={"interface": iface_id},
        ).mock(
            return_value=httpx.Response(
                200,
                json=_document_render(doc_id, content=success_script),
            )
        )

        patch_route = respx.patch(f"{BASE_URL}/documents/{doc_id}").mock(
            return_value=httpx.Response(
                200,
                json={"id": doc_id, "status": "success", "message": "ok"},
            )
        )

        result = runner.invoke(
            cli_app,
            ["services", "run-tests", service_id, "--force"],
        )

        assert result.exit_code == 0, result.stdout
        assert "success" in result.stdout

        # Results were POSTed back — body carries per-interface shape
        # and the rolled-up status. Per-interface results are keyed by
        # access_interface.id (so documents shared across services
        # don't collide) with the display name carried inside the entry.
        body = json.loads(patch_route.calls.last.request.content.decode())
        assert body["status"] == "success"
        assert "tests" in body
        assert len(body["tests"]) == 1
        entry = next(iter(body["tests"].values()))
        assert entry["status"] == "success"
        assert entry["name"] == "default"

    @respx.mock
    def test_elevates_draft_service_and_restores_status(
        self,
        runner: CliRunner,
        env: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """draft → pending before tests, then back to draft after.

        The gateway route resolver only accepts services in
        pending/review/active. The legacy test runner bumps draft or
        rejected services to pending (with ``run_tests=False`` so the
        backend does NOT auto-queue its own Celery run), runs tests,
        then restores the original status. This test verifies that
        both PATCH /services/{id} calls happen in order.
        """
        service_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        doc_id = "22222222-2222-2222-2222-222222222222"
        iface_id = "ffffffff-ffff-ffff-ffff-ffffffffff02"

        monkeypatch.setenv("UNITYSVC_API_KEY", "svcpass_local_test")

        respx.get(f"{BASE_URL}/services/{service_id}").mock(
            return_value=httpx.Response(
                200,
                json=_service_detail_with_docs(service_id, [doc_id], status="draft", interface_id=iface_id),
            )
        )
        respx.get(f"{BASE_URL}/documents/{doc_id}").mock(
            return_value=httpx.Response(
                200,
                json=_document_detail(doc_id, file_content="ignored"),
            )
        )
        respx.get(
            f"{BASE_URL}/documents/{doc_id}/render",
            params={"interface": iface_id},
        ).mock(
            return_value=httpx.Response(
                200,
                json=_document_render(doc_id, content="exit 0\n"),
            )
        )
        respx.patch(f"{BASE_URL}/documents/{doc_id}").mock(
            return_value=httpx.Response(
                200,
                json={"id": doc_id, "status": "success", "message": "ok"},
            )
        )
        set_status_route = respx.patch(f"{BASE_URL}/services/{service_id}").mock(
            return_value=httpx.Response(
                200,
                json={"id": service_id},
            )
        )

        result = runner.invoke(
            cli_app,
            ["services", "run-tests", service_id, "--force"],
        )

        assert result.exit_code == 0, result.stdout
        # Two PATCH /services/{id} calls: elevate to pending, restore to draft.
        assert set_status_route.call_count == 2
        bodies = [json.loads(c.request.content.decode()) for c in set_status_route.calls]
        assert bodies[0]["status"] == "pending"
        assert bodies[0]["run_tests"] is False
        assert bodies[1]["status"] == "draft"
        assert bodies[1]["run_tests"] is False

    @respx.mock
    def test_failing_script_surfaces_stderr_and_exits_nonzero(
        self,
        runner: CliRunner,
        env: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A script that exits non-zero is reported as script_failed."""
        service_id = "dddddddd-dddd-dddd-dddd-dddddddddddd"
        doc_id = "33333333-3333-3333-3333-333333333333"
        iface_id = "ffffffff-ffff-ffff-ffff-ffffffffff03"

        monkeypatch.setenv("UNITYSVC_API_KEY", "svcpass_local_test")

        respx.get(f"{BASE_URL}/services/{service_id}").mock(
            return_value=httpx.Response(
                200,
                json=_service_detail_with_docs(service_id, [doc_id], status="active", interface_id=iface_id),
            )
        )
        respx.get(f"{BASE_URL}/documents/{doc_id}").mock(
            return_value=httpx.Response(
                200,
                json=_document_detail(doc_id, file_content="ignored"),
            )
        )
        # Script always fails with exit 7 — mirrors the curl
        # "connection refused" class of failures the seller hits
        # when the gateway URL is wrong.  Coming from the render
        # endpoint, not from the doc detail.
        respx.get(
            f"{BASE_URL}/documents/{doc_id}/render",
            params={"interface": iface_id},
        ).mock(
            return_value=httpx.Response(
                200,
                json=_document_render(doc_id, content='echo "boom" >&2\nexit 7\n'),
            )
        )
        respx.patch(f"{BASE_URL}/documents/{doc_id}").mock(
            return_value=httpx.Response(
                200,
                json={"id": doc_id, "status": "script_failed", "message": "ok"},
            )
        )

        result = runner.invoke(
            cli_app,
            ["services", "run-tests", service_id, "--force"],
        )

        assert result.exit_code == 1
        assert "script_failed" in result.stdout


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
