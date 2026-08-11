"""Uniform model-metadata contract (``ModelSpec``) for LLM populate scripts.

Every LLM provider's ``scripts/update_params.py`` becomes a thin adapter: it
fetches the provider's ``/models`` list and calls :func:`build_model_spec` per
model. The function resolves a **fixed field set** through tiered acquisition
and returns the ``parameters`` dict that the universal LLM template renders
identically for every provider (unitysvc #1768). A uniform iterator surface is
what makes one template — and, later, one backend system template — possible.

Acquisition tiers, per field (low → high effort, first hit wins):

* **T1** — the provider's own ``/models`` entry (``model_info``): authoritative.
* **T2** — the litellm price/context catalog, **exact-key match only**. The
  fuzzy substring matching in :meth:`ModelDataLookup.lookup_model_details`
  silently attaches a *different* model's numbers, so it is deliberately not
  used here.
* **T3** — a provider-website-sourced ``price_override`` the adapter passes in
  (never fetched here — brittle live scraping stays out of the driver).

Pricing / publish gate: a model that needs a **resale** price
(``allow_managed=True``) but has none from T2/T3 is returned with
``status="pending"`` and null pricing — uploaded but not published, flagged for
investigation, never shipped with a guessed price. A **byok-only** model does
not need an upstream price to publish (the customer pays the provider directly),
so a missing price leaves it ``ready``.
"""

from __future__ import annotations

from typing import Any

from .model_data import ModelDataFetcher

PER_1M = 1_000_000

# Fields on a provider ``/models`` entry that, across providers, carry the
# context window. Checked in order; first positive int wins (T1).
_T1_CONTEXT_FIELDS = (
    "context_length",
    "max_context_length",
    "max_input_tokens",
    "context_window",
)


def _titleize(model_id: str) -> str:
    """A human display name from a bare model id (fallback when /models omits one)."""
    tail = model_id.rsplit("/", 1)[-1]
    return tail.replace("-", " ").replace("_", " ").title()


def _derive_service_type(model_id: str, mode: str | None) -> str:
    """Best-effort service_type from the litellm ``mode`` (T2) then id heuristics."""
    if mode:
        m = mode.lower()
        if m in ("embedding", "embeddings"):
            return "embedding"
        if m == "rerank":
            return "rerank"
        if m in ("chat", "completion", "responses"):
            return "llm"
    low = model_id.lower()
    if any(k in low for k in ("embed", "embedding")):
        return "embedding"
    if "rerank" in low:
        return "rerank"
    if "vision" in low:
        return "vision_language_model"
    return "llm"


def litellm_exact(model_id: str, litellm_data: dict[str, Any], provider_name: str | None = None) -> dict[str, Any] | None:
    """Exact-only litellm lookup (T2): the bare id, or ``<provider>/<id>``.

    No substring fallback — an exact key or nothing. This is the accuracy
    guarantee the fuzzy :meth:`ModelDataLookup.lookup_model_details` cannot make.
    """
    if not litellm_data:
        return None
    entry = litellm_data.get(model_id)
    if isinstance(entry, dict):
        return entry
    if provider_name:
        entry = litellm_data.get(f"{provider_name}/{model_id}")
        if isinstance(entry, dict):
            return entry
    return None


def _t1_context_length(model_info: dict[str, Any]) -> int | None:
    for field in _T1_CONTEXT_FIELDS:
        v = model_info.get(field)
        if isinstance(v, int) and v > 0:
            return v
    return None


def _per_1m(cost_per_token: Any) -> str | None:
    """A per-token cost → a per-1M-token string, trimmed of trailing ``.0``."""
    try:
        v = round(float(cost_per_token) * PER_1M, 4)
    except (TypeError, ValueError):
        return None
    return str(int(v)) if v == int(v) else str(v)


def _price_from_litellm(entry: dict[str, Any] | None) -> dict[str, str] | None:
    """A ``{input, output[, cached_input]}`` per-1M price from a litellm entry (T2)."""
    if not entry:
        return None
    inp = _per_1m(entry.get("input_cost_per_token"))
    out = _per_1m(entry.get("output_cost_per_token"))
    if inp is None or out is None:
        return None
    price = {"input": inp, "output": out}
    cached = _per_1m(entry.get("cache_read_input_token_cost"))
    if cached is not None:
        price["cached_input"] = cached
    return price


