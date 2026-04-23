"""High-level file upload helpers.

:func:`upload_file` uploads a single file to content-addressed S3 storage
and returns the ``object_key``.  For Markdown files it also scans for local
image and link references, uploads those assets first, and rewrites the
references to ``${UNITYSVC_S3_BASE_URL}/{object_key}`` before uploading the
final Markdown.

The ``${UNITYSVC_S3_BASE_URL}`` placeholder is resolved by the platform at
read-time so the stored document stays deployment-agnostic.
"""

from __future__ import annotations

import mimetypes
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient


# Matches Markdown image and link syntax that point at local paths:
#   ![alt](path)  or  [text](path)
# Excludes anything that already starts with a URL scheme or placeholder.
_MD_LOCAL_REF = re.compile(
    r"(!?\[[^\]]*\])\((?!https?://|ftp://|\$\{)([^)]+)\)"
)

_S3_PLACEHOLDER = "${UNITYSVC_S3_BASE_URL}"


def _is_local_path(ref: str) -> bool:
    """Return True if ref looks like a relative local file path."""
    return not ref.startswith(("#", "mailto:", "data:"))


def _upload_one(client: AuthenticatedClient, path: Path) -> str:
    """Upload a single file; return its object_key."""
    from io import BytesIO

    from ._generated.api.seller.seller_upload_file import sync_detailed
    from ._generated.models.body_seller_upload_file import BodySellerUploadFile
    from ._generated.types import File

    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    content = path.read_bytes()
    body = BodySellerUploadFile(
        file=File(payload=BytesIO(content), file_name=path.name, mime_type=mime),
    )
    response = sync_detailed(client=client, body=body)
    if response.parsed is None or not hasattr(response.parsed, "object_key"):
        raise RuntimeError(
            f"Upload failed for {path.name}: HTTP {response.status_code} — {response.content!r}"
        )
    return response.parsed.object_key  # type: ignore[union-attr]


def _process_markdown(client: AuthenticatedClient, md_path: Path) -> bytes:
    """Upload all local assets referenced by a Markdown file and rewrite links.

    Scans for ``![alt](local/path)`` and ``[text](local/path)`` patterns.
    For each local reference that resolves to an existing file:

    1. Upload the asset via ``POST /upload``.
    2. Replace the reference with ``${UNITYSVC_S3_BASE_URL}/{object_key}``.

    Returns the rewritten Markdown content as bytes, ready to upload.
    """
    text = md_path.read_text(encoding="utf-8")
    base = md_path.parent

    def _rewrite(m: re.Match[str]) -> str:
        bracket, ref = m.group(1), m.group(2).strip()
        if not _is_local_path(ref):
            return m.group(0)
        asset = (base / ref).resolve()
        if not asset.exists():
            return m.group(0)
        key = _upload_one(client, asset)
        return f"{bracket}({_S3_PLACEHOLDER}/{key})"

    rewritten = _MD_LOCAL_REF.sub(_rewrite, text)
    return rewritten.encode("utf-8")


def upload_file(
    client: AuthenticatedClient,
    filename: str | Path,
) -> str:
    """Upload a file to content-addressed S3 storage.

    For plain files (scripts, binaries, images, …) the file is uploaded
    as-is and the ``object_key`` is returned.

    For Markdown (``.md``) files the function automatically scans the
    content for local image and link references, uploads each referenced
    asset first, rewrites those references to
    ``${UNITYSVC_S3_BASE_URL}/{object_key}``, and then uploads the
    rewritten Markdown.  This mirrors the attachment-upload pattern used
    by the platform's blog editor, so embedded images are always
    resolvable after upload without any extra steps.

    All files are stored as publicly readable — access control is enforced
    at the document/service level, not the storage object level.

    Args:
        client: Authenticated low-level client (``Client._client``).
        filename: Path to the file to upload.

    Returns:
        The content-addressed ``object_key`` (SHA-256 hash + extension).
        Build the public URL as ``{s3_base_url}/{object_key}``.

    Raises:
        FileNotFoundError: If ``filename`` does not exist.
        RuntimeError: If the backend rejects the upload.
    """
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() == ".md":
        content = _process_markdown(client, path)
        from io import BytesIO

        from ._generated.api.seller.seller_upload_file import sync_detailed
        from ._generated.models.body_seller_upload_file import BodySellerUploadFile
        from ._generated.types import File

        body = BodySellerUploadFile(
            file=File(payload=BytesIO(content), file_name=path.name, mime_type="text/markdown"),
        )
        response = sync_detailed(client=client, body=body)
        if response.parsed is None or not hasattr(response.parsed, "object_key"):
            raise RuntimeError(
                f"Upload failed for {path.name}: HTTP {response.status_code} — {response.content!r}"
            )
        return response.parsed.object_key  # type: ignore[union-attr]

    return _upload_one(client, path)
