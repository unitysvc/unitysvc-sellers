"""``client.files`` — seller account file browser (unitysvc#1533).

Wraps the seller-tagged ``/v1/seller/files/*`` operations from the
generated low-level client:

* :meth:`list`         — ``GET  /files/list``     (one folder level)
* :meth:`download_url` — ``GET  /files/download`` (short-TTL presigned GET)
* :meth:`download`     — presign + stream the bytes to a local file
* :meth:`upload`       — ``POST /files/upload`` (mint) + presigned POST

Files live in a platform bucket under the seller's flat folder — unlike
the customer SDK there are no personal/shared scopes (sellers have no
team structure). Keys and paths are always relative to the seller root;
the server rejects traversal, so other tenants' folders are unreachable.

This is general-purpose seller file storage, distinct from
:mod:`unitysvc_sellers.storage`, which uploads content-addressed
*documents* (listing images, docs) referenced by services.

Upload and download bytes flow directly between this machine and the
storage endpoint (never through the UnitySVC API), and the storage
requests deliberately carry **no API credentials** — authorization is
embedded in the short-lived presigned URL/policy.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import httpx

from ._http import unwrap
from .exceptions import APIError

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.account_file_upload_ticket import AccountFileUploadTicket
    from ._generated.models.seller_file_download_response import (
        SellerFileDownloadResponse,
    )
    from ._generated.models.seller_files_list_response import SellerFilesListResponse

# Generous read/write budget: uploads and downloads stream large files.
_STORAGE_TIMEOUT = httpx.Timeout(30.0, read=600.0, write=600.0)


def _post_to_ticket(ticket: AccountFileUploadTicket, src: Path, filename: str) -> None:
    """POST ``src`` to a presigned-POST ticket (sync).

    Policy fields come first, the file last — S3 ignores form fields
    after ``file``. Uses a bare httpx client: the storage host must not
    see the UnitySVC API key.
    """
    fields = ticket.fields.additional_properties
    with (
        src.open("rb") as fh,
        httpx.Client(timeout=_STORAGE_TIMEOUT) as storage,
    ):
        resp = storage.post(
            ticket.url,
            data=dict(fields),
            files={"file": (filename, fh)},
        )
    if resp.status_code // 100 != 2:
        raise APIError(
            f"storage rejected upload (HTTP {resp.status_code}): {resp.text[:200]}",
            status_code=resp.status_code,
        )


class Files:
    """Operations on the seller's account files (``/v1/seller/files``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list(
        self,
        path: str = "",
        *,
        max_keys: int = 100,
        continuation_token: str | None = None,
    ) -> SellerFilesListResponse:
        """List one folder level; keys are relative to the seller root."""
        from ._generated.api.seller import seller_list_seller_files
        from ._generated.types import UNSET

        return unwrap(
            seller_list_seller_files.sync_detailed(
                client=self._client,
                path=path,
                max_keys=max_keys,
                continuation_token=(continuation_token if continuation_token is not None else UNSET),
            )
        )

    def download_url(
        self,
        key: str,
        *,
        expires_in: int = 900,
    ) -> SellerFileDownloadResponse:
        """Presign a download URL for one file (no bytes transferred)."""
        from ._generated.api.seller import seller_download_seller_file

        return unwrap(
            seller_download_seller_file.sync_detailed(
                client=self._client,
                key=key,
                expires_in=expires_in,
            )
        )

    def download(
        self,
        key: str,
        dest: str | Path | None = None,
    ) -> Path:
        """Download one file to ``dest`` (default: its basename in cwd).

        Returns the path written. Bytes stream storage → disk directly.
        """
        presigned = self.download_url(key)
        target = Path(dest) if dest is not None else Path(Path(key).name)
        if target.is_dir():
            target = target / Path(key).name

        with httpx.Client(timeout=_STORAGE_TIMEOUT) as storage:
            with storage.stream("GET", presigned.url) as resp:
                if resp.status_code // 100 != 2:
                    raise APIError(
                        f"storage rejected download (HTTP {resp.status_code})",
                        status_code=resp.status_code,
                    )
                with target.open("wb") as fh:
                    for chunk in resp.iter_bytes():
                        fh.write(chunk)
        return target

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def upload(
        self,
        src: str | Path,
        path: str = "",
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> str:
        """Upload a local file into a folder under the seller root.

        Mints a policy-constrained presigned POST from the API, then
        POSTs the bytes directly to storage. Returns the file's key
        relative to the seller root (``{path}/{filename}``). Uploading
        to an existing key overwrites it, like a home directory.
        """
        from ._generated.api.seller import seller_upload_seller_file
        from ._generated.models.seller_file_upload_request import (
            SellerFileUploadRequest,
        )
        from ._generated.types import UNSET

        source = Path(src)
        name = filename or source.name
        size = source.stat().st_size

        ticket: AccountFileUploadTicket = unwrap(
            seller_upload_seller_file.sync_detailed(
                client=self._client,
                body=SellerFileUploadRequest(
                    filename=name,
                    size=size,
                    content_type=content_type if content_type is not None else UNSET,
                    path=path,
                ),
            )
        )
        _post_to_ticket(ticket, source, name)
        return ticket.key
