"""Tests for the uniform ModelSpec driver (unitysvc #1768)."""

from __future__ import annotations

from typing import Any

from unitysvc_sellers.model_spec import build_model_spec, litellm_exact


class FakeFetcher:
    """Minimal ModelDataFetcher stand-in: serves a fixed litellm table."""

    def __init__(self, litellm: dict[str, Any] | None = None):
        self._litellm = litellm or {}

    def fetch_litellm_model_data(self, quiet: bool = False) -> dict[str, Any]:
        return self._litellm


LITELLM = {
    "groq/llama-3.3-70b": {
        "mode": "chat",
        "max_input_tokens": 128000,
        "input_cost_per_token": 0.00000059,
        "output_cost_per_token": 0.00000079,
    },
    "gpt-4o": {
        "mode": "chat",
        "max_input_tokens": 128000,
        "input_cost_per_token": 0.0000025,
        "output_cost_per_token": 0.00001,
        "cache_read_input_token_cost": 0.00000125,
    },
}


def _spec(**over: Any) -> dict[str, Any]:
    kwargs: dict[str, Any] = dict(
        model_id="llama-3.3-70b",
        model_info={},
        provider_name="groq",
        provider_display_name="Groq",
        api_base_url="https://api.groq.com/openai/v1",
        env_api_key_name="GROQ_API_KEY",
        fetcher=FakeFetcher(LITELLM),
    )
    kwargs.update(over)
    return build_model_spec(**kwargs)


def test_litellm_exact_is_not_fuzzy():
    # A bare id that only substring-matches a provider-prefixed key must NOT hit.
    assert litellm_exact("llama-3.3-70b", LITELLM) is None
    # Exact bare key hits; exact provider-prefixed key hits.
    assert litellm_exact("gpt-4o", LITELLM) is LITELLM["gpt-4o"]
    assert litellm_exact("llama-3.3-70b", LITELLM, provider_name="groq") is LITELLM["groq/llama-3.3-70b"]


def test_byok_only_is_ready_even_without_price():
    # model_id doesn't exact-match any litellm key → no price. byok-only still ready.
    spec = _spec(model_id="some-unlisted-model")
    assert spec["status"] == "ready"
    assert spec["list_price"] is None
    assert spec["details"] == {"context_length": None, "parameter_count": None}
    assert spec["allow_managed"] is False
    assert spec["llm_translator"] == "anthropic_to_openai"
    assert spec["name"] == "groq/some-unlisted-model"


def test_byok_resolves_context_from_litellm_exact():
    spec = _spec(model_id="gpt-4o", provider_name="openai")
    assert spec["details"]["context_length"] == 128000
    assert spec["service_type"] == "llm"


def test_t1_context_beats_t2():
    spec = _spec(model_id="gpt-4o", provider_name="openai", model_info={"context_length": 200000})
    assert spec["details"]["context_length"] == 200000


def test_managed_with_price_is_channel_keyed():
    spec = _spec(model_id="gpt-4o", provider_name="openai", allow_managed=True)
    assert spec["status"] == "ready"
    lp = spec["list_price"]
    assert lp["type"] == "channel" and lp["default"] == "managed"
    assert lp["channels"]["byok"]["price"] == "0"
    managed = lp["channels"]["managed"]
    assert managed["type"] == "one_million_tokens"
    assert managed["input"] == "2.5" and managed["output"] == "10"
    assert managed["cached_input"] == "1.25"


def test_managed_without_price_is_pending():
    spec = _spec(model_id="unlisted", provider_name="x", allow_managed=True)
    assert spec["status"] == "pending"
    assert spec["list_price"] is None


def test_price_override_used_when_litellm_misses():
    spec = _spec(
        model_id="unlisted",
        provider_name="x",
        allow_managed=True,
        price_override={"input": "1", "output": "3"},
    )
    assert spec["status"] == "ready"
    assert spec["list_price"]["channels"]["managed"]["input"] == "1"


def test_anthropic_native_params_passthrough():
    spec = _spec(model_id="claude", llm_translator="openai_to_anthropic", base_url_strip="")
    assert spec["llm_translator"] == "openai_to_anthropic"
    assert spec["base_url_strip"] == ""
