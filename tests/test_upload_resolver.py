"""Tests for ``_resolve_file_references`` in ``resources/upload.py``.

The resolver walks a data dict, finds every ``file_path`` reference,
reads the file (rendering Jinja2 templates with the surrounding
catalog as context), and inlines the content as a sibling
``file_content`` field. The backend ingest worker reads from
``file_content`` — it never touches the seller's filesystem — so this
step is required for catalogs with code examples, connectivity
scripts, or any templated document.
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
import respx

from unitysvc_sellers import Client
from unitysvc_sellers.upload import (
    _resolve_file_references,
    upload_directory,
)

BASE_URL = "https://seller.staging.unitysvc.test"


class TestResolveFileReferencesUnit:
    def test_plain_file_inlined_as_file_content(self, tmp_path: Path) -> None:
        (tmp_path / "example.py").write_text("print('hello')\n")
        data = {
            "documents": {
                "Example": {
                    "file_path": "example.py",
                    "mime_type": "python",
                }
            }
        }

        resolved = _resolve_file_references(data, tmp_path)

        doc = resolved["documents"]["Example"]
        assert doc["file_path"] == "example.py"
        assert doc["file_content"] == "print('hello')\n"
        assert doc["mime_type"] == "python"

    def test_jinja_template_renders_and_strips_j2(self, tmp_path: Path) -> None:
        (tmp_path / "code.js.j2").write_text(
            "const key = '{{ provider.name }}';\n"
            "const url = '{{ offering.upstream_access_config.default.base_url }}';\n"
        )
        data = {
            "file_path": "code.js.j2",
            "mime_type": "javascript",
        }

        resolved = _resolve_file_references(
            data,
            tmp_path,
            provider={"name": "acme"},
            offering={"upstream_access_config": {"default": {"base_url": "https://api.acme.example"}}},
        )

        # .j2 suffix stripped from the stored file_path.
        assert resolved["file_path"] == "code.js"
        # Jinja rendered both variables using the provided context.
        assert "const key = 'acme';" in resolved["file_content"]
        assert "const url = 'https://api.acme.example';" in resolved["file_content"]

    def test_relative_parent_path_resolved(self, tmp_path: Path) -> None:
        """Seller catalogs often reference shared templates via ``../../docs/...``.

        Real catalog layout::

            provider/
            ├── docs/
            │   └── shared.js.j2
            └── services/
                └── svc1/
                    └── listing.json   ← references ../../docs/shared.js.j2
        """
        provider_dir = tmp_path / "acme"
        docs_dir = provider_dir / "docs"
        docs_dir.mkdir(parents=True)
        (docs_dir / "shared.js.j2").write_text("// shared template for {{ provider.name }}\n")

        service_dir = provider_dir / "services" / "svc1"
        service_dir.mkdir(parents=True)

        data = {"file_path": "../../docs/shared.js.j2", "mime_type": "javascript"}

        resolved = _resolve_file_references(
            data,
            service_dir,
            provider={"name": "acme"},
        )

        assert resolved["file_path"] == "../../docs/shared.js"
        assert "shared template for acme" in resolved["file_content"]

    def test_missing_file_raises_value_error(self, tmp_path: Path) -> None:
        data = {"file_path": "nope.py", "mime_type": "python"}
        with pytest.raises(ValueError, match="File not found: nope.py"):
            _resolve_file_references(data, tmp_path)

    def test_nested_documents_walked_recursively(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("a\n")
        (tmp_path / "b.py").write_text("b\n")

        data = {
            "documents": {
                "A": {"file_path": "a.py", "mime_type": "python"},
                "B": {"file_path": "b.py", "mime_type": "python"},
            },
            "meta": {"nothing": "here"},
        }

        resolved = _resolve_file_references(data, tmp_path)

        assert resolved["documents"]["A"]["file_content"] == "a\n"
        assert resolved["documents"]["B"]["file_content"] == "b\n"
        assert resolved["meta"] == {"nothing": "here"}

    def test_list_of_docs_walked(self, tmp_path: Path) -> None:
        (tmp_path / "one.py").write_text("1\n")
        (tmp_path / "two.py").write_text("2\n")

        data = {
            "code_examples": [
                {"file_path": "one.py", "mime_type": "python"},
                {"file_path": "two.py", "mime_type": "python"},
            ]
        }

        resolved = _resolve_file_references(data, tmp_path)

        assert resolved["code_examples"][0]["file_content"] == "1\n"
        assert resolved["code_examples"][1]["file_content"] == "2\n"

    def test_fields_without_file_path_key_passthrough(self, tmp_path: Path) -> None:
        data = {
            "name": "svc1",
            "display_name": "Service 1",
            "list_price": {"type": "constant", "price": "1.00"},
        }

        resolved = _resolve_file_references(data, tmp_path)

        assert resolved == data


class TestResolveFileReferencesIntegration:
    """End-to-end: the upload flow embeds file content into the POST body."""

    @respx.mock
    def test_upload_inlines_rendered_template_into_request_body(self, tmp_path: Path) -> None:
        # Build a catalog with a .j2 code example shared across services.
        # Layout mirrors the real unitysvc-services-* repos:
        #
        #     provider/
        #     ├── docs/
        #     │   └── code_example.js.j2
        #     ├── provider.json
        #     └── services/
        #         └── svc1/
        #             ├── listing.json
        #             └── offering.json
        provider_dir = tmp_path / "acme"
        docs_dir = provider_dir / "docs"
        docs_dir.mkdir(parents=True)
        (docs_dir / "code_example.js.j2").write_text("const svc = '{{ offering.name }}';\n")

        service_dir = provider_dir / "services" / "svc1"
        service_dir.mkdir(parents=True)

        (provider_dir / "provider.json").write_text(
            json.dumps(
                {
                    "schema": "provider_v1",
                    "name": "acme",
                    "display_name": "Acme",
                    "contact_email": "ops@acme.example",
                    "homepage": "https://acme.example",
                    "status": "ready",
                }
            )
        )
        (service_dir / "offering.json").write_text(
            json.dumps(
                {
                    "schema": "offering_v1",
                    "name": "svc1",
                    "display_name": "Service 1",
                    "service_type": "llm",
                    "status": "ready",
                    "upstream_access_config": {
                        "default": {
                            "access_method": "http",
                            "base_url": "https://api.acme.example",
                        },
                    },
                }
            )
        )
        (service_dir / "listing.json").write_text(
            json.dumps(
                {
                    "schema": "listing_v1",
                    "name": "svc1",
                    "display_name": "Service 1",
                    "status": "ready",
                    "list_price": {"type": "constant", "price": "1.00"},
                    "documents": {
                        "JS Example": {
                            "file_path": "../../docs/code_example.js.j2",
                            "mime_type": "javascript",
                            "category": "code_example",
                        }
                    },
                }
            )
        )

        upload_route = respx.post(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(
                202,
                json={
                    "task_id": "task-svc1",
                    "status": "queued",
                    "message": "queued",
                },
            )
        )
        respx.get(url__startswith=f"{BASE_URL}/tasks/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "task-svc1": {
                        "task_id": "task-svc1",
                        "state": "SUCCESS",
                        "status": "completed",
                        "message": "ok",
                        "result": {"service_id": "svc-111"},
                    },
                },
            )
        )

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            result = upload_directory(
                client,
                tmp_path,
                task_poll_interval=0.001,
                task_wait_timeout=5.0,
            )

        assert result.services.success == 1
        assert result.services.failed == 0

        # Inspect what we actually sent to the backend.
        sent_body = json.loads(upload_route.calls.last.request.content.decode())
        doc = sent_body["listing_data"]["documents"]["JS Example"]

        # .j2 suffix stripped in the stored file_path.
        assert doc["file_path"] == "../../docs/code_example.js"
        # The rendered template is inlined as file_content, with
        # {{ offering.name }} substituted from the local offering.
        assert "const svc = 'svc1';" in doc["file_content"]
