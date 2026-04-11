"""Async mirror of :mod:`unitysvc_sellers.resources.tasks`."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from .._http import unwrap
from ..exceptions import APIError
from .tasks import _TERMINAL_STATUSES, _coerce_status

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient


class AsyncTasksResource:
    """Async operations on Celery task status."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def get(self, task_id: str) -> dict[str, Any]:
        from .._generated.api.tasks import tasks_get_task_status

        parsed = unwrap(
            await tasks_get_task_status.asyncio_detailed(
                task_id=task_id,
                client=self._client,
            )
        )
        return _coerce_status(parsed)

    async def batch_status(self, task_ids: list[str]) -> dict[str, dict[str, Any]]:
        from .._generated.api.tasks import tasks_get_batch_task_status

        response = unwrap(
            await tasks_get_batch_task_status.asyncio_detailed(
                client=self._client,
                body=list(task_ids),
            )
        )
        inner = getattr(response, "additional_properties", None)
        if inner is None and hasattr(response, "to_dict"):
            inner = response.to_dict()
        inner = inner or {}
        return {task_id: _coerce_status(entry) for task_id, entry in inner.items()}

    async def wait(
        self,
        task_id: str,
        *,
        timeout: float = 600.0,
        poll_interval: float = 2.0,
    ) -> dict[str, Any]:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while True:
            status = await self.get(task_id)
            if status.get("status") in _TERMINAL_STATUSES:
                return status
            if loop.time() > deadline:
                raise APIError(
                    f"Task {task_id} did not reach a terminal state within {timeout}s",
                    status_code=0,
                    detail=status,
                )
            await asyncio.sleep(poll_interval)

    async def wait_batch(
        self,
        task_ids: list[str],
        *,
        timeout: float = 600.0,
        poll_interval: float = 2.0,
        on_update: Any = None,
    ) -> dict[str, dict[str, Any]]:
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
                batch = await self.batch_status(chunk)
                for tid, status in batch.items():
                    last_seen[tid] = status
                    if status.get("status") in _TERMINAL_STATUSES:
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
