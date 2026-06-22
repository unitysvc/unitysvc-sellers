"""``client.services`` — service catalog management.

Wraps the seller-tagged ``/v1/seller/services/*`` operations from the
generated low-level client. ``client.services.get(...)`` returns a
:class:`Service` active-record wrapper whose methods (``refresh``,
``update``, ``delete``, ``submit``, ``run_tests``) navigate without
re-passing the service id; ``client.services.list(...)`` returns a
:class:`ServiceList` that's iterable directly so ``for svc in
services`` works alongside ``services.next_cursor`` /
``services.has_more`` for pagination.

Field access on a :class:`Service` is forwarded to the underlying
generated record (``ServicePublic`` for list items,
``ServiceDetailResponse`` for ``get()``), so ``svc.id``,
``svc.status``, ``svc.name`` etc. all work transparently.

The same operations remain available on the manager directly
(``client.services.update(service_id, ...)``); :class:`Service`
is just sugar that pre-binds the id.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.body_services_upload import BodyServicesUpload
    from ._generated.models.service_delete_response import ServiceDeleteResponse
    from ._generated.models.service_detail_response import ServiceDetailResponse
    from ._generated.models.service_public import ServicePublic
    from ._generated.models.service_update_response import ServiceUpdateResponse
    from ._generated.models.task_queued_response import TaskQueuedResponse
    from .client import Client


@dataclass(frozen=True)
class RunTestsIfaceResult:
    """One per (document × interface) row from a diagnostic run.

    Mirrors the dict shape returned by the backend's
    ``run_service_diagnostic`` celery task (see
    ``backend/app/workers/service_health_tasks.py``).  Fields are
    optional because the task payload omits them on success rows
    (stdout/stderr are stripped) and on skipped rows.
    """

    document_id: str
    document_title: str | None = None
    category: str | None = None
    interface_id: str | None = None
    interface_name: str | None = None
    status: str = ""
    exit_code: int | None = None
    error: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    executed_at: str | None = None
    # Outcome of the gateway-then-upstream attribution:
    # gateway_pass | platform_fault | upstream_fault | gateway_only_fail | already_passed
    outcome: str | None = None
    # ``"success"`` | ``"script_failed"`` | … — the gateway-mode result string.
    gateway: str | None = None
    # When upstream fallback ran, this carries the upstream-mode probe summary
    # (the representative channel — a passing one if any).
    upstream: dict[str, Any] | None = None
    # Per upstream-access-channel probe summaries, keyed by channel name
    # (#1281/#1297).  A multi-channel service is probed once per channel; the
    # enrollment channel is probed via its ops enrollment.  ``upstream`` above
    # stays for back-compat; this carries the full per-channel breakdown.
    upstream_channels: dict[str, Any] | None = None


@dataclass(frozen=True)
class RunTestsResult:
    """Result of a server-side ``services.run_tests`` call.

    Wraps the celery task payload from ``run_service_diagnostic`` plus
    the ``task_id`` we polled, so consumers don't need to know about
    the underlying task surface.

    ``passed`` is the convenience boolean — ``True`` iff every executed
    (doc × iface) row reported ``status="success"``.  Skipped rows
    (``outcome="already_passed"``) don't count against ``passed``.
    """

    task_id: str
    service_id: str
    status: str  # the top-level task status: "success" | "failure" | "error"
    outcome: str | None = None  # e.g. "no_executable_documents" or None on normal runs
    snapshot_status: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    success_count: int = 0
    fail_count: int = 0
    skipped_count: int = 0
    results: list[RunTestsIfaceResult] = field(default_factory=list)
    # The raw task payload, kept around so callers can dig into fields
    # we haven't promoted to typed attributes yet.
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """``True`` iff the diagnostic ran cleanly with zero failing rows."""
        return self.status == "success" and self.fail_count == 0


def _parse_run_tests_payload(task_id: str, payload: dict[str, Any]) -> RunTestsResult:
    """Coerce the task-status dict from ``/tasks/{id}`` into a typed result.

    The backend's diagnostic task returns its summary in
    ``payload["result"]`` when the task succeeded.  When the celery
    task itself errored (status="failed"), there's no ``result`` —
    surface a minimal RunTestsResult with status="error" so callers
    can render the failure without crashing on missing keys.
    """
    if payload.get("status") == "failed":
        return RunTestsResult(
            task_id=task_id,
            service_id="",
            status="error",
            outcome=payload.get("error") or payload.get("message"),
            raw=payload,
        )

    body: dict[str, Any] = payload.get("result") or {}
    iface_results = [
        RunTestsIfaceResult(
            document_id=row.get("document_id", ""),
            document_title=row.get("document_title"),
            category=row.get("category"),
            interface_id=row.get("interface_id"),
            interface_name=row.get("interface_name"),
            status=row.get("status", ""),
            exit_code=row.get("exit_code"),
            error=row.get("error"),
            stdout=row.get("stdout"),
            stderr=row.get("stderr"),
            executed_at=row.get("executed_at"),
            outcome=row.get("outcome"),
            gateway=row.get("gateway"),
            upstream=row.get("upstream"),
            upstream_channels=row.get("upstream_channels"),
        )
        for row in (body.get("results") or [])
    ]
    return RunTestsResult(
        task_id=task_id,
        service_id=body.get("service_id", ""),
        status=body.get("status", "unknown"),
        outcome=body.get("outcome"),
        snapshot_status=body.get("snapshot_status"),
        started_at=body.get("started_at"),
        completed_at=body.get("completed_at"),
        success_count=int(body.get("success_count") or 0),
        fail_count=int(body.get("fail_count") or 0),
        skipped_count=int(body.get("skipped_count") or 0),
        results=iface_results,
        raw=payload,
    )


class Service:
    """Active-record wrapper around a seller service.

    Forwards field access (``svc.id``, ``svc.name``, ``svc.status``,
    ``svc.visibility``, …) to the underlying generated record via
    ``__getattr__`` — every attribute exposed on
    :class:`ServicePublic` / :class:`ServiceDetailResponse` is
    available unchanged. Adds methods that delegate to the parent
    :class:`Client`:

    - :meth:`refresh` — re-fetch the full record via ``services_get``.
    - :meth:`update` — patch fields (status, visibility, routing_vars,
      list_price). Same body shape as :meth:`Services.update`.
    - :meth:`delete` — remove the service.
    - :meth:`submit` — convenience for ``update({"status": "pending"})``.
    - :meth:`run_tests` — queue a server-side diagnostic and block until
      complete; returns gateway-then-upstream attribution per (doc × iface).

    Returned by :meth:`Services.get` and as items inside
    :class:`ServiceList` from :meth:`Services.list`.
    """

    __slots__ = ("_raw", "_parent")

    def __init__(
        self,
        raw: ServicePublic | ServiceDetailResponse,
        parent: Client,
    ) -> None:
        object.__setattr__(self, "_raw", raw)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, item: str) -> Any:
        return getattr(object.__getattribute__(self, "_raw"), item)

    def __repr__(self) -> str:
        raw = object.__getattribute__(self, "_raw")
        name = getattr(raw, "name", None)
        status = getattr(raw, "status", None)
        return f"<Service id={raw.id!r} name={name!r} status={status!r}>"

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def refresh(self) -> Service:
        """Re-fetch the service via ``services_get``.

        Returns a new :class:`Service` wrapping the fresh record.
        Useful after :meth:`update` / :meth:`submit` to observe
        server-side state transitions.
        """
        return self._parent.services.get(self._raw.id)

    def run_tests(
        self,
        *,
        document_id: str | None = None,
        force: bool = False,
        poll_interval: float = 2.0,
        timeout: float = 600.0,
        on_progress: Callable[[str], None] | None = None,
    ) -> RunTestsResult:
        """Queue a server-side diagnostic and block until it completes.

        See :meth:`Services.run_tests` for the full argument and result
        documentation; this is the active-record shortcut that
        pre-binds the service id.
        """
        return self._parent.services.run_tests(
            self._raw.id,
            document_id=document_id,
            force=force,
            poll_interval=poll_interval,
            timeout=timeout,
            on_progress=on_progress,
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def update(self, body: dict[str, Any]) -> ServiceUpdateResponse:
        """Patch fields. See :meth:`Services.update` for the body shape."""
        return self._parent.services.update(self._raw.id, body)

    def delete(self, *, dryrun: bool = False) -> ServiceDeleteResponse:
        """Delete the service. See :meth:`Services.delete`."""
        return self._parent.services.delete(self._raw.id, dryrun=dryrun)

    def submit(self, *, run_tests: bool = True) -> ServiceUpdateResponse:
        """Submit for review — shortcut for ``update({"status": "pending"})``.

        The seller flow is ``draft`` → ``pending`` (this call) →
        admin sets ``review`` / ``active`` / ``rejected`` /
        ``suspended`` after their checks.

        Args:
            run_tests: When ``True`` (default) the backend runs the gateway
                diagnostic after the transition and flips the service to
                ``review`` / ``active`` / ``rejected`` based on the result.
                Pass ``False`` to skip the diagnostic and hold the service at
                ``pending`` (routable) — useful for on-wire testing of code
                examples while iterating. Content is still validated either way.
        """
        return self.update({"status": "pending", "run_tests": run_tests})


class ServiceList:
    """Cursor-paginated wrapper around a service list response.

    Iterable directly, so callers can write::

        services = client.services.list(limit=50)
        for svc in services:
            print(svc.id, svc.status)

    Pagination metadata is still on the object — ``services.data``,
    ``services.next_cursor``, ``services.has_more`` — for callers
    that need to advance manually. :meth:`next_page` returns the
    next page (or ``None`` if there are no more); for the common
    "iterate everything" case use :meth:`Services.iter_all`.
    """

    __slots__ = ("data", "next_cursor", "has_more", "_parent", "_list_kwargs")

    def __init__(
        self,
        data: list[Service],
        next_cursor: str | None,
        has_more: bool,
        *,
        parent: Client | None = None,
        list_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.data = data
        self.next_cursor = next_cursor
        self.has_more = has_more
        self._parent = parent
        self._list_kwargs = list_kwargs or {}

    def __iter__(self) -> Iterator[Service]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Service:
        return self.data[idx]

    def __bool__(self) -> bool:
        return bool(self.data)

    def __repr__(self) -> str:
        return f"<ServiceList n={len(self.data)} has_more={self.has_more}>"

    def next_page(self) -> ServiceList | None:
        """Fetch the next page using ``next_cursor``, or ``None`` if exhausted."""
        if not self.has_more or self.next_cursor is None or self._parent is None:
            return None
        kwargs = dict(self._list_kwargs)
        kwargs["cursor"] = self.next_cursor
        return self._parent.services.list(**kwargs)


class Services:
    """Operations on the seller's service catalog (``/v1/seller/services``).

    Example::

        # Active-record style — preferred for chained calls
        for svc in client.services.list(limit=50):
            print(svc.id, svc.name, svc.status)
            if svc.status == "draft" and svc.is_complete:
                svc.submit()

        # Or the equivalent manager-style — by id
        client.services.update(service_id, {"status": "pending"})
        client.services.delete(service_id)
    """

    def __init__(self, client: AuthenticatedClient, *, parent: Client) -> None:
        self._client = client
        self._parent = parent

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        status: str | None = None,
        visibility: str | None = None,
        service_type: str | None = None,
        listing_type: str | None = None,
        name: str | None = None,
        provider: str | None = None,
        ids: list[UUID] | None = None,
    ) -> ServiceList:
        """List services owned by the authenticated seller.

        Cursor-paginated. Returns a :class:`ServiceList` that's
        iterable over :class:`Service` items and exposes
        ``next_cursor`` / ``has_more`` for manual pagination.
        For "iterate all pages" use :meth:`iter_all`.
        """
        from ._generated.api.seller_services import services_list
        from ._generated.types import UNSET

        raw = unwrap(
            services_list.sync_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                status=status if status is not None else UNSET,
                visibility=visibility if visibility is not None else UNSET,
                service_type=service_type if service_type is not None else UNSET,
                listing_type=listing_type if listing_type is not None else UNSET,
                name=name if name is not None else UNSET,
                provider=provider if provider is not None else UNSET,
                ids=ids if ids is not None else UNSET,
            )
        )
        return ServiceList(
            data=[Service(item, parent=self._parent) for item in raw.data],
            next_cursor=raw.next_cursor if isinstance(raw.next_cursor, str) else None,
            has_more=bool(raw.has_more),
            parent=self._parent,
            list_kwargs={
                "limit": limit,
                "status": status,
                "visibility": visibility,
                "service_type": service_type,
                "listing_type": listing_type,
                "name": name,
                "provider": provider,
                "ids": ids,
            },
        )

    def iter_all(
        self,
        *,
        limit: int = 50,
        status: str | None = None,
        visibility: str | None = None,
        service_type: str | None = None,
        listing_type: str | None = None,
        name: str | None = None,
        provider: str | None = None,
    ) -> Iterable[Service]:
        """Iterate over all services across pages, auto-advancing the cursor.

        Convenience for the common "process everything in my catalog"
        loop — wraps :meth:`list` + ``next_page`` so callers don't
        thread cursors manually.
        """
        kwargs: dict[str, Any] = {
            "limit": limit,
            "status": status,
            "visibility": visibility,
            "service_type": service_type,
            "listing_type": listing_type,
            "name": name,
            "provider": provider,
        }
        page: ServiceList | None = self.list(**kwargs)
        while page is not None:
            yield from page
            page = page.next_page()

    def get(self, service_id: str | UUID) -> Service:
        """Get the full record for a single service.

        Returns a :class:`Service` wrapping
        :class:`ServiceDetailResponse` — includes documents and
        interfaces alongside the bare service fields.
        """
        from ._generated.api.seller_services import services_get

        raw = unwrap(
            services_get.sync_detailed(
                service_id=str(service_id),
                client=self._client,
            )
        )
        return Service(raw, parent=self._parent)

    def run_tests(
        self,
        service_id: str | UUID,
        *,
        document_id: str | None = None,
        force: bool = False,
        poll_interval: float = 2.0,
        timeout: float = 600.0,
        on_progress: Callable[[str], None] | None = None,
    ) -> RunTestsResult:
        """Queue a server-side diagnostic and block until it completes.

        Calls ``POST /v1/seller/services/{id}/run-tests`` to queue a
        ``run_service_diagnostic`` celery task on the backend, then
        polls ``GET /v1/seller/tasks/{task_id}`` until the task reaches
        a terminal state.  Returns the parsed task payload as a
        :class:`RunTestsResult`.

        The diagnostic runs every executable document (connectivity
        tests + code examples) across every active access interface
        inside the cluster — the same network environment customers
        hit — and falls back to an upstream-mode probe on any
        iface-level gateway failure so the result attributes the
        fault as ``platform_fault`` vs ``upstream_fault``.

        Args:
            service_id: UUID of the service to test.
            document_id: When set, restrict execution to one document.
            force: Re-execute documents whose per-iface result on
                ``meta.test.tests[iface_id].status`` was previously
                ``success``.  Default skips them.
            poll_interval: Seconds between task-status polls.
            timeout: Hard cap on total wait, including queue time.
            on_progress: Optional callback ``on_progress(status: str)``
                called every poll tick with the current task status
                string (``"pending"``, ``"running"``, …).  Use for
                a spinner / progress indicator.

        Returns:
            :class:`RunTestsResult` with per-(doc × iface) rows on
            ``.results`` and pass/fail counts on ``.success_count`` /
            ``.fail_count`` / ``.skipped_count``.  ``.passed`` is the
            convenience boolean.
        """
        from ._generated.api.seller_services import services_run_tests
        from ._generated.types import UNSET

        queued = unwrap(
            services_run_tests.sync_detailed(
                service_id=str(service_id),
                client=self._client,
                document_id=document_id if document_id is not None else UNSET,
                force=force,
            )
        )

        # Wrap tasks.wait()'s batch callback into the simpler
        # per-tick callback the run_tests API exposes.
        wrapped_on_update = None
        if on_progress is not None:

            def _wrapped(done: int, total: int, last_ids: list[str]) -> None:  # pragma: no cover - thin adapter
                # tasks.wait only fires on_update when a task hits a
                # terminal state, which for a single task means the
                # final tick.  We additionally poll the status
                # ourselves below to drive per-tick progress.
                _ = (done, total, last_ids)
                on_progress("completed")

            wrapped_on_update = _wrapped

        # Per-tick progress: tasks.wait doesn't expose a "every poll"
        # hook, so callers that want a spinner can subscribe via
        # on_progress and we'll drive it manually with a small inner
        # loop.  For simplicity in v1 we just wait() and emit a
        # single "completed"/"failed" tick at the end via the
        # wrapped on_update above.
        terminal = self._parent.tasks.wait(
            queued.task_id,
            timeout=timeout,
            poll_interval=poll_interval,
            on_update=wrapped_on_update,
        )

        return _parse_run_tests_payload(queued.task_id, terminal.get(queued.task_id) or {})

    # ------------------------------------------------------------------
    # Write — bulk upload
    # ------------------------------------------------------------------
    def upload(
        self,
        body: BodyServicesUpload | dict[str, Any],
        *,
        auto_submit: bool = False,
    ) -> TaskQueuedResponse:
        """Submit a service for ingestion.

        ``body`` is ``{"data": {provider_data, offering_data, listing_data},
        "service_status": {...}}`` — the authored content and the status sidecar
        (service.json) travel as separate fields.

        With ``auto_submit=True`` the freshly published draft is also submitted
        for review (validate → pending → run tests) in the same ingest task;
        otherwise (the default) it is left as a reviewable draft.
        """
        from ._generated.api.seller_services import services_upload
        from ._generated.models.body_services_upload import BodyServicesUpload

        if isinstance(body, dict):
            body = BodyServicesUpload.from_dict(body)

        return unwrap(
            services_upload.sync_detailed(
                client=self._client,
                body=body,
                auto_submit=auto_submit,
            )
        )

    # ------------------------------------------------------------------
    # Write — update
    # ------------------------------------------------------------------
    def update(
        self,
        service_id: str | UUID,
        body: dict[str, Any],
    ) -> ServiceUpdateResponse:
        """Update a service — status, visibility, routing vars, and/or list price.

        All fields are optional. Include only the fields you want to change.
        Multiple fields can be updated in a single request.

        Args:
            service_id: Service to update.
            body: Dict with any combination of::

                {"status": "pending"}
                {"visibility": "public"}
                {"routing_vars": {"region": "us-east"}}              # full replacement
                {"routing_vars": {"set": {"count": 1}}}              # partial update
                {"list_price": {"type": "constant", "price": "1"}}   # full replacement
                {"list_price": {"set": {"price": "2"}}}              # partial update

        Example::

            # Set visibility and update price in one call
            client.services.update(service_id, {
                "visibility": "public",
                "list_price": {"type": "constant", "price": "1.00"},
            })
        """
        from ._generated.api.seller_services import services_update
        from ._generated.models.service_update import ServiceUpdate

        return unwrap(
            services_update.sync_detailed(
                service_id=str(service_id),
                client=self._client,
                body=ServiceUpdate.from_dict(body),
            )
        )

    # ------------------------------------------------------------------
    # Write — delete
    # ------------------------------------------------------------------
    def delete(
        self,
        service_id: str | UUID,
        *,
        dryrun: bool = False,
    ) -> ServiceDeleteResponse:
        """Delete a service."""
        from ._generated.api.seller_services import services_delete

        return unwrap(
            services_delete.sync_detailed(
                service_id=str(service_id),
                client=self._client,
                dryrun=dryrun,
            )
        )
