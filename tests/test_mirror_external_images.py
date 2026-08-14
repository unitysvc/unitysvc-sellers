"""Tests for external-image mirroring: logo/image documents with external
URLs are fetched and re-hosted on platform S3 during upload resolution."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import httpx
import pytest
import respx

from unitysvc_sellers import storage
from unitysvc_sellers.upload import _is_image_document, _resolve_file_references


@pytest.fixture(autouse=True)
def _clear_mirror_cache() -> None:
    storage._MIRROR_CACHE.clear()


class _FakeClient:
    """Stands in for Client (only ``._client`` is touched downstream)."""

    _client = object()


class TestIsImageDocument:
    def test_logo_category_is_image(self) -> None:
        assert _is_image_document({"category": "logo", "mime_type": "url"})

    def test_image_mime_is_image(self) -> None:
        assert _is_image_document({"category": "code_example", "mime_type": "png"})

    def test_page_link_is_not_image(self) -> None:
        assert not _is_image_document({"category": "terms_of_service", "mime_type": "url"})


class TestMirrorExternalImage:
    @respx.mock
    def test_fetches_and_uploads(self) -> None:
        respx.get("https://example.com/brand/logo.svg").mock(
            return_value=httpx.Response(200, content=b"<svg/>", headers={"content-type": "image/svg+xml"})
        )
        with patch.object(storage, "upload_bytes", return_value="abc123.svg") as up:
            key = storage.mirror_external_image(object(), "https://example.com/brand/logo.svg")
        assert key == "abc123.svg"
        args = up.call_args[0]
        assert args[1] == b"<svg/>"
        assert args[2] == "logo.svg"
        assert args[3] == "image/svg+xml"

    @respx.mock
    def test_extension_derived_from_content_type(self) -> None:
        # LinkedIn-style URL with no extension in the path.
        respx.get("https://cdn.example.com/dms/image/companylogo").mock(
            return_value=httpx.Response(200, content=b"jpg", headers={"content-type": "image/jpeg"})
        )
        with patch.object(storage, "upload_bytes", return_value="k.jpg") as up:
            storage.mirror_external_image(object(), "https://cdn.example.com/dms/image/companylogo")
        assert up.call_args[0][2] == "companylogo.jpg"

    @respx.mock
    def test_non_image_content_type_raises(self) -> None:
        respx.get("https://example.com/page").mock(
            return_value=httpx.Response(200, text="<html/>", headers={"content-type": "text/html"})
        )
        with pytest.raises(ValueError, match="not an image content-type"):
            storage.mirror_external_image(object(), "https://example.com/page")

    @respx.mock
    def test_memoized_per_url(self) -> None:
        route = respx.get("https://example.com/logo.png").mock(
            return_value=httpx.Response(200, content=b"p", headers={"content-type": "image/png"})
        )
        with patch.object(storage, "upload_bytes", return_value="k.png"):
            storage.mirror_external_image(object(), "https://example.com/logo.png")
            storage.mirror_external_image(object(), "https://example.com/logo.png")
        assert route.call_count == 1


class TestResolveFileReferencesMirroring:
    def _provider_with_logo(self, url: str) -> dict[str, Any]:
        return {
            "name": "prov",
            "documents": {
                "Company Logo": {
                    "category": "logo",
                    "external_url": url,
                    "mime_type": "svg",
                    "is_public": True,
                }
            },
        }

    def test_logo_external_url_rewritten(self, tmp_path: Any) -> None:
        with patch("unitysvc_sellers.storage.mirror_external_image", return_value="deadbeef.svg"):
            out = _resolve_file_references(
                self._provider_with_logo("https://example.com/logo.svg"),
                tmp_path,
                client=_FakeClient(),
            )
        assert out["documents"]["Company Logo"]["external_url"] == "${UNITYSVC_S3_BASE_URL}/deadbeef.svg"

    def test_fetch_failure_keeps_external_url(self, tmp_path: Any) -> None:
        with patch(
            "unitysvc_sellers.storage.mirror_external_image",
            side_effect=RuntimeError("host down"),
        ):
            out = _resolve_file_references(
                self._provider_with_logo("https://example.com/logo.svg"),
                tmp_path,
                client=_FakeClient(),
            )
        assert out["documents"]["Company Logo"]["external_url"] == "https://example.com/logo.svg"

    def test_no_client_leaves_url_untouched(self, tmp_path: Any) -> None:
        out = _resolve_file_references(self._provider_with_logo("https://example.com/logo.svg"), tmp_path, client=None)
        assert out["documents"]["Company Logo"]["external_url"] == "https://example.com/logo.svg"

    def test_page_links_never_mirrored(self, tmp_path: Any) -> None:
        data = {
            "documents": {
                "Terms of Service": {
                    "category": "terms_of_service",
                    "external_url": "https://example.com/terms",
                    "mime_type": "url",
                }
            }
        }
        with patch("unitysvc_sellers.storage.mirror_external_image") as m:
            out = _resolve_file_references(data, tmp_path, client=_FakeClient())
        m.assert_not_called()
        assert out["documents"]["Terms of Service"]["external_url"] == "https://example.com/terms"

    def test_platform_placeholder_urls_untouched(self, tmp_path: Any) -> None:
        # Already-mirrored references must not be re-fetched.
        data = {
            "documents": {
                "Company Logo": {
                    "category": "logo",
                    "external_url": "${UNITYSVC_S3_BASE_URL}/abc.svg",
                    "mime_type": "svg",
                }
            }
        }
        with patch("unitysvc_sellers.storage.mirror_external_image") as m:
            out = _resolve_file_references(data, tmp_path, client=_FakeClient())
        m.assert_not_called()
        assert out["documents"]["Company Logo"]["external_url"] == "${UNITYSVC_S3_BASE_URL}/abc.svg"
