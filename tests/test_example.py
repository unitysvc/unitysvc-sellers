"""Tests for unitysvc_sellers.example helpers."""

from __future__ import annotations

import json
from pathlib import Path

from unitysvc_sellers.example import build_upstream_template_context, execute_code_example, expand_template_strings


def test_build_upstream_template_context_renames_base_url() -> None:
    """``base_url`` is exposed as ``service_base_url`` to match unitysvc-data."""
    ctx = build_upstream_template_context({"base_url": "https://api.example.com"})
    assert ctx == {"service_base_url": "https://api.example.com"}


def test_build_upstream_template_context_drops_api_key() -> None:
    """``api_key`` is never inlined into rendered output.

    Templates read ``UNITYSVC_API_KEY`` from the environment instead, so the
    key must not leak into the Jinja2 namespace.
    """
    ctx = build_upstream_template_context(
        {"base_url": "https://api.example.com", "api_key": "sk-secret"}
    )
    assert "api_key" not in ctx
    assert ctx == {"service_base_url": "https://api.example.com"}


def test_build_upstream_template_context_passes_other_fields_through() -> None:
    """Non-special fields keep their names — including nested dicts."""
    ctx = build_upstream_template_context(
        {
            "base_url": "https://api.example.com",
            "routing_key": {"model": "gpt-4o"},
            "host": "smtp.example.com",
            "port": 465,
            "region": "us-west-2",
        }
    )
    assert ctx == {
        "service_base_url": "https://api.example.com",
        "routing_key": {"model": "gpt-4o"},
        "host": "smtp.example.com",
        "port": 465,
        "region": "us-west-2",
    }


def test_build_upstream_template_context_empty() -> None:
    """An empty interface yields an empty context (no defaults)."""
    assert build_upstream_template_context({}) == {}


# ---------------------------------------------------------------------------
# expand_template_strings
# ---------------------------------------------------------------------------

def test_expand_template_strings_expands_top_level_strings() -> None:
    result = expand_template_strings(
        {"url": "https://{{ host }}/v1"},
        extra_context={"host": "api.example.com"},
    )
    assert result == {"url": "https://api.example.com/v1"}


def test_expand_template_strings_recurses_into_nested_dicts() -> None:
    """Nested dict values (e.g. routing_key) must be expanded so that
    ``routing_key.model = "{{ params.model }}"`` resolves to the default
    parameter value before being placed into the code-example render context.
    """
    result = expand_template_strings(
        {"routing_key": {"model": "{{ params.model }}", "stream": "true"}},
        extra_context={"params": {"model": "gpt-4o"}},
    )
    assert result == {"routing_key": {"model": "gpt-4o", "stream": "true"}}


def test_expand_template_strings_nested_unexpanded_strings_pass_through() -> None:
    """Nested strings without Jinja2 syntax are left unchanged."""
    result = expand_template_strings(
        {"routing_key": {"model": "gpt-4o"}},
        extra_context={"params": {}},
    )
    assert result == {"routing_key": {"model": "gpt-4o"}}


def test_expand_template_strings_non_string_values_unchanged() -> None:
    result = expand_template_strings({"port": 465, "flag": True})
    assert result == {"port": 465, "flag": True}


def test_execute_code_example_uses_resolved_credentials_for_template_context(
    tmp_path: Path,
) -> None:
    """Render context comes from ``credentials``, not the raw upstream config.

    Regression for a bug where ``execute_code_example`` re-read the unrendered
    ``offering.upstream_access_config`` and passed it to the Jinja2 namespace.
    Listings whose upstream entry contained nested templating
    (``"{{ routing_vars.backend_host }}"``, ``"${ customer_secrets.X }"``,
    ``"https://.../{{ enrollment_vars.code }}"``) ended up emitting the
    *raw* placeholder text into the rendered script and crashing at execution
    time with "bad substitution" / "HTTP  from {{ routing_vars.X }}".

    The caller (``run-tests``) resolves those placeholders into a flat
    ``credentials`` dict before invoking ``execute_code_example``.  This test
    pins that contract: render must consume ``credentials``, so when the raw
    upstream still has unresolved Jinja2 the rendered script reflects the
    resolved value.
    """
    # Provider/offering/listing layout matches the real catalog shape so
    # ``load_related_data`` populates ``offering`` correctly.
    provider_dir = tmp_path / "provider"
    service_dir = provider_dir / "services" / "svc1"
    service_dir.mkdir(parents=True)

    (provider_dir / "provider.json").write_text(
        json.dumps({"schema": "provider_v1", "name": "provider", "status": "ready"})
    )
    (service_dir / "offering.json").write_text(
        json.dumps(
            {
                "schema": "offering_v1",
                "name": "svc1",
                "service_type": "proxy",
                "status": "ready",
                "upstream_access_config": {
                    "default": {
                        "access_method": "http",
                        # Raw, unresolved — the bug used to read this verbatim.
                        "base_url": "{{ routing_vars.backend_host }}",
                    }
                },
            }
        )
    )
    listing_data = {
        "schema": "listing_v1",
        "name": "svc1",
        "status": "ready",
        "service_options": {"routing_vars": {"backend_host": "https://upstream.test"}},
    }
    listing_file = service_dir / "listing.json"
    listing_file.write_text(json.dumps(listing_data))

    # Tiny shell example that just echoes the rendered URL — keeps the test
    # independent of network/curl availability.
    example_path = service_dir / "probe.sh.j2"
    example_path.write_text('#!/bin/bash\necho "URL={{ service_base_url }}"\n')

    code_example = {
        "service_name": "svc1",
        "title": "probe",
        "mime_type": "bash",
        "file_path": str(example_path),
        "listing_data": listing_data,
        "listing_file": listing_file,
        "interface": {},
        "category": "connectivity_test",
    }
    # Resolved credentials — what the run-tests caller would build after
    # expanding ``{{ routing_vars.backend_host }}``.
    credentials = {"base_url": "https://upstream.test", "api_key": ""}

    result = execute_code_example(code_example, credentials)

    rendered = result["rendered_content"]
    assert rendered is not None, result.get("error")
    # The raw ``{{ routing_vars.backend_host }}`` from the offering MUST NOT
    # leak through — the rendered script sees the resolved value.
    assert "{{ routing_vars" not in rendered
    assert "https://upstream.test" in rendered
    # Sanity: the script ran cleanly and printed the resolved URL.
    assert result["exit_code"] == 0, result.get("stderr")
    assert "URL=https://upstream.test" in (result.get("stdout") or "")
