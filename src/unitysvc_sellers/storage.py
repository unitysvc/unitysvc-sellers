"""High-level file upload helpers.

:func:`upload_file` uploads a single file to content-addressed S3 storage
and returns the ``object_key``.  For Markdown files it also scans for local
image and link references (both Markdown syntax and raw HTML ``<img>`` tags),
uploads those assets first, and rewrites the references to
``${UNITYSVC_S3_BASE_URL}/{object_key}`` before uploading the final Markdown.

The ``${UNITYSVC_S3_BASE_URL}`` placeholder is resolved by the platform at
read-time so the stored document stays deployment-agnostic.
"""

from __future__ import annotations

import mimetypes
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import mistune
from mistune.renderers.markdown import MarkdownRenderer

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient

_S3_PLACEHOLDER = "${UNITYSVC_S3_BASE_URL}"

# Matches <img src="local/path"> or <img src='local/path'>
_HTML_IMG_SRC = re.compile(r'<img\s[^>]*\bsrc=["\']([^"\']+)["\']', re.IGNORECASE)


class _LocalRefExtractor(MarkdownRenderer):
    """mistune renderer that collects local image and link paths."""

    def __init__(self) -> None:
        super().__init__()
        self.paths: list[str] = []

    def image(self, token: dict[str, Any], state: Any) -> str:
        src = token.get("attrs", {}).get("url", "")
        if src and not src.startswith(("http://", "https://", _S3_PLACEHOLDER)):
            self.paths.append(src)
        return super().image(token, state)

    def link(self, token: dict[str, Any], state: Any) -> str:
        href = token.get("attrs", {}).get("url", "")
        if href and not href.startswith(("http://", "https://", "#", "mailto:", _S3_PLACEHOLDER)):
            if "." in Path(href).name or "/" in href:
                self.paths.append(href)
        return super().link(token, state)


def _collect_local_refs(text: str, base: Path) -> dict[str, Path]:
    """Return a mapping of {original_ref: resolved_absolute_path} for all
    local references found in *text* (Markdown syntax + HTML img tags)
    that resolve to existing files."""
    extractor = _LocalRefExtractor()
    mistune.create_markdown(renderer=extractor)(text)

    # HTML <img src="..."> tags (mistune passes these through as raw HTML)
    for m in _HTML_IMG_SRC.finditer(text):
        src = m.group(1)
        if not src.startswith(("http://", "https://", _S3_PLACEHOLDER)):
            extractor.paths.append(src)

    result: dict[str, Path] = {}
    for ref in extractor.paths:
        if ref in result:
            continue
        p = Path(ref)
        resolved = p if p.is_absolute() else (base / ref).resolve()
        if resolved.exists():
            result[ref] = resolved
    return result


def _upload_one(client: AuthenticatedClient, path: Path) -> str:
    """Upload a single file and return its object_key."""
    from io import BytesIO

    from ._generated.api.seller.seller_upload_file import sync_detailed
    from ._generated.models.body_seller_upload_file import BodySellerUploadFile
    from ._generated.types import File

    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = BodySellerUploadFile(
        file=File(payload=BytesIO(path.read_bytes()), file_name=path.name, mime_type=mime),
    )
    response = sync_detailed(client=client, body=body)
    if response.parsed is None or not hasattr(response.parsed, "object_key"):
        raise RuntimeError(
            f"Upload failed for {path.name}: HTTP {response.status_code} — {response.content!r}"
        )
    return response.parsed.object_key  # type: ignore[union-attr]


def _process_markdown(client: AuthenticatedClient, md_path: Path) -> bytes:
    """Upload all local assets referenced in a Markdown file and rewrite links.

    Handles both Markdown syntax (``![alt](path)``, ``[text](path)``) and
    raw HTML ``<img src="path">`` tags.  For each local reference that
    resolves to an existing file:

    1. Upload the asset via ``POST /upload``.
    2. Replace every occurrence of that path with
       ``${UNITYSVC_S3_BASE_URL}/{object_key}``.

    Returns the rewritten Markdown as bytes.
    """
    text = md_path.read_text(encoding="utf-8")
    local_refs = _collect_local_refs(text, md_path.parent)

    # Upload each unique asset and build path → new_url mapping
    ref_to_url: dict[str, str] = {}
    for ref, resolved in local_refs.items():
        key = _upload_one(client, resolved)
        ref_to_url[ref] = f"{_S3_PLACEHOLDER}/{key}"

    # Rewrite Markdown syntax: ![...](path) and [...](path)
    for ref, new_url in ref_to_url.items():
        escaped = re.escape(ref)
        text = re.sub(rf"(!?\[[^\]]*\]\()({escaped})(\))", rf"\g<1>{new_url}\g<3>", text)
        # Rewrite HTML src attributes: src="path" or src='path'
        text = re.sub(rf'(\bsrc=["\'])({escaped})(["\'])', rf"\g<1>{new_url}\g<3>", text)

    return text.encode("utf-8")


def upload_file(
    client: AuthenticatedClient,
    filename: str | Path,
) -> str:
    """Upload a file to content-addressed S3 storage.

    For plain files (scripts, binaries, images, …) the file is uploaded
    as-is and the ``object_key`` is returned.

    For Markdown (``.md``) files the function automatically scans the
    content for local image and link references (both Markdown syntax and
    raw HTML ``<img>`` tags), uploads each referenced asset first, rewrites
    those references to ``${UNITYSVC_S3_BASE_URL}/{object_key}``, and then
    uploads the rewritten Markdown.

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
