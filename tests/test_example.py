"""Tests for unitysvc_sellers.example helpers."""

from unitysvc_sellers.example import build_upstream_template_context


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
