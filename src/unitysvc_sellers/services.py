"""``client.services`` — service catalog management.

Wraps the seller-tagged ``/v1/seller/services/*`` operations from the
generated low-level client. ``client.services.get(...)`` returns a
:class:`Service` active-record wrapper whose methods (``refresh``,
``update``, ``delete``, ``test_env``, ``submit``) navigate without
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

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.service_data_input import ServiceDataInput
    from ._generated.models.service_delete_response import ServiceDeleteResponse
    from ._generated.models.service_detail_response import ServiceDetailResponse
    from ._generated.models.service_public import ServicePublic
    from ._generated.models.service_update_response import ServiceUpdateResponse
    from ._generated.models.task_queued_response import TaskQueuedResponse
    from ._generated.models.test_env_response import TestEnvResponse
    from .client import Client


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
    - :meth:`test_env` — rendered environment for code-example scripts.
    - :meth:`submit` — convenience for ``update({"status": "pending"})``.

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

    def test_env(self) -> TestEnvResponse:
        """Rendered environment used to run code-example scripts."""
        return self._parent.services.get_test_env(self._raw.id)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def update(self, body: dict[str, Any]) -> ServiceUpdateResponse:
        """Patch fields. See :meth:`Services.update` for the body shape."""
        return self._parent.services.update(self._raw.id, body)

    def delete(self, *, dryrun: bool = False) -> ServiceDeleteResponse:
        """Delete the service. See :meth:`Services.delete`."""
        return self._parent.services.delete(self._raw.id, dryrun=dryrun)

    def submit(self) -> ServiceUpdateResponse:
        """Submit for review — shortcut for ``update({"status": "pending"})``.

        The seller flow is ``draft`` → ``pending`` (this call) →
        admin sets ``review`` / ``active`` / ``rejected`` /
        ``suspended`` after their checks.
        """
        return self.update({"status": "pending"})


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

    def get_test_env(self, service_id: str | UUID) -> TestEnvResponse:
        """Return the rendered environment used to run code-example scripts for a service."""
        from ._generated.api.seller_services import services_get_test_env

        return unwrap(
            services_get_test_env.sync_detailed(
                service_id=str(service_id),
                client=self._client,
            )
        )

    # ------------------------------------------------------------------
    # Write — bulk upload
    # ------------------------------------------------------------------
    def upload(
        self,
        body: ServiceDataInput | dict[str, Any],
    ) -> TaskQueuedResponse:
        """Submit a provider/offering/listing bundle for ingestion."""
        from ._generated.api.seller_services import services_upload
        from ._generated.models.service_data_input import ServiceDataInput

        if isinstance(body, dict):
            body = ServiceDataInput.from_dict(body)

        return unwrap(
            services_upload.sync_detailed(
                client=self._client,
                body=body,
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
