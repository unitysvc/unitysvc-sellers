"""``client.enrollments`` — the enrollments in the seller's services.

Wraps the seller-tagged ``/v1/seller/enrollments/*`` operations
(unitysvc#2759):

* :meth:`list`        — ``GET  /enrollments`` (one cursor page)
* :meth:`iter_all`    — every page, following the cursor
* :meth:`acquire_key` — ``POST /enrollments/{id}/lease``
* :meth:`release_key` — ``POST /enrollments/{id}/lease/return``
* :meth:`lease_key`   — acquire, yield, and always release

A leased key acts *for the enrolled customer*, with the policy the customer
approved when enrolling. Use it with the customer SDK (``unitysvc.Client``)
to read the customer's ``me/profile`` or send a ``notify``. It expires within
an hour (never after the enrollment); release it as soon as the work is done.
The plaintext key is returned once and cannot be fetched again.

Polling enrollments needs no webhook::

    from unitysvc import Client as CustomerClient
    from unitysvc_sellers import Client as SellerClient

    with SellerClient(api_key=seller_key) as seller:
        for enrollment in seller.enrollments.iter_all(service_id=service_id, status="active"):
            with seller.enrollments.lease_key(enrollment.id) as credential:
                with CustomerClient(api_key=credential.apikey, api_base_url=gateway_url) as customer:
                    profile = customer.dispatch("me/profile", method="GET").json()["profile"]
                    ...

A lease controls a credential, not who does the work: repeated polls see the
same enrollments again, so deduplicate work and notifications yourself.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING
from uuid import UUID

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.cursor_page_seller_enrollment_public import (
        CursorPageSellerEnrollmentPublic,
    )
    from ._generated.models.enrollment_key_lease import EnrollmentKeyLease
    from ._generated.models.seller_enrollment_public import SellerEnrollmentPublic
    from .client import Client


class Enrollments:
    """Operations on the enrollments in the seller's services (``/v1/seller/enrollments``)."""

    def __init__(self, client: AuthenticatedClient, *, parent: Client) -> None:
        self._client = client
        self._parent = parent

    def list(
        self,
        *,
        service_id: str | UUID | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> CursorPageSellerEnrollmentPublic:
        """One page of enrollments, newest first.

        Args:
            service_id: Only this service's enrollments.
            status: Only enrollments in this status (``active``, ``paused``,
                ``pending``, ``incomplete``, ``cancelled``).
            cursor: ``next_cursor`` from the previous page.
            limit: Page size (at most 200).

        Each item carries the enrollment's id, service, channel, code,
        status, masked parameters and timestamps, never the customer's
        identity. Use :meth:`iter_all` to walk every page.
        """
        from ._generated.api.seller_enrollments import enrollments_list
        from ._generated.models.service_enrollment_status_enum import (
            check_service_enrollment_status_enum,
        )
        from ._generated.types import UNSET

        return unwrap(
            enrollments_list.sync_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                service_id=UUID(str(service_id)) if service_id is not None else UNSET,
                status=check_service_enrollment_status_enum(status) if status is not None else UNSET,
            )
        )

    def iter_all(
        self,
        *,
        service_id: str | UUID | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> Iterator[SellerEnrollmentPublic]:
        """Iterate over every matching enrollment, following the cursor.

        A scan of ``status="active"`` reports what is active now, not what
        was cancelled since the last scan: reconcile work still running
        against a completed scan, or scan every status.
        """
        cursor: str | None = None
        while True:
            page = self.list(service_id=service_id, status=status, cursor=cursor, limit=limit)
            yield from page.data
            if not page.has_more or not isinstance(page.next_cursor, str):
                return
            cursor = page.next_cursor

    def acquire_key(self, enrollment_id: str | UUID) -> EnrollmentKeyLease:
        """Lease a key that acts for this enrollment's customer.

        Returns ``key_id``, ``apikey_identifier``, the plaintext ``apikey``
        (only this once) and ``expires_at`` (within an hour). Release it with
        :meth:`release_key`, or use :meth:`lease_key`, which does both.

        Raises:
            NotFoundError: The enrollment is not in one of this seller's services.
            ConflictError: The enrollment already has the maximum number of
                live keys; release one or wait for one to expire.
            ValidationError: The enrollment cannot be leased (not active, or
                the customer delegated nothing).
        """
        from ._generated.api.seller_enrollments import enrollments_lease

        return unwrap(
            enrollments_lease.sync_detailed(
                UUID(str(enrollment_id)),
                client=self._client,
            )
        )

    def release_key(self, enrollment_id: str | UUID, apikey: str) -> None:
        """Return a leased key: it expires now.

        Releasing a key twice, or one that was since leased again, does
        nothing, so a late release never ends a newer lease.
        """
        from ._generated.api.seller_enrollments import enrollments_return_lease
        from ._generated.models.enrollment_key_return import EnrollmentKeyReturn

        unwrap(
            enrollments_return_lease.sync_detailed(
                UUID(str(enrollment_id)),
                client=self._client,
                body=EnrollmentKeyReturn(apikey=apikey),
            )
        )

    @contextmanager
    def lease_key(self, enrollment_id: str | UUID) -> Iterator[EnrollmentKeyLease]:
        """Lease a key for the ``with`` block and release it on the way out.

        The key is released whether the block finishes or raises. If the
        release itself fails while the block is raising, the block's error
        is the one you see; the key still expires on its own.
        """
        lease = self.acquire_key(enrollment_id)
        try:
            yield lease
        except BaseException:
            try:
                self.release_key(enrollment_id, lease.apikey)
            except Exception:
                pass
            raise
        self.release_key(enrollment_id, lease.apikey)