def _channel_list_price(price: dict[str, str], provider_display_name: str) -> dict[str, Any]:
    """Channel-keyed list price: byok free, managed resells upstream tokens at cost."""
    unit = "input/output" + ("/cached" if "cached_input" in price else "")
    amounts = "/".join(v for v in (price["input"], price["output"], price.get("cached_input")) if v)
    managed: dict[str, Any] = {
        "type": "one_million_tokens",
        "input": price["input"],
        "output": price["output"],
        "description": f"${amounts} per 1M {unit} tokens",
    }
    if "cached_input" in price:
        managed["cached_input"] = price["cached_input"]
    return {
        "type": "channel",
        "default": "managed",
        "channels": {
            "byok": {
                "type": "constant",
                "price": "0",
                "description": (
                    f"Free — bring your own {provider_display_name} API key; "
                    f"you pay {provider_display_name} directly for tokens"
                ),
            },
            "managed": managed,
        },
    }


def build_model_spec(
    *,
    model_id: str,
    model_info: dict[str, Any],
    provider_name: str,
    provider_display_name: str,
    api_base_url: str,
    env_api_key_name: str,
    fetcher: ModelDataFetcher,
    llm_translator: str = "anthropic_to_openai",
    allow_managed: bool = False,
    base_url_strip: str = "/v1",
    service_type: str | None = None,
    price_override: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Resolve one model to the uniform ``ModelSpec`` params dict.

    Args:
        model_id: the provider's bare model id (routing identity).
        model_info: the provider's ``/models`` entry for this model (T1).
        provider_name / provider_display_name: provider identity.
        api_base_url / env_api_key_name: provider-static upstream config.
        fetcher: a shared :class:`ModelDataFetcher` (its cache means repeated
            calls for one provider don't re-hit the network).
        llm_translator: dialect direction — ``anthropic_to_openai`` for an
            OpenAI-compatible upstream, ``openai_to_anthropic`` for an
            Anthropic-native one.
        allow_managed: emit a managed (resale) channel in addition to byok.
        base_url_strip: path suffix the template strips from ``api_base_url``.
        service_type: override; derived from litellm ``mode`` / id when omitted.
        price_override: a provider-website-sourced price (T3) the adapter supplies.

    Returns:
        The ``parameters`` dict for the universal template. ``status`` is
        ``pending`` iff a resale price is required (``allow_managed``) and none
        could be resolved.
    """
    litellm = fetcher.fetch_litellm_model_data(quiet=True)
    entry = litellm_exact(model_id, litellm, provider_name)

    stype = service_type or _derive_service_type(model_id, entry.get("mode") if entry else None)
    display_name = model_info.get("display_name") or model_info.get("name") or _titleize(model_id)
    description = model_info.get("description") or f"{display_name} model from {provider_display_name}"

    # context_length: T1 (/models) → T2 litellm exact. Null-allowed by schema.
    context_length = _t1_context_length(model_info)
    if context_length is None and entry:
        v = entry.get("max_input_tokens") or entry.get("max_tokens")
        context_length = v if isinstance(v, int) and v > 0 else None

    # parameter_count: T2 exact only, else null. No fuzzy, no T3.
    parameter_count = None
    if entry and isinstance(entry.get("parameter_count"), int):
        parameter_count = entry["parameter_count"]

    # price: T2 litellm exact → T3 provider-website override → none.
    price = _price_from_litellm(entry) or price_override or None

    # Publish gate: only a resale channel needs a price to go live.
    status = "pending" if (allow_managed and price is None) else "ready"

    list_price = _channel_list_price(price, provider_display_name) if (allow_managed and price) else None

    spec: dict[str, Any] = {
        # specs/ path == listing.name == "<provider>/<model_id>" (flat layout).
        "name": f"{provider_name}/{model_id}",
        "offering_name": model_id,
        "display_name": display_name,
        "description": description,
        "service_type": stype,
        "status": status,
        "details": {"context_length": context_length, "parameter_count": parameter_count},
        "list_price": list_price,
        "payout_price": None,
        # Provider-static (template params).
        "provider_name": provider_name,
        "provider_display_name": provider_display_name,
        "api_base_url": api_base_url,
        "env_api_key_name": env_api_key_name,
        "llm_translator": llm_translator,
        "allow_managed": allow_managed,
        "base_url_strip": base_url_strip,
    }
    return spec
