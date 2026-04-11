"""Tests for ``client.tasks`` and the polling path in ``client.upload``.

Covers the three shapes the polling flow has to handle:

* Every task reports ``completed`` → ``UploadResult.services.success``
  reflects the count; no errors; override files written.
* Any task reports ``failed`` with an ``error`` message → that entry
  shows up in ``UploadResult.services.errors`` with the backend's
  message (not the optimistic "queued" message).
* Polling times out before every task reaches terminal state → the
  still-running tasks are reported as failed with a timeout message,
  the finished-successfully tasks still count as success.
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import respx

from unitysvc_sellers import Client
from unitysvc_sellers.resources.upload import upload_directory

BASE_URL = "https://seller.staging.unitysvc.test"


# ---------------------------------------------------------------------------
# client.tasks — direct resource tests
# ---------------------------------------------------------------------------
class TestTasksResource:
    @respx.mock
    def test_get_single_task_success(self) -> None:
        respx.get(f"{BASE_URL}/tasks/task-123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "task_id": "task-123",
                    "state": "SUCCESS",
                    "status": "completed",
                    "message": "Task completed successfully",
                    "result": {"service_id": "svc-456", "name": "svc1"},
                },
            )
        )

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            status = client.tasks.get("task-123")

        assert status["status"] == "completed"
        assert status["result"]["service_id"] == "svc-456"

    @respx.mock
    def test_get_single_task_failure(self) -> None:
        respx.get(f"{BASE_URL}/tasks/task-456").mock(
            return_value=httpx.Response(
                200,
                json={
                    "task_id": "task-456",
                    "state": "FAILURE",
                    "status": "failed",
                    "message": "Task failed: ValueError: missing secret",
                    "error": "ValueError: Secret 'FIREWORKS_API_KEY' not found",
                },
            )
        )

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            status = client.tasks.get("task-456")

        assert status["status"] == "failed"
        assert "FIREWORKS_API_KEY" in status["error"]

    @respx.mock
    def test_batch_status_returns_mapping(self) -> None:
        route = respx.post(f"{BASE_URL}/tasks/batch-status").mock(
            return_value=httpx.Response(
                200,
                json={
                    "task-a": {
                        "task_id": "task-a",
                        "state": "SUCCESS",
                        "status": "completed",
                        "message": "ok",
                        "result": {"service_id": "svc-a"},
                    },
                    "task-b": {
                        "task_id": "task-b",
                        "state": "FAILURE",
                        "status": "failed",
                        "message": "fail",
                        "error": "kaboom",
                    },
                },
            )
        )

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            results = client.tasks.batch_status(["task-a", "task-b"])

        # Request body was a JSON array of the task ids.
        sent = json.loads(route.calls.last.request.content.decode())
        assert sent == ["task-a", "task-b"]

        assert results["task-a"]["status"] == "completed"
        assert results["task-b"]["error"] == "kaboom"

    @respx.mock
    def test_wait_returns_terminal_status(self) -> None:
        # First call: still running. Second call: completed.
        responses = iter(
            [
                httpx.Response(
                    200,
                    json={
                        "task_id": "task-x",
                        "state": "STARTED",
                        "status": "running",
                        "message": "running",
                    },
                ),
                httpx.Response(
                    200,
                    json={
                        "task_id": "task-x",
                        "state": "SUCCESS",
                        "status": "completed",
                        "message": "ok",
                        "result": {"service_id": "svc-x"},
                    },
                ),
            ]
        )
        respx.get(f"{BASE_URL}/tasks/task-x").mock(side_effect=lambda req: next(responses))

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            status = client.tasks.wait("task-x", poll_interval=0.001, timeout=5.0)

        assert status["status"] == "completed"
        assert status["result"]["service_id"] == "svc-x"

    @respx.mock
    def test_wait_batch_drains_until_all_terminal(self) -> None:
        # First poll: one done, one running. Second poll: both done.
        responses = iter(
            [
                httpx.Response(
                    200,
                    json={
                        "task-a": {
                            "task_id": "task-a",
                            "state": "SUCCESS",
                            "status": "completed",
                            "result": {"service_id": "svc-a"},
                        },
                        "task-b": {
                            "task_id": "task-b",
                            "state": "STARTED",
                            "status": "running",
                        },
                    },
                ),
                # Second poll only asks about task-b (the still-running one).
                httpx.Response(
                    200,
                    json={
                        "task-b": {
                            "task_id": "task-b",
                            "state": "SUCCESS",
                            "status": "completed",
                            "result": {"service_id": "svc-b"},
                        },
                    },
                ),
            ]
        )
        respx.post(f"{BASE_URL}/tasks/batch-status").mock(side_effect=lambda req: next(responses))

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            results = client.tasks.wait_batch(
                ["task-a", "task-b"],
                timeout=5.0,
                poll_interval=0.001,
            )

        assert results["task-a"]["result"]["service_id"] == "svc-a"
        assert results["task-b"]["result"]["service_id"] == "svc-b"

    @respx.mock
    def test_wait_batch_timeout_marks_leftovers(self) -> None:
        # Always returns task-c as still running.
        respx.post(f"{BASE_URL}/tasks/batch-status").mock(
            return_value=httpx.Response(
                200,
                json={
                    "task-c": {
                        "task_id": "task-c",
                        "state": "STARTED",
                        "status": "running",
                    },
                },
            )
        )

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            results = client.tasks.wait_batch(
                ["task-c"],
                timeout=0.0,  # fires the timeout on the first check
                poll_interval=0.001,
            )

        # Timeout path still returns the task, preserving the last-seen
        # status so callers can report "stuck: running".
        assert "task-c" in results
        assert results["task-c"]["status"] == "running"


# ---------------------------------------------------------------------------
# upload_directory — polling integrated into the upload flow
# ---------------------------------------------------------------------------
def _write_catalog(tmp_path: Path) -> Path:
    """Minimal catalog: one provider, one offering, one listing."""
    provider_dir = tmp_path / "acme"
    service_dir = provider_dir / "services" / "svc1"
    service_dir.mkdir(parents=True)

    (provider_dir / "provider.json").write_text(
        json.dumps(
            {
                "schema": "provider_v1",
                "name": "acme",
                "display_name": "Acme",
                "contact_email": "ops@acme.example",
                "homepage": "https://acme.example",
                "status": "ready",
            }
        )
    )
    (service_dir / "offering.json").write_text(
        json.dumps(
            {
                "schema": "offering_v1",
                "name": "svc1",
                "display_name": "Service 1",
                "service_type": "llm",
                "status": "ready",
                "upstream_access_config": {
                    "default": {
                        "access_method": "http",
                        "base_url": "https://api.acme.example",
                    },
                },
            }
        )
    )
    (service_dir / "listing.json").write_text(
        json.dumps(
            {
                "schema": "listing_v1",
                "name": "svc1",
                "display_name": "Service 1",
                "status": "ready",
                "list_price": {"type": "constant", "price": "1.00"},
            }
        )
    )
    return tmp_path


class TestUploadDirectoryPolling:
    @respx.mock
    def test_upload_success_reports_real_completion(self, tmp_path: Path) -> None:
        catalog = _write_catalog(tmp_path)

        respx.post(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(
                202,
                json={
                    "task_id": "task-svc1",
                    "status": "queued",
                    "message": "queued",
                    "dryrun_result": None,
                },
            )
        )
        respx.post(f"{BASE_URL}/tasks/batch-status").mock(
            return_value=httpx.Response(
                200,
                json={
                    "task-svc1": {
                        "task_id": "task-svc1",
                        "state": "SUCCESS",
                        "status": "completed",
                        "message": "ok",
                        "result": {"service_id": "svc-111", "name": "svc1"},
                    },
                },
            )
        )

        progress_events: list[tuple[str, str, str, str]] = []

        def _on_progress(kind: str, status: str, name: str, detail: str = "") -> None:
            progress_events.append((kind, status, name, detail))

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            result = upload_directory(
                client,
                catalog,
                on_progress=_on_progress,
                task_poll_interval=0.001,
                task_wait_timeout=5.0,
            )

        assert result.services.total == 1
        assert result.services.success == 1
        assert result.services.failed == 0

        # Progress flow: queued first, then ok.
        kinds = [(kind, status) for kind, status, *_ in progress_events if kind == "service"]
        assert ("service", "queued") in kinds
        assert ("service", "ok") in kinds

        # Override file written with the service_id from task result.
        override = catalog / "acme" / "services" / "svc1" / "listing.override.json"
        assert override.exists()
        assert "svc-111" in override.read_text()

    @respx.mock
    def test_upload_task_failure_marks_service_failed(self, tmp_path: Path) -> None:
        catalog = _write_catalog(tmp_path)

        respx.post(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(
                202,
                json={
                    "task_id": "task-svc1",
                    "status": "queued",
                    "message": "queued",
                    "dryrun_result": None,
                },
            )
        )
        respx.post(f"{BASE_URL}/tasks/batch-status").mock(
            return_value=httpx.Response(
                200,
                json={
                    "task-svc1": {
                        "task_id": "task-svc1",
                        "state": "FAILURE",
                        "status": "failed",
                        "message": "Task failed",
                        "error": "ValueError: Secret 'FIREWORKS_API_KEY' not found",
                    },
                },
            )
        )

        progress_events: list[tuple[str, str, str, str]] = []

        def _on_progress(kind: str, status: str, name: str, detail: str = "") -> None:
            progress_events.append((kind, status, name, detail))

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            result = upload_directory(
                client,
                catalog,
                on_progress=_on_progress,
                task_poll_interval=0.001,
                task_wait_timeout=5.0,
            )

        assert result.services.total == 1
        assert result.services.success == 0
        assert result.services.failed == 1
        assert len(result.services.errors) == 1
        assert "FIREWORKS_API_KEY" in result.services.errors[0]["error"]

        # Both events should have fired (queued then error) — no "ok".
        service_events = [(status, detail) for kind, status, _n, detail in progress_events if kind == "service"]
        statuses = {status for status, _ in service_events}
        assert "queued" in statuses
        assert "error" in statuses
        assert "ok" not in statuses

        # Override file must NOT have been written on failure.
        override = catalog / "acme" / "services" / "svc1" / "listing.override.json"
        assert not override.exists()

    @respx.mock
    def test_upload_polling_api_error_fails_all(self, tmp_path: Path) -> None:
        catalog = _write_catalog(tmp_path)

        respx.post(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(
                202,
                json={
                    "task_id": "task-svc1",
                    "status": "queued",
                    "message": "queued",
                    "dryrun_result": None,
                },
            )
        )
        respx.post(f"{BASE_URL}/tasks/batch-status").mock(
            return_value=httpx.Response(503, json={"detail": "task backend down"})
        )

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            result = upload_directory(
                client,
                catalog,
                task_poll_interval=0.001,
                task_wait_timeout=5.0,
            )

        assert result.services.failed == 1
        assert "task polling hit a backend error (503)" in result.services.errors[0]["error"]

    @respx.mock
    def test_upload_polling_404_emits_composite_deployment_hint(self, tmp_path: Path) -> None:
        """When polling returns 404, surface an actionable hint about the
        composite-vs-dedicated deployment split instead of a raw 'Not
        Found'."""
        catalog = _write_catalog(tmp_path)

        respx.post(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(
                202,
                json={
                    "task_id": "task-svc1",
                    "status": "queued",
                    "message": "queued",
                    "dryrun_result": None,
                },
            )
        )
        respx.post(f"{BASE_URL}/tasks/batch-status").mock(
            return_value=httpx.Response(404, json={"detail": "Not Found"})
        )

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            result = upload_directory(
                client,
                catalog,
                task_poll_interval=0.001,
                task_wait_timeout=5.0,
            )

        assert result.services.failed == 1
        error_msg = result.services.errors[0]["error"]
        assert "task polling endpoint is missing" in error_msg
        assert "composite layout" in error_msg
        assert "DEPLOYMENT_TYPE=seller" in error_msg

    @respx.mock
    def test_dryrun_skips_polling(self, tmp_path: Path) -> None:
        catalog = _write_catalog(tmp_path)

        # Dryrun uploads still route through POST /services but the
        # backend runs them synchronously and returns 200, not 202.
        respx.post(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(
                200,
                json={
                    "task_id": None,
                    "status": "dryrun",
                    "message": "dryrun",
                    "dryrun_result": {
                        "provider": {"status": "create"},
                        "offering": {"status": "create"},
                        "listing": {"status": "create"},
                        "service": {"status": "create"},
                    },
                },
            )
        )
        batch_route = respx.post(f"{BASE_URL}/tasks/batch-status").mock(
            return_value=httpx.Response(500, json={"detail": "should not be called"})
        )

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            result = upload_directory(client, catalog, dryrun=True)

        assert result.services.success == 1
        assert result.services.failed == 0
        assert batch_route.called is False
