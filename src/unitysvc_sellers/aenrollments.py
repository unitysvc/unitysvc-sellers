"""Async mirror of :mod:`enrollments`.

Bounded concurrency: each job leases its own key and uses its own customer
client, so releasing one never interrupts another::

    import asyncio
    from unitysvc import AsyncClient as CustomerClient
    from unitysvc_sellers import AsyncClient as SellerClient

    async def handle(seller, enrollment, limit):
        async with limit:
            try:
                async with seller.enrollments.lease_key(enrollment.id) as credential:
                    async with CustomerClient(api_key=credential.apikey, api_base_url=gateway_url) as customer:
                        ...
            except Exception as exc:  # one enrollment's failure does not stop the scan
                log.warning("enrollment %s: %s", enrollment.id, exc)

    async def main():
        limit = asyncio.Semaphore(8)
        async with SellerClient(api_key=seller_key) as seller:
            async with asyncio.TaskGroup() as tg:
                async for enrollment in seller.enrollments.iter_all(service_id=service_id, status="active"):
                    tg.create_task(handle(seller, enrollment, limit))
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
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
    from .aclient import AsyncClient


class AsyncEnrollments:
    """Async operations on the enrollments in the seller's services.

    See :class:`unitysvc_sellers.enrollments.Enrollments`.
    """

    def __init__(self, client: AuthenticatedClient, *, parent: AsyncClient) -> None:
        self._client = client
        self._parent = parent

    async def list(
        self,
        *,
        service_id: str | UUID | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> CursorPageSellerEnrollmentPublic:
        """One page of enrollments, newest first. See :meth:`Enrollments.list`."""
        from ._generated.api.seller_enrollments import enrollments_list
        from ._generated.models.service_enrollment_status_enum import (
            check_service_enrollment_status_enum,
        )
        from ._generated.types import UNSET

        return unwrap(
            await enrollments_list.asyncio_detailed(
                client=self._client,
                cursor=cursor if cursor is not None else UNSET,
                limit=limit,
                service_id=UUID(str(service_id)) if service_id is not None else UNSET,
                status=check_service_enrollment_status_enum(status) if status is not None else UNSET,
            )
        )

    async def iter_all(
        self,
        *,
        service_id: str | UUID | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> AsyncIterator[SellerEnrollmentPublic]:
        """Async-iterate over every matching enrollment, following the cursor."""
        cursor: str | None = None
        while True:
            page = await self.list(service_id=service_id, status=status, cursor=cursor, limit=limit)
            for item in page.data:
                yield item
            if not page.has_more or not isinstance(page.next_cursor, str):
                return
            cursor = page.next_cursor

    async def acquire_key(self, enrollment_id: str | UUID) -> EnrollmentKeyLease:
        """Lease a key that acts for this enrollment's customer. See :meth:`Enrollments.acquire_key`."""
        from ._generated.api.seller_enrollments import enrollments_lease

        return unwrap(
            await enrollments_lease.asyncio_detailed(
                UUID(str(enrollment_id)),
                client=self._client,
            )
        )

    async def release_key(self, enrollment_id: str | UUID, apikey: str) -> None:
        """Return a leased key: it expires now. See :meth:`Enrollments.release_key`."""
        from ._generated.api.seller_enrollments import enrollments_return_lease
        from ._generated.models.enrollment_key_return import EnrollmentKeyReturn

        unwrap(
            await enrollments_return_lease.asyncio_detailed(
                UUID(str(enrollment_id)),
                client=self._client,
                body=EnrollmentKeyReturn(apikey=apikey),
            )
        )

    @asynccontextmanager
    async def lease_key(self, enrollment_id: str | UUID) -> AsyncIterator[EnrollmentKeyLease]:
        """Lease a key for the ``async with`` block and release it on the way out.

        See :meth:`Enrollments.lease_key`.
        """
        lease = await self.acquire_key(enrollment_id)
        try:
            yield lease
        except BaseException:
            try:
                await self.release_key(enrollment_id, lease.apikey)
            except Exception:
                pass
            raise
        await self.release_key(enrollment_id, lease.apikey)
