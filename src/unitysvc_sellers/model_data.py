"""Model data fetching utilities for LLM service providers.

This module provides utilities for fetching model pricing, context window,
and evaluation data from external sources like LiteLLM, Hugging Face,
and OpenRouter. These are useful for any-llm providers that need to
enrich their service data with information from these sources.

Example usage:
    from unitysvc_services.model_data import ModelDataFetcher, ModelDataLookup

    fetcher = ModelDataFetcher()
    litellm_data = fetcher.fetch_litellm_model_data()
    hf_data = fetcher.fetch_huggingface_leaderboard_data()

    lookup = ModelDataLookup()
    details = lookup.lookup_model_details("gpt-4", litellm_data)
"""

import json
from typing import Any

import httpx


class ModelDataFetcher:
    """Handles fetching model data from external sources.

    This class provides methods to fetch model information from various
    public APIs and data sources:
    - LiteLLM: Model pricing and context window data
    - Hugging Face Leaderboard: Model evaluation benchmarks
    - OpenRouter: Model details, pricing, and context lengths
    - Hugging Face Model Hub: Individual model details

    All fetch methods use caching to avoid redundant network requests.
    """

    def __init__(self, user_agent: str = "unitysvc-services/1.0"):
        """Initialize the fetcher with an httpx client.

        Args:
            user_agent: User agent string for HTTP requests
        """
        self._client: httpx.Client | None = None
        self._user_agent = user_agent
        self._litellm_data: dict[str, Any] | None = None
        self._hf_leaderboard_data: dict[str, Any] | None = None
        self._openrouter_data: dict[str, Any] | None = None

    @property
    def client(self) -> httpx.Client:
        """Lazily create and return the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                headers={"User-Agent": self._user_agent},
                timeout=30.0,
            )
        return self._client

    def fetch_litellm_model_data(self, quiet: bool = False) -> dict[str, Any]:
        """Fetch model pricing and context window data from LiteLLM.

        LiteLLM maintains a comprehensive JSON file with pricing and context
        window information for models from various providers.

        Args:
            quiet: If True, suppress progress messages

        Returns:
            Dictionary mapping model identifiers to their pricing/context data.
            Returns empty dict if fetch fails.

        Example:
            >>> fetcher = ModelDataFetcher()
            >>> data = fetcher.fetch_litellm_model_data()
            >>> data.get("gpt-4")
            {'input_cost_per_token': 0.00003, 'output_cost_per_token': 0.00006, ...}
        """
        if self._litellm_data is not None:
            return self._litellm_data

        url = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"

        try:
            if not quiet:
                print("Fetching LiteLLM model data...")
            response = self.client.get(url)
            response.raise_for_status()
            self._litellm_data = response.json()
            return self._litellm_data
        except httpx.HTTPError as e:
            if not quiet:
                print(f"Warning: Failed to fetch LiteLLM model data: {e}")
            self._litellm_data = {}
            return self._litellm_data
        except json.JSONDecodeError as e:
            if not quiet:
                print(f"Warning: Failed to parse LiteLLM model data: {e}")
            self._litellm_data = {}
            return self._litellm_data

    def fetch_huggingface_leaderboard_data(self, quiet: bool = False) -> dict[str, Any]:
        """Fetch model evaluation data from Hugging Face Open LLM Leaderboard.

        The leaderboard contains benchmark scores for various LLMs on tasks
        like ARC, HellaSwag, MMLU, TruthfulQA, WinoGrande, and GSM8K.

        Args:
            quiet: If True, suppress progress messages

        Returns:
            Dictionary mapping model names to their leaderboard data.
            Returns empty dict if fetch fails.

        Example:
            >>> fetcher = ModelDataFetcher()
            >>> data = fetcher.fetch_huggingface_leaderboard_data()
            >>> data.get("meta-llama/Llama-2-70b-chat-hf")
            {'average': 67.87, 'arc': 64.59, 'mmlu': 63.91, ...}
        """
        if self._hf_leaderboard_data is not None:
            return self._hf_leaderboard_data

        url = "https://huggingface.co/api/datasets/open-llm-leaderboard/results"

        try:
            if not quiet:
                print("Fetching Hugging Face leaderboard data...")
            response = self.client.get(url)
            response.raise_for_status()
            data = response.json()

            # Convert to a dict keyed by model name for easier lookup
            leaderboard_dict: dict[str, Any] = {}
            if "rows" in data:
                for row in data["rows"]:
                    if "row" in row and "fullname" in row["row"]:
                        model_name = row["row"]["fullname"]
                        leaderboard_dict[model_name] = row["row"]

            self._hf_leaderboard_data = leaderboard_dict
            return self._hf_leaderboard_data
        except httpx.HTTPError as e:
            if not quiet:
                print(f"Warning: Failed to fetch Hugging Face leaderboard data: {e}")
            self._hf_leaderboard_data = {}
            return self._hf_leaderboard_data
        except (json.JSONDecodeError, KeyError) as e:
            if not quiet:
                print(f"Warning: Failed to parse Hugging Face leaderboard data: {e}")
            self._hf_leaderboard_data = {}
            return self._hf_leaderboard_data

    def fetch_openrouter_models_data(self, quiet: bool = False) -> dict[str, Any]:
        """Fetch model data from OpenRouter API.

        OpenRouter provides information about available models including
        context lengths, pricing, and capabilities.

        Args:
            quiet: If True, suppress progress messages

        Returns:
            Dictionary mapping model IDs to their OpenRouter data.
            Returns empty dict if fetch fails.

        Example:
            >>> fetcher = ModelDataFetcher()
            >>> data = fetcher.fetch_openrouter_models_data()
            >>> data.get("anthropic/claude-3-opus")
            {'id': 'anthropic/claude-3-opus', 'context_length': 200000, ...}
        """
        if self._openrouter_data is not None:
            return self._openrouter_data

        url = "https://openrouter.ai/api/v1/models"

        try:
            if not quiet:
                print("Fetching OpenRouter model data...")
            response = self.client.get(url)
            response.raise_for_status()
            data = response.json()

            # Convert to a dict keyed by model ID for easier lookup
            models_dict: dict[str, Any] = {}
            if "data" in data:
                for model in data["data"]:
                    if "id" in model:
                        models_dict[model["id"]] = model

            self._openrouter_data = models_dict
            return self._openrouter_data
        except httpx.HTTPError as e:
            if not quiet:
                print(f"Warning: Failed to fetch OpenRouter model data: {e}")
            self._openrouter_data = {}
            return self._openrouter_data
        except (json.JSONDecodeError, KeyError) as e:
            if not quiet:
                print(f"Warning: Failed to parse OpenRouter model data: {e}")
            self._openrouter_data = {}
            return self._openrouter_data

    def fetch_huggingface_model_details(self, model_id: str, quiet: bool = False) -> dict[str, Any] | None:
        """Fetch detailed model information from Hugging Face Model Hub API.

        Attempts to fetch model details using various ID format variations
        to handle different naming conventions.

        Args:
            model_id: Model identifier (e.g., "llama-2-70b", "meta-llama/Llama-2-70b")
            quiet: If True, suppress progress messages

        Returns:
            Model details dict if found, None otherwise.

        Example:
            >>> fetcher = ModelDataFetcher()
            >>> details = fetcher.fetch_huggingface_model_details("meta-llama/Llama-2-70b-chat-hf")
            >>> details.get("pipeline_tag")
            'text-generation'
        """
        # Try various model ID formats for HF
        model_variations = [
            model_id,
            model_id.replace(":", "/"),
            f"huggingface/{model_id}",
            f"microsoft/{model_id}",
            f"meta-llama/{model_id}",
            f"google/{model_id}",
            f"mistralai/{model_id}",
            f"anthropic/{model_id}",
        ]

        # Use shorter timeout for individual model lookups
        for model_name in model_variations:
            url = f"https://huggingface.co/api/models/{model_name}"
            try:
                response = self.client.get(url, timeout=15.0)
                if response.status_code == 200:
                    return response.json()
            except httpx.HTTPError:
                continue

        return None

    def clear_cache(self) -> None:
        """Clear all cached data to force fresh fetches."""
        self._litellm_data = None
        self._hf_leaderboard_data = None
        self._openrouter_data = None

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "ModelDataFetcher":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


class ModelDataLookup:
    """Handles looking up model details from fetched data.

    This class provides static methods for fuzzy matching model IDs
    against the data fetched by ModelDataFetcher.
    """

    @staticmethod
    def lookup_model_details(model_id: str, litellm_data: dict[str, Any]) -> dict[str, Any] | None:
        """Look up additional model details from LiteLLM data.

        Performs fuzzy matching to find model data, trying:
        1. Exact match
        2. Match with provider prefix (e.g., "openai/gpt-4")
        3. Partial match (model_id in key or key in model_id)

        Args:
            model_id: Model identifier to look up
            litellm_data: Dictionary from fetch_litellm_model_data()

        Returns:
            Model details dict if found, None otherwise.
        """
        if not litellm_data:
            return None

        # Try exact match first
        if model_id in litellm_data:
            return litellm_data[model_id]

        # Try with provider prefix
        for key in litellm_data:
            if key.endswith(f"/{model_id}") or key.endswith(model_id):
                return litellm_data[key]

        # Try partial match
        for key in litellm_data:
            if model_id in key or key in model_id:
                return litellm_data[key]

        return None

    @staticmethod
    def lookup_hf_leaderboard_details(model_id: str, hf_data: dict[str, Any]) -> dict[str, Any] | None:
        """Look up model evaluation details from Hugging Face leaderboard data.

        Performs fuzzy matching with various transformations including
        case variations and underscore/hyphen substitutions.

        Args:
            model_id: Model identifier to look up
            hf_data: Dictionary from fetch_huggingface_leaderboard_data()

        Returns:
            Leaderboard details dict if found, None otherwise.
        """
        if not hf_data:
            return None

        # Try exact match first
        if model_id in hf_data:
            return hf_data[model_id]

        # Try different variations
        variations = [
            model_id.lower(),
            model_id.upper(),
            model_id.replace("-", "_"),
            model_id.replace("_", "-"),
        ]

        for variation in variations:
            if variation in hf_data:
                return hf_data[variation]

        # Try partial matching
        for key in hf_data:
            key_lower = key.lower()
            model_lower = model_id.lower()

            if model_lower in key_lower or key_lower in model_lower:
                return hf_data[key]

            # Try matching without common prefixes
            key_clean = key_lower.replace("huggingface/", "").replace("microsoft/", "").replace("meta-llama/", "")
            if model_lower in key_clean or key_clean in model_lower:
                return hf_data[key]

        return None

    @staticmethod
    def lookup_openrouter_details(model_id: str, openrouter_data: dict[str, Any]) -> dict[str, Any] | None:
        """Look up model details from OpenRouter data.

        Performs fuzzy matching with case-insensitive comparison
        and partial matching.

        Args:
            model_id: Model identifier to look up
            openrouter_data: Dictionary from fetch_openrouter_models_data()

        Returns:
            OpenRouter details dict if found, None otherwise.
        """
        if not openrouter_data:
            return None

        # Try exact match first
        if model_id in openrouter_data:
            return openrouter_data[model_id]

        # Try different variations and partial matching
        model_lower = model_id.lower()

        for key in openrouter_data:
            key_lower = key.lower()

            if (
                key_lower == model_lower
                or key_lower.endswith(f"/{model_lower}")
                or key_lower.endswith(model_lower)
                or model_lower in key_lower
                or key_lower in model_lower
            ):
                return openrouter_data[key]

        return None

    # =========================================================================
    # HuggingFace pipeline_tag utilities
    # =========================================================================

    # Map HuggingFace pipeline_tag to code example template suffix.
    # pipeline_tag is HuggingFace's standardized task taxonomy:
    # https://huggingface.co/docs/hub/en/models-tasks
    PIPELINE_EXAMPLE_SUFFIX: dict[str, str] = {
        # NLP / text tasks → chat completion template
        "text-generation": "",
        "text2text-generation": "",
        "conversational": "",
        "fill-mask": "",
        "text-classification": "",
        "token-classification": "",
        "question-answering": "",
        "summarization": "",
        "translation": "",
        "zero-shot-classification": "",
        "document-question-answering": "",
        # Embedding / similarity → sentence transformers template
        "feature-extraction": "-sentencetransformers",
        "sentence-similarity": "-sentencetransformers",
        # Image generation → image template
        "text-to-image": "-image",
        "unconditional-image-generation": "-image",
        # Image-to-image → imagetoimage template
        "image-to-image": "-imagetoimage",
        # Vision → chat template (no dedicated vision template yet)
        "image-to-text": "",
        "image-text-to-text": "",
        "visual-question-answering": "",
        "image-classification": "",
        "zero-shot-image-classification": "",
        # Audio → speech templates
        "automatic-speech-recognition": "-prerecordedtranscription",
        "text-to-speech": "-tts",
        "text-to-audio": "-tts",
        # Video → text-to-video template
        "text-to-video": "-ttv",
        "image-to-video": "-ttv",
    }

    @staticmethod
    def get_capabilities_from_hf(model_id: str, fetcher: "ModelDataFetcher") -> tuple[list[str], str]:
        """Get capabilities and example suffix from HuggingFace model metadata.

        Fetches pipeline_tag from the HuggingFace Model Hub API and uses it
        as the model's capability. Also determines the appropriate code
        example template suffix.

        Args:
            model_id: Model identifier (e.g., "meta-llama/Llama-3.1-8B")
            fetcher: ModelDataFetcher instance for API calls

        Returns:
            Tuple of (capabilities list, example_suffix string).
            capabilities uses HF pipeline_tag values directly (e.g., "text-generation",
            "image-to-image", "automatic-speech-recognition").
            example_suffix is the template suffix (e.g., "", "-image", "-tts").
            Falls back to (["llm"], "") if HF metadata is unavailable.
        """
        hf_details = fetcher.fetch_huggingface_model_details(model_id, quiet=True)
        if not hf_details:
            return ["llm"], ""

        pipeline_tag = hf_details.get("pipeline_tag")
        if not pipeline_tag:
            return ["llm"], ""

        capabilities = [pipeline_tag]
        example_suffix = ModelDataLookup.PIPELINE_EXAMPLE_SUFFIX.get(pipeline_tag, "")
        return capabilities, example_suffix

    @staticmethod
    def get_hf_tags(model_id: str, fetcher: "ModelDataFetcher") -> list[str]:
        """Get cleaned tags from HuggingFace model metadata.

        Fetches tags from the HuggingFace Model Hub API, filtering out
        metadata-only tags (base_model, region, license).

        Args:
            model_id: Model identifier
            fetcher: ModelDataFetcher instance for API calls

        Returns:
            List of cleaned tag strings, or empty list if unavailable.
        """
        hf_details = fetcher.fetch_huggingface_model_details(model_id, quiet=True)
        if not hf_details:
            return []

        return [
            t
            for t in hf_details.get("tags", [])
            if not t.startswith("base_model:") and not t.startswith("region:") and not t.startswith("license:")
        ]

    # =========================================================================
    # Canonical LLM metadata (context_length + parameter_count)
    # =========================================================================

    @staticmethod
    def get_canonical_metadata(
        model_id: str,
        *,
        fetcher: "ModelDataFetcher",
    ) -> dict[str, Any]:
        """Return canonical LLM metadata for use in ``offering.details``.

        Resolves ``context_length`` and ``parameter_count`` to the platform's
        canonical (snake_case) field names, hiding the upstream field-name
        chaos behind a single call.  Each field independently falls back
        across multiple sources; either may end up ``None`` if no source
        publishes the value (e.g., closed-source models for which weight
        counts aren't public).

        Source priority for ``context_length`` (most → least authoritative):

        1. **OpenRouter** ``context_length`` — explicitly named, snake_case,
           covers most commercial models.
        2. **LiteLLM** ``max_input_tokens`` — comprehensive coverage but
           sometimes lags long-context model upgrades.
        3. **HuggingFace** ``config.max_position_embeddings`` — works for
           any open-weights model on the Hub.

        Source for ``parameter_count``:

        - **HuggingFace** ``safetensors.parameters`` — the only reliable
          public source.  Sums per-dtype counts when ``total`` is absent.
          Will be ``None`` for closed models (GPT-*, Claude-*, Gemini),
          which is expected and acceptable per the platform's null-allowed
          schema.

        Args:
            model_id: Model identifier (e.g. ``"meta-llama/Llama-3.1-8B"``,
                ``"gpt-4"``, ``"anthropic/claude-3-opus"``).  Fuzzy matching
                inside each ``lookup_*`` method handles provider-prefix
                variations.
            fetcher: ``ModelDataFetcher`` instance.  Reused across calls;
                its internal cache means repeated lookups for the same
                upstream don't re-hit the network.

        Returns:
            ``{"context_length": int | None, "parameter_count": int | None,
            "sources": {"context_length": str, "parameter_count": str}}``.
            ``sources`` only includes entries for fields that were
            successfully resolved — useful for surfacing provenance in
            ``offering.details.metadata_sources`` and for triage of
            ``"this value looks wrong"`` reports.

        Example:
            >>> with ModelDataFetcher() as fetcher:
            ...     meta = ModelDataLookup.get_canonical_metadata(
            ...         "anthropic/claude-3-opus", fetcher=fetcher
            ...     )
            >>> meta
            {'context_length': 200000, 'parameter_count': None,
             'sources': {'context_length': 'openrouter'}}
        """
        result: dict[str, Any] = {
            "context_length": None,
            "parameter_count": None,
            "sources": {},
        }

        # context_length: OpenRouter → LiteLLM → HuggingFace config.json.
        # Each source uses a different field name; normalise to int here so
        # callers don't have to know.
        or_data = fetcher.fetch_openrouter_models_data(quiet=True)
        or_match = ModelDataLookup.lookup_openrouter_details(model_id, or_data)
        if or_match:
            cl = or_match.get("context_length")
            if isinstance(cl, int) and cl > 0:
                result["context_length"] = cl
                result["sources"]["context_length"] = "openrouter"

        if result["context_length"] is None:
            ll_data = fetcher.fetch_litellm_model_data(quiet=True)
            ll_match = ModelDataLookup.lookup_model_details(model_id, ll_data)
            if ll_match:
                cl = ll_match.get("max_input_tokens")
                if isinstance(cl, int) and cl > 0:
                    result["context_length"] = cl
                    result["sources"]["context_length"] = "litellm"

        # HuggingFace details are also the source for parameter_count, so
        # fetch once and reuse.  Returns None on miss / network failure.
        hf_details = fetcher.fetch_huggingface_model_details(model_id, quiet=True)

        if result["context_length"] is None and hf_details:
            cfg = hf_details.get("config") or {}
            mpe = cfg.get("max_position_embeddings")
            if isinstance(mpe, int) and mpe > 0:
                result["context_length"] = mpe
                result["sources"]["context_length"] = "huggingface_config"

        if hf_details:
            # safetensors.parameters is the per-dtype breakdown the Hub
            # publishes on weight-bearing model uploads since mid-2024.
            # Older uploads won't have it; closed-source models never will.
            st = (hf_details.get("safetensors") or {}).get("parameters") or {}
            if isinstance(st, dict) and st:
                # Prefer explicit total; otherwise sum per-dtype counts
                # (BF16 + F32 etc.) — they represent the same parameter
                # set in different precisions, so summing is wrong for the
                # multi-precision case.  Use max() instead, which gives
                # the parameter count regardless of how the weights are
                # stored.  Fall back to sum if max isn't applicable.
                total = st.get("total")
                if not isinstance(total, int):
                    int_values = [v for v in st.values() if isinstance(v, int) and v > 0]
                    total = max(int_values) if int_values else None
                if isinstance(total, int) and total > 0:
                    result["parameter_count"] = total
                    result["sources"]["parameter_count"] = "huggingface_safetensors"

        return result
