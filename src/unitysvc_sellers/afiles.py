"""Async mirror of :mod:`unitysvc_sellers.files`."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import httpx

from ._http import unwrap
from .exceptions import APIError
from .files import _STORAGE_TIMEOUT

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.account_file_upload_ticket import AccountFileUploadTicket
    from ._generated.models.seller_file_download_response import (
        SellerFileDownloadResponse,
    )
    from ._generated.models.seller_files_list_response import SellerFilesListResponse


async def _post_to_ticket(ticket: AccountFileUploadTicket, src: Path, filename: str) -> None:
    """POST ``src`` to a presigned-POST ticket (async).

    See :func:`unitysvc_sellers.files._post_to_ticket` — same contract;
    bare httpx client so the storage host never sees the API key.
    """
    fields = ticket.fields.additional_properties
    with src.open("rb") as fh:
        async with httpx.AsyncClient(timeout=_STORAGE_TIMEOUT) as storage:
            resp = await storage.post(
                ticket.url,
                data=dict(fields),
                files={"file": (filename, fh)},
            )
    if resp.status_code // 100 != 2:
        raise APIError(
            f"storage rejected upload (HTTP {resp.status_code}): {resp.text[:200]}",
            status_code=resp.status_code,
        )


class AsyncFiles:
    """Async operations on the seller's account files.

    Mirrors :class:`unitysvc_sellers.files.Files` — see that class for
    the ``list`` / ``download_url`` / ``download`` / ``upload`` surface
    and rationale (unitysvc#1533).
    """

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(
        self,
        path: str = "",
        *,
        max_keys: int = 100,
        continuation_token: str | None = None,
    ) -> SellerFilesListResponse:
        from ._generated.api.seller import seller_list_seller_files
        from ._generated.types import UNSET

        return unwrap(
            await seller_list_seller_files.asyncio_detailed(
                client=self._client,
                path=path,
                max_keys=max_keys,
                continuation_token=(continuation_token if continuation_token is not None else UNSET),
            )
        )

    async def download_url(
        self,
        key: str,
        *,
        expires_in: int = 900,
    ) -> SellerFileDownloadResponse:
        from ._generated.api.seller import seller_download_seller_file

        return unwrap(
            await seller_download_seller_file.asyncio_detailed(
                client=self._client,
                key=key,
                expires_in=expires_in,
            )
        )

    async def download(
        self,
        key: str,
        dest: str | Path | None = None,
    ) -> Path:
        presigned = await self.download_url(key)
        target = Path(dest) if dest is not None else Path(Path(key).name)
        if target.is_dir():
            target = target / Path(key).name

        async with httpx.AsyncClient(timeout=_STORAGE_TIMEOUT) as storage:
            async with storage.stream("GET", presigned.url) as resp:
                if resp.status_code // 100 != 2:
                    raise APIError(
                        f"storage rejected download (HTTP {resp.status_code})",
                        status_code=resp.status_code,
                    )
                with target.open("wb") as fh:
                    async for chunk in resp.aiter_bytes():
                        fh.write(chunk)
        return target

    async def upload(
        self,
        src: str | Path,
        path: str = "",
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> str:
        from ._generated.api.seller import seller_upload_seller_file
        from ._generated.models.seller_file_upload_request import (
            SellerFileUploadRequest,
        )
        from ._generated.types import UNSET

        source = Path(src)
        name = filename or source.name
        size = source.stat().st_size

        ticket: AccountFileUploadTicket = unwrap(
            await seller_upload_seller_file.asyncio_detailed(
                client=self._client,
                body=SellerFileUploadRequest(
                    filename=name,
                    size=size,
                    content_type=content_type if content_type is not None else UNSET,
                    path=path,
                ),
            )
        )
        await _post_to_ticket(ticket, source, name)
        return ticket.key
