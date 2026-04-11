"""``client.tasks`` — query Celery task status for async backend operations.

Seller operations that the backend queues (notably
``POST /services`` — the catalog upload) return
``202 Accepted`` with a Celery task id. This resource wraps the two
task-status endpoints so callers can poll until a task reaches a
terminal state.

The task endpoints come from the backend's generic ``tasks`` router.
They are not seller-specific; ``build_seller_app()`` on the backend
side explicitly includes them so the generated SDK has access.

Typical usage::

    task = client.services.upload(catalog_payload)
    status = client.tasks.wait(task.task_id, timeout=300)
    if status["status"] == "completed":
        print("service ingested:", status["result"])
    else:
        raise RuntimeError(status["error"])

Or batched, which is what :meth:`unitysvc_sellers.Client.upload`
uses under the hood when a whole catalog directory is queued::

    task_ids = [resp.task_id for resp in uploaded_responses]
    results = client.tasks.wait_batch(task_ids, timeout=600)
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from .._http import unwrap
from ..exceptions import APIError

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient


# Terminal states — anything else means the task is still in flight.
_TERMINAL_STATUSES = frozenset({"completed", "failed"})


def _coerce_status(payload: Any) -> dict[str, Any]:
    """Turn a generated-model response into a plain status dict.

    ``ResponseTasksGetTaskStatus`` and each entry of
    ``ResponseTasksGetBatchTaskStatus`` are both attrs wrappers around
    a free-form ``additional_properties`` dict. The backend puts the
    real fields (``status``, ``state``, ``message``, ``result``,
    ``error``, ``task_id``) in there. Flatten it.
    """
    if isinstance(payload, dict):
        return payload
    if hasattr(payload, "additional_properties"):
        return dict(payload.additional_properties)
    if hasattr(payload, "to_dict"):
        return payload.to_dict()
    return {"raw": repr(payload)}


class TasksResource:
    """Operations on Celery task status (``/tasks/*``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Single-task status
    # ------------------------------------------------------------------
    def get(self, task_id: str) -> dict[str, Any]:
        """Return the current status dict for a single task.

        The shape comes straight from the backend's
        ``/tasks/{task_id}`` handler::

            {
                "task_id": "...",
                "state": "PENDING" | "STARTED" | "SUCCESS" | "FAILURE" | ...,
                "status": "pending" | "running" | "completed" | "failed" | ...,
                "message": "...",
                "result": {...},  # only when SUCCESS
                "error":  "...",  # only when FAILURE
            }
        """
        from .._generated.api.tasks import tasks_get_task_status

        parsed = unwrap(
            tasks_get_task_status.sync_detailed(
                task_id=task_id,
                client=self._client,
            )
        )
        return _coerce_status(parsed)

    # ------------------------------------------------------------------
    # Batch task status
    # ------------------------------------------------------------------
    def batch_status(self, task_ids: list[str]) -> dict[str, dict[str, Any]]:
        """Return a mapping of ``task_id → status dict``.

        Takes up to 100 task ids per call (backend-enforced). For
        larger uploads, chunk the input and merge the results.
        """
        from .._generated.api.tasks import tasks_get_batch_task_status

        response = unwrap(
            tasks_get_batch_task_status.sync_detailed(
                client=self._client,
                body=list(task_ids),
            )
        )

        # ``ResponseTasksGetBatchTaskStatus`` wraps a dict of
        # ``task_id -> ResponseTasksGetBatchTaskStatusAdditionalProperty``.
        inner = getattr(response, "additional_properties", None)
        if inner is None and hasattr(response, "to_dict"):
            inner = response.to_dict()
        inner = inner or {}
        return {task_id: _coerce_status(entry) for task_id, entry in inner.items()}

    # ------------------------------------------------------------------
    # Convenience: poll to completion
    # ------------------------------------------------------------------
    def wait(
        self,
        task_id: str,
        *,
        timeout: float = 600.0,
        poll_interval: float = 2.0,
    ) -> dict[str, Any]:
        """Block until ``task_id`` reaches a terminal state, or time out.

        Returns the final status dict. Raises :class:`APIError` on
        timeout — callers that want a softer failure should catch it.
        """
        deadline = time.time() + timeout
        while True:
            status = self.get(task_id)
            if status.get("status") in _TERMINAL_STATUSES:
                return status
            if time.time() > deadline:
                raise APIError(
                    f"Task {task_id} did not reach a terminal state within {timeout}s",
                    status_code=0,
                    detail=status,
                )
            time.sleep(poll_interval)

    def wait_batch(
        self,
        task_ids: list[str],
        *,
        timeout: float = 600.0,
        poll_interval: float = 2.0,
        on_update: Any = None,
    ) -> dict[str, dict[str, Any]]:
        """Block until all of ``task_ids`` reach a terminal state, or time out.

        Polls ``batch_status`` every ``poll_interval`` seconds, keeps a
        running map of terminal results, and only polls the still-open
        task ids on each iteration. Returns the merged terminal-state
        dict.

        ``on_update``, if provided, is called as
        ``on_update(terminal_count, total_count, last_finished_ids)``
        after every poll that advanced the terminal-count watermark —
        used by the CLI to render a running progress bar.

        Partial completion on timeout: the returned dict still contains
        the terminal entries that finished in time, plus each
        still-running task id mapped to its most-recent non-terminal
        status dict (so callers can surface a "stuck: pending…" line
        instead of losing the task entirely).
        """
        remaining: set[str] = set(task_ids)
        total = len(remaining)
        terminal: dict[str, dict[str, Any]] = {}
        last_seen: dict[str, dict[str, Any]] = {}
        deadline = time.time() + timeout
        last_finished: list[str] = []

        while remaining:
            # Chunk to respect the backend's 100-id cap on /batch-status.
            finished_this_round: list[str] = []
            chunk_ids = list(remaining)
            for start in range(0, len(chunk_ids), 100):
                chunk = chunk_ids[start : start + 100]
                batch = self.batch_status(chunk)
                for tid, status in batch.items():
                    last_seen[tid] = status
                    if status.get("status") in _TERMINAL_STATUSES:
                        terminal[tid] = status
                        remaining.discard(tid)
                        finished_this_round.append(tid)

            if finished_this_round and on_update is not None:
                last_finished = finished_this_round
                try:
                    on_update(len(terminal), total, last_finished)
                except Exception:  # noqa: BLE001 — progress shouldn't crash polling
                    pass

            if not remaining:
                break

            if time.time() > deadline:
                # Merge still-running tasks into the result so callers
                # can report "timed out after N seconds (pending: X, running: Y)".
                for tid in remaining:
                    terminal[tid] = last_seen.get(
                        tid,
                        {"task_id": tid, "status": "unknown", "message": "timed out"},
                    )
                break

            time.sleep(poll_interval)

        return terminal
