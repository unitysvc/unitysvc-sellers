"""Tests for ModelDataLookup.get_canonical_metadata.

The other ``ModelDataLookup`` methods are thin fuzzy-matchers tested
implicitly through the per-provider scrapers; this file specifically
covers ``get_canonical_metadata`` because it owns the source-priority
logic and provenance contract that consuming code depends on.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from unitysvc_sellers.model_data import ModelDataFetcher, ModelDataLookup


def _make_fetcher(
    *,
    openrouter: dict[str, Any] | None = None,
    litellm: dict[str, Any] | None = None,
    hf_details: dict[str, Any] | None = None,
) -> MagicMock:
    """Build a MagicMock that quacks like ModelDataFetcher.

    Each source is independently controllable so each test only stubs
    the ones it cares about.  Defaults to empty / None so the helper's
    fallback chain is exercised honestly.
    """
    f = MagicMock(spec=ModelDataFetcher)
    f.fetch_openrouter_models_data.return_value = openrouter or {}
    f.fetch_litellm_model_data.return_value = litellm or {}
    f.fetch_huggingface_model_details.return_value = hf_details
    return f


class TestContextLengthSourcePriority:
    """OpenRouter beats LiteLLM beats HuggingFace config."""

    def test_openrouter_wins_when_present(self) -> None:
        fetcher = _make_fetcher(
            openrouter={"anthropic/claude-3-opus": {"context_length": 200_000}},
            litellm={"claude-3-opus": {"max_input_tokens": 100_000}},
            hf_details={"config": {"max_position_embeddings": 50_000}},
        )
        result = ModelDataLookup.get_canonical_metadata("anthropic/claude-3-opus", fetcher=fetcher)
        assert result["context_length"] == 200_000
        assert result["sources"]["context_length"] == "openrouter"

    def test_litellm_used_when_openrouter_missing(self) -> None:
        fetcher = _make_fetcher(
            openrouter={},
            litellm={"gpt-4": {"max_input_tokens": 128_000}},
        )
        result = ModelDataLookup.get_canonical_metadata("gpt-4", fetcher=fetcher)
        assert result["context_length"] == 128_000
        assert result["sources"]["context_length"] == "litellm"

    def test_huggingface_config_used_as_last_resort(self) -> None:
        fetcher = _make_fetcher(
            openrouter={},
            litellm={},
            hf_details={"config": {"max_position_embeddings": 32_768}},
        )
        result = ModelDataLookup.get_canonical_metadata("meta-llama/Llama-3.1-8B", fetcher=fetcher)
        assert result["context_length"] == 32_768
        assert result["sources"]["context_length"] == "huggingface_config"

    def test_null_context_length_when_no_source_has_it(self) -> None:
        fetcher = _make_fetcher()
        result = ModelDataLookup.get_canonical_metadata("unknown-model", fetcher=fetcher)
        assert result["context_length"] is None
        assert "context_length" not in result["sources"]


class TestContextLengthRobustness:
    """Source data may be malformed; fall through to the next source."""

    def test_openrouter_zero_falls_through_to_litellm(self) -> None:
        fetcher = _make_fetcher(
            openrouter={"some-model": {"context_length": 0}},  # invalid
            litellm={"some-model": {"max_input_tokens": 8192}},
        )
        result = ModelDataLookup.get_canonical_metadata("some-model", fetcher=fetcher)
        assert result["context_length"] == 8192
        assert result["sources"]["context_length"] == "litellm"

    def test_openrouter_string_falls_through_to_litellm(self) -> None:
        fetcher = _make_fetcher(
            openrouter={"m": {"context_length": "200K"}},  # string, not int
            litellm={"m": {"max_input_tokens": 200_000}},
        )
        result = ModelDataLookup.get_canonical_metadata("m", fetcher=fetcher)
        assert result["context_length"] == 200_000

    def test_litellm_missing_field_falls_through_to_hf(self) -> None:
        fetcher = _make_fetcher(
            litellm={"m": {"input_cost_per_token": 0.01}},  # no max_input_tokens
            hf_details={"config": {"max_position_embeddings": 4096}},
        )
        result = ModelDataLookup.get_canonical_metadata("m", fetcher=fetcher)
        assert result["context_length"] == 4096
        assert result["sources"]["context_length"] == "huggingface_config"


class TestParameterCount:
    """parameter_count comes only from HuggingFace safetensors metadata."""

    def test_total_from_safetensors_total(self) -> None:
        fetcher = _make_fetcher(
            hf_details={
                "safetensors": {"parameters": {"total": 7_000_000_000}},
            },
        )
        result = ModelDataLookup.get_canonical_metadata("llama-3-7b", fetcher=fetcher)
        assert result["parameter_count"] == 7_000_000_000
        assert result["sources"]["parameter_count"] == "huggingface_safetensors"

    def test_total_inferred_from_per_dtype_counts(self) -> None:
        """Same parameter set in two precisions — the larger count is the
        true parameter count, not the sum (which would double-count)."""
        fetcher = _make_fetcher(
            hf_details={
                "safetensors": {"parameters": {"BF16": 8_000_000_000, "F32": 8_000_000_000}},
            },
        )
        result = ModelDataLookup.get_canonical_metadata("llama-3-8b", fetcher=fetcher)
        assert result["parameter_count"] == 8_000_000_000

    def test_null_parameter_count_for_closed_model(self) -> None:
        """Closed models (GPT-*, Claude-*, etc.) have no HF safetensors
        publish — must return None gracefully."""
        fetcher = _make_fetcher(
            openrouter={"gpt-4": {"context_length": 128_000}},
            hf_details=None,
        )
        result = ModelDataLookup.get_canonical_metadata("gpt-4", fetcher=fetcher)
        assert result["parameter_count"] is None
        assert "parameter_count" not in result["sources"]
        # context_length still comes through — fields are independent.
        assert result["context_length"] == 128_000

    def test_safetensors_present_but_empty(self) -> None:
        fetcher = _make_fetcher(
            hf_details={"safetensors": {"parameters": {}}},
        )
        result = ModelDataLookup.get_canonical_metadata("m", fetcher=fetcher)
        assert result["parameter_count"] is None


class TestSourcesProvenance:
    """The sources dict must accurately reflect which upstream supplied
    each value, so reviewers can triage 'this looks wrong' reports."""

    def test_sources_only_includes_resolved_fields(self) -> None:
        # context_length resolved, parameter_count not.
        fetcher = _make_fetcher(
            openrouter={"m": {"context_length": 100_000}},
        )
        result = ModelDataLookup.get_canonical_metadata("m", fetcher=fetcher)
        assert result["sources"] == {"context_length": "openrouter"}

    def test_sources_empty_when_nothing_resolves(self) -> None:
        fetcher = _make_fetcher()
        result = ModelDataLookup.get_canonical_metadata("nope", fetcher=fetcher)
        assert result["sources"] == {}

    def test_both_fields_resolved_from_different_sources(self) -> None:
        fetcher = _make_fetcher(
            openrouter={"m": {"context_length": 200_000}},
            hf_details={"safetensors": {"parameters": {"total": 70_000_000_000}}},
        )
        result = ModelDataLookup.get_canonical_metadata("m", fetcher=fetcher)
        assert result == {
            "context_length": 200_000,
            "parameter_count": 70_000_000_000,
            "sources": {
                "context_length": "openrouter",
                "parameter_count": "huggingface_safetensors",
            },
        }


class TestReturnShape:
    """The return shape is a public contract that consuming scrapers
    depend on; lock it down."""

    def test_keys_always_present(self) -> None:
        result = ModelDataLookup.get_canonical_metadata("anything", fetcher=_make_fetcher())
        assert set(result.keys()) == {"context_length", "parameter_count", "sources"}
        assert isinstance(result["sources"], dict)


@pytest.mark.parametrize("model_id", ["", "  ", "a"])
def test_short_model_id_does_not_crash(model_id: str) -> None:
    """Edge case: empty / whitespace / single-char model IDs reach the
    fuzzy-matchers; ensure they degrade gracefully."""
    fetcher = _make_fetcher()
    result = ModelDataLookup.get_canonical_metadata(model_id, fetcher=fetcher)
    assert result["context_length"] is None
    assert result["parameter_count"] is None
