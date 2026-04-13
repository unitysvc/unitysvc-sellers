"""Async mirror of :mod:`unitysvc_sellers.resources.tasks`."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from .._http import unwrap
from .tasks import TERMINAL_STATUSES, _coerce_status

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient


class AsyncTasksResource:
    """Async operations on Celery task status (``GET /tasks/?id=…``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def get(self, *task_ids: str) -> dict[str, dict[str, Any]]:
        """Return a mapping of ``task_id → status dict``."""
        from .._generated.api.tasks import tasks_get_task_status

        response = unwrap(
            await tasks_get_task_status.asyncio_detailed(
                id=list(task_ids),
                client=self._client,
            )
        )
        inner = getattr(response, "additional_properties", None)
        if inner is None and hasattr(response, "to_dict"):
            inner = response.to_dict()
        inner = inner or {}
        return {tid: _coerce_status(entry) for tid, entry in inner.items()}

    async def wait(
        self,
        *task_ids: str,
        timeout: float = 600.0,
        poll_interval: float = 2.0,
        on_update: Any = None,
    ) -> dict[str, dict[str, Any]]:
        """Poll until all ``task_ids`` reach a terminal state, or time out."""
        remaining: set[str] = set(task_ids)
        total = len(remaining)
        terminal: dict[str, dict[str, Any]] = {}
        last_seen: dict[str, dict[str, Any]] = {}
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout

        while remaining:
            finished_this_round: list[str] = []
            chunk_ids = list(remaining)
            for start in range(0, len(chunk_ids), 100):
                chunk = chunk_ids[start : start + 100]
                batch = await self.get(*chunk)
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

            if loop.time() > deadline:
                for tid in remaining:
                    terminal[tid] = last_seen.get(
                        tid,
                        {"task_id": tid, "status": "unknown", "message": "timed out"},
                    )
                break

            await asyncio.sleep(poll_interval)

        return terminal
