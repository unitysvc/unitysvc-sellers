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

    def test_code_example_template_kept_raw_for_backend_render(self, tmp_path: Path) -> None:
        """Code-example / connectivity-test templates ship raw to the backend.

        The backend renders them per consumption context (gateway vs. local
        probe, customer-inline vs. env-var portable). The ``.j2`` suffix is
        preserved as the marker that the file is still a template, and any
        ``{{ ... }}`` placeholders are sent verbatim — no client-side
        substitution. See unitysvc/unitysvc#877 / #878.
        """
        (tmp_path / "code.py.j2").write_text("import os\nbase_url = '{{ interface.base_url }}'\n")
        data = {
            "file_path": "code.py.j2",
            "mime_type": "python",
            "category": "code_example",
        }

        resolved = _resolve_file_references(
            data,
            tmp_path,
            interface={"base_url": "https://api.acme.example"},
        )

        # .j2 preserved on the stored file_path.
        assert resolved["file_path"] == "code.py.j2"
        # Raw template content — the placeholder is *not* substituted.
        assert resolved["file_content"] == ("import os\nbase_url = '{{ interface.base_url }}'\n")

    def test_connectivity_test_template_kept_raw_for_backend_render(self, tmp_path: Path) -> None:
        (tmp_path / "probe.sh.j2").write_text("curl '{{ interface.base_url }}/health'\n")
        data = {
            "file_path": "probe.sh.j2",
            "mime_type": "bash",
            "category": "connectivity_test",
        }

        resolved = _resolve_file_references(
            data,
            tmp_path,
            interface={"base_url": "https://api.acme.example"},
        )

        assert resolved["file_path"] == "probe.sh.j2"
        assert resolved["file_content"] == "curl '{{ interface.base_url }}/health'\n"

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

        # Code-example documents ship as raw templates (the backend renders
        # them per consumption context). The ``.j2`` suffix and the
        # ``{{ offering.name }}`` placeholder are preserved verbatim.
        assert doc["file_path"] == "../../docs/code_example.js.j2"
        assert doc["file_content"] == "const svc = '{{ offering.name }}';\n"


def _write_service(provider_dir: Path, svc: str, listing_name: str) -> None:
    """Write a minimal provider + offering + listing bundle for ``svc``."""
    provider_dir.mkdir(parents=True, exist_ok=True)
    if not (provider_dir / "provider.json").exists():
        (provider_dir / "provider.json").write_text(
            json.dumps(
                {
                    "schema": "provider_v1",
                    "name": provider_dir.name,
                    "display_name": "Acme",
                    "contact_email": "ops@acme.example",
                    "homepage": "https://acme.example",
                    "status": "ready",
                }
            )
        )
    service_dir = provider_dir / "services" / svc
    service_dir.mkdir(parents=True)
    (service_dir / "offering.json").write_text(
        json.dumps(
            {
                "schema": "offering_v1",
                "name": svc,
                "display_name": svc,
                "service_type": "llm",
                "status": "ready",
                "upstream_access_config": {
                    "default": {"access_method": "http", "base_url": "https://api.acme.example"},
                },
            }
        )
    )
    (service_dir / "listing.json").write_text(
        json.dumps(
            {
                "schema": "listing_v1",
                "name": listing_name,
                "display_name": svc,
                "status": "ready",
                "list_price": {"type": "constant", "price": "1.00"},
            }
        )
    )


class TestUploadByName:
    """``upload_directory(name=...)`` uploads exactly the one service whose
    service_name (= listing.name) matches (#1138)."""

    @respx.mock
    def test_name_uploads_only_matching_service(self, tmp_path: Path) -> None:
        provider_dir = tmp_path / "acme"
        _write_service(provider_dir, "svc1", "acme/svc1")
        _write_service(provider_dir, "svc2", "acme/svc2")

        upload_route = respx.post(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(202, json={"task_id": "t1", "status": "queued", "message": "q"})
        )
        respx.get(url__startswith=f"{BASE_URL}/tasks/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "t1": {"task_id": "t1", "state": "SUCCESS", "status": "completed", "result": {"service_id": "s1"}}
                },
            )
        )

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            result = upload_directory(
                client, tmp_path, name="acme/svc1", task_poll_interval=0.001, task_wait_timeout=5.0
            )

        assert result.services.total == 1
        assert result.services.success == 1
        # Exactly one POST, for the matching service.
        assert upload_route.call_count == 1
        sent = json.loads(upload_route.calls.last.request.content.decode())
        assert sent["listing_data"]["name"] == "acme/svc1"

    def test_name_no_match_raises(self, tmp_path: Path) -> None:
        provider_dir = tmp_path / "acme"
        _write_service(provider_dir, "svc1", "acme/svc1")
        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            with pytest.raises(ValueError, match="No service with service_name"):
                upload_directory(client, tmp_path, name="acme/does-not-exist")

    @respx.mock
    def test_name_glob_uploads_all_matches(self, tmp_path: Path) -> None:
        # A wildcard pattern uploads every matching service.
        provider_dir = tmp_path / "acme"
        _write_service(provider_dir, "svc1", "acme/svc1")
        _write_service(provider_dir, "svc2", "acme/svc2")
        _write_service(provider_dir, "other", "acme/other")

        upload_route = respx.post(f"{BASE_URL}/services").mock(
            return_value=httpx.Response(202, json={"task_id": "t1", "status": "queued", "message": "q"})
        )
        respx.get(url__startswith=f"{BASE_URL}/tasks/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "t1": {"task_id": "t1", "state": "SUCCESS", "status": "completed", "result": {"service_id": "s1"}}
                },
            )
        )

        with Client(api_key="svcpass_test", base_url=BASE_URL) as client:
            result = upload_directory(
                client, tmp_path, name="acme/svc*", task_poll_interval=0.001, task_wait_timeout=5.0
            )

        # acme/svc1 + acme/svc2 match 'acme/svc*'; acme/other does not.
        assert result.services.total == 2
        uploaded = {json.loads(c.request.content.decode())["listing_data"]["name"] for c in upload_route.calls}
        assert uploaded == {"acme/svc1", "acme/svc2"}
