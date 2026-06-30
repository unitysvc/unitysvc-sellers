"""Tests for unitysvc_sellers.example helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from unitysvc_core.models.base import DocumentCategoryEnum

from unitysvc_sellers.example import (
    MissingSecretEnvVar,
    build_upstream_template_context,
    discover_code_examples,
    document_applies_to_channel,
    execute_code_example,
    expand_template_strings,
    extract_code_examples_from_listing,
    resolve_secret_ref,
)

EXAMPLE_DATA = Path(__file__).parent / "example_data"


def test_build_upstream_template_context_renames_base_url() -> None:
    """``base_url`` is exposed as ``service_base_url`` to match unitysvc-data."""
    ctx = build_upstream_template_context({"base_url": "https://api.example.com"})
    assert ctx == {"service_base_url": "https://api.example.com"}


def test_build_upstream_template_context_drops_api_key() -> None:
    """``api_key`` is never inlined into rendered output.

    Templates read ``UNITYSVC_API_KEY`` from the environment instead, so the
    key must not leak into the Jinja2 namespace.
    """
    ctx = build_upstream_template_context({"base_url": "https://api.example.com", "api_key": "sk-secret"})
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
    ``"https://.../{{ enrollment.code }}"``) ended up emitting the
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


def test_discover_code_examples_resolves_provider_from_sibling_file() -> None:
    """Provider comes from the sibling provider_v1 file (flat ``specs/`` layout),
    not the directory name — regression for the ``unknown`` provider column when
    there is no ``services/`` path component."""
    results = discover_code_examples(EXAMPLE_DATA)
    providers = {prov_name for _example, prov_name in results}
    assert providers == {"provider1", "provider2"}
    assert "unknown" not in providers


def test_discover_code_examples_exposes_channel_name() -> None:
    """Each discovered entry carries the upstream-*channel* name/data (#1297
    terminology) — guards against regressing to the old ``upstream_interface_*``
    keys that mislabelled the run-tests / list-tests output."""
    results = discover_code_examples(EXAMPLE_DATA)
    assert results, "expected at least one discovered example"
    for example, _prov in results:
        assert "upstream_channel_name" in example
        assert "upstream_channel" in example
        assert "upstream_interface_name" not in example


def test_document_applies_to_channel() -> None:
    """Absent/empty ``meta.channels`` applies to every channel; a non-empty
    list restricts the document to exactly those channels (unitysvc#1321)."""
    assert document_applies_to_channel(None, "apprise") is True
    assert document_applies_to_channel([], "apprise") is True
    assert document_applies_to_channel(["apprise"], "apprise") is True
    assert document_applies_to_channel(["apprise", "native"], "native") is True
    assert document_applies_to_channel(["apprise"], "native") is False


def test_extract_code_examples_captures_meta_channels() -> None:
    """``meta.channels`` is carried onto the discovered example so the
    document × channel cross-product can filter per channel (unitysvc#1321)."""
    listing_data = {
        "name": "demo/svc",
        "documents": {
            "Scoped": {
                "category": DocumentCategoryEnum.connectivity_test,
                "file_path": "scoped.sh.j2",
                "mime_type": "shell",
                "meta": {"channels": ["apprise"]},
            },
            "Shared": {
                "category": DocumentCategoryEnum.connectivity_test,
                "file_path": "shared.sh.j2",
                "mime_type": "shell",
                "meta": {},
            },
        },
    }
    by_title = {e["title"]: e for e in extract_code_examples_from_listing(listing_data, Path("/tmp/listing.json"))}
    assert by_title["Scoped"]["channels"] == ["apprise"]
    assert by_title["Shared"]["channels"] is None


# --- resolve_secret_ref: in-place (embedded) substitution -------------------


def test_resolve_secret_ref_literal_passthrough() -> None:
    """A string with no reference is returned unchanged."""
    assert resolve_secret_ref("https://api.example.com/v1", "base_url") == "https://api.example.com/v1"


def test_resolve_secret_ref_non_secret_namespace_untouched() -> None:
    """``${VAR}`` env-style refs (no secrets namespace) are left alone."""
    assert resolve_secret_ref("${API_GATEWAY_BASE_URL}/svc", "base_url") == "${API_GATEWAY_BASE_URL}/svc"


def test_resolve_secret_ref_whole_value_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """A whole-value reference resolves from the environment (back-compat)."""
    monkeypatch.setenv("MY_TOKEN", "abc123")
    assert resolve_secret_ref("${ secrets.MY_TOKEN }", "api_key") == "abc123"


def test_resolve_secret_ref_default_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    """``?? default`` is used when the env var is unset."""
    monkeypatch.delenv("MY_TOKEN", raising=False)
    assert resolve_secret_ref("${ secrets.MY_TOKEN ?? fallback }", "api_key") == "fallback"


def test_resolve_secret_ref_required_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """A required reference with no default and no env var raises."""
    monkeypatch.delenv("MY_TOKEN", raising=False)
    with pytest.raises(MissingSecretEnvVar):
        resolve_secret_ref("${ secrets.MY_TOKEN }", "api_key")


def test_resolve_secret_ref_embedded_prefix_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """The regression: a ref embedded as a URL *prefix* resolves, keeping the path.

    This is the stress-service base_url shape — previously the whole-value
    regex failed to match, leaving the raw ``${ ... }`` to reach bash as a
    ``bad substitution``.
    """
    monkeypatch.setenv("UNITYSVC_STRESS_BASE_URL", "https://stress.unitysvc.dev")
    out = resolve_secret_ref(
        "${ customer_secrets.UNITYSVC_STRESS_BASE_URL ?? http://stress-server:8800 }/stress/anthropic",
        "base_url",
    )
    assert out == "https://stress.unitysvc.dev/stress/anthropic"


def test_resolve_secret_ref_embedded_prefix_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Embedded ref falls back to its default and keeps the trailing path."""
    monkeypatch.delenv("UNITYSVC_STRESS_BASE_URL", raising=False)
    out = resolve_secret_ref(
        "${ customer_secrets.UNITYSVC_STRESS_BASE_URL ?? http://stress-server:8800 }/stress/anthropic",
        "base_url",
    )
    assert out == "http://stress-server:8800/stress/anthropic"


def test_resolve_secret_ref_empty_env_preserved(monkeypatch: pytest.MonkeyPatch) -> None:
    """``??`` coalesces on null, not empty — an empty env value is kept."""
    monkeypatch.setenv("MY_TOKEN", "")
    assert resolve_secret_ref("${ secrets.MY_TOKEN ?? fallback }", "api_key") == ""
