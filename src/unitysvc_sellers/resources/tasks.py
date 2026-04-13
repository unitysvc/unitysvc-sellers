"""``client.tasks`` — query Celery task status.

Wraps ``GET /tasks/?id=…`` — the single endpoint for polling task
status. Accepts one or more task IDs (up to 100 per request) and
returns a mapping of task_id → status dict.

Example::

    # Poll once
    result = client.tasks.get("abc", "def")
    for tid, status in result.items():
        print(tid, status["status"])

    # Poll until done
    result = client.tasks.wait("abc", "def", timeout=300)
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from .._http import unwrap

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient


# Terminal states — anything else means the task is still in flight.
TERMINAL_STATUSES = frozenset({"completed", "failed"})


def _coerce_status(payload: Any) -> dict[str, Any]:
    """Turn a generated-model response into a plain status dict."""
    if isinstance(payload, dict):
        return payload
    if hasattr(payload, "additional_properties"):
        return dict(payload.additional_properties)
    if hasattr(payload, "to_dict"):
        return payload.to_dict()
    return {"raw": repr(payload)}


class TasksResource:
    """Operations on Celery task status (``GET /tasks/?id=…``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def get(self, *task_ids: str) -> dict[str, dict[str, Any]]:
        """Return a mapping of ``task_id → status dict``.

        Accepts one or more task IDs. Uses ``GET /tasks/?id=a&id=b&…``
        (up to 100 IDs per call).
        """
        from .._generated.api.tasks import tasks_get_task_status

        response = unwrap(
            tasks_get_task_status.sync_detailed(
                id=list(task_ids),
                client=self._client,
            )
        )

        inner = getattr(response, "additional_properties", None)
        if inner is None and hasattr(response, "to_dict"):
            inner = response.to_dict()
        inner = inner or {}
        return {tid: _coerce_status(entry) for tid, entry in inner.items()}

    def wait(
        self,
        *task_ids: str,
        timeout: float = 600.0,
        poll_interval: float = 2.0,
        on_update: Any = None,
    ) -> dict[str, dict[str, Any]]:
        """Poll until all ``task_ids`` reach a terminal state, or time out.

        Returns a mapping of ``task_id → final status dict``.

        ``on_update``, if provided, is called as
        ``on_update(terminal_count, total_count, last_finished_ids)``
        after every poll that advances the terminal-count watermark.

        On timeout, the returned dict includes every task — terminal
        ones with their final status, still-running ones with their
        last-seen status.
        """
        remaining: set[str] = set(task_ids)
        total = len(remaining)
        terminal: dict[str, dict[str, Any]] = {}
        last_seen: dict[str, dict[str, Any]] = {}
        deadline = time.time() + timeout

        while remaining:
            finished_this_round: list[str] = []
            chunk_ids = list(remaining)
            for start in range(0, len(chunk_ids), 100):
                chunk = chunk_ids[start : start + 100]
                batch = self.get(*chunk)
                for tid, status in batch.items():
                    last_seen[tid] = status
                    if status.get("status") in TERMINAL_STATUSES:
                        terminal[tid] = status
                        remaining.discard(tid)
                        finished_this_round.append(tid)

            if finished_this_round and on_update is not None:
                try:
                    on_update(len(terminal), total, finished_this_round)
                except Exception:  # noqa: BLE001
                    pass

            if not remaining:
                break

            if time.time() > deadline:
                for tid in remaining:
                    terminal[tid] = last_seen.get(
                        tid,
                        {"task_id": tid, "status": "unknown", "message": "timed out"},
                    )
                break

            time.sleep(poll_interval)

        return terminal
