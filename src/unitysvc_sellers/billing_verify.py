"""Test-time billing verification (unitysvc#1522).

Verify that a connectivity-test request through the gateway was billed
CORRECTLY — without predicting the amount (impossible for token-metered LLM
services, where the response size is upstream-determined). Instead of a static
expected charge, we verify the charge is a correct function of the usage that
ACTUALLY occurred:

  1. a usage event EXISTS for the test request              — catches a skipped
     event (the #1484 non-streaming-translate class);
  2. the priced-dimension metric is present and non-zero    — catches a missing
     request_count / failed token extraction (charge-silently-0 class);
  3. the recorded charge == calculate_cost(list_price, observed_metrics) within
     a tolerance — an INDEPENDENT recomputation via the canonical Python pricing
     engine (unitysvc_core), cross-validating the gateway's Lua charge path.

Because step 3 recomputes from whatever tokens/bytes actually came back, it
needs no prediction and works for constant, per-request, and token/byte pricing
alike.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from pydantic import TypeAdapter
from unitysvc_core.models.pricing import Pricing, UsageData

_PRICING_ADAPTER: TypeAdapter[object] = TypeAdapter(Pricing)

# UsageData field a given pricing ``type`` charges on — the "priced dimension"
# whose metric must be present and non-zero for the charge to be meaningful.
# (constant/per-request are quantity-deterministic and handled separately.)
_PRICED_DIMENSION: dict[str, tuple[str, ...]] = {
    "one_million_tokens": ("input_tokens", "output_tokens", "total_tokens"),
    "one_byte": ("one_byte",),
    "count": ("count",),
}
_PER_REQUEST_TYPES = frozenset({"constant", "count"})


@dataclass
class BillingVerifyResult:
    """Outcome of verifying one test request's billing."""

    ok: bool
    service: str
    reasons: list[str] = field(default_factory=list)
    observed_charge: Decimal | None = None
    recomputed_charge: Decimal | None = None
    observed_metrics: dict[str, object] = field(default_factory=dict)

    def summary(self) -> str:
        head = "PASS" if self.ok else "FAIL"
        detail = "; ".join(self.reasons) if self.reasons else "billing verified"
        return f"[billing:{head}] {self.service}: {detail}"


def recompute_charge(
    list_price: dict[str, object], usage_metrics: dict[str, object]
) -> Decimal:
    """Independently recompute the charge from the declared ``list_price`` and
    the OBSERVED ``usage_metrics``, via the canonical unitysvc_core pricing
    engine. Distinct implementation from the gateway's Lua, so a match
    cross-validates both metric extraction and pricing application."""
    price = _PRICING_ADAPTER.validate_python(list_price)
    usage = UsageData.model_validate(_usage_data_kwargs(usage_metrics))
    # Every PriceData exposes calculate_cost(usage, ...) -> Decimal.
    return price.calculate_cost(usage)  # type: ignore[attr-defined,no-any-return]


def _usage_data_kwargs(metrics: dict[str, object]) -> dict[str, object]:
    """Keep only keys UsageData accepts, coercing numeric strings."""
    allowed = UsageData.model_fields
    out: dict[str, object] = {}
    for key, value in metrics.items():
        if key in allowed and value is not None:
            out[key] = value
    return out


def verify_billing(
    *,
    service: str,
    list_price: dict[str, object] | None,
    usage_event: dict[str, object] | None,
    tolerance: Decimal = Decimal("0.0001"),
    min_expected_metrics: dict[str, float] | None = None,
) -> BillingVerifyResult:
    """Verify one test request's billing against its declared pricing.

    Args:
        service: service name (for reporting).
        list_price: the service listing's ``list_price`` dict (None / falsy =
            free service; nothing to verify, passes trivially).
        usage_event: the joined usage event from the request-logs API, carrying
            ``usage_metrics`` and the recorded charge (``total_customer_charge``
            or ``customer_charge``). None = NO usage event was produced.
        tolerance: absolute charge tolerance (rounding / float drift).
        min_expected_metrics: floors for the priced dimension, e.g.
            ``{"output_tokens": 1}`` — proves the response was actually metered.
    """
    result = BillingVerifyResult(ok=True, service=service)

    # Free service: no billing to verify.
    if not list_price:
        return result

    ptype = str(list_price.get("type", ""))

    # (1) a usage event must exist for a billable service.
    if not usage_event:
        result.ok = False
        result.reasons.append(
            "no usage event for a billable request (charge silently skipped)"
        )
        return result

    metrics = _coerce_metrics(usage_event.get("usage_metrics") or {})
    result.observed_metrics = metrics

    # (2) the priced-dimension metric must be present and non-zero, so we know
    #     the request was actually metered (not charged on an empty event).
    dims = _PRICED_DIMENSION.get(ptype)
    if dims is not None:
        if not any(_num(metrics.get(d)) > 0 for d in dims):
            result.ok = False
            result.reasons.append(
                f"priced dimension {'/'.join(dims)} is absent or zero on the "
                f"usage event — request not metered (would charge 0)"
            )
    elif ptype in _PER_REQUEST_TYPES:
        if _num(metrics.get("count")) <= 0 and _num(metrics.get("request_count")) <= 0:
            result.ok = False
            result.reasons.append(
                "per-request pricing but no request count on the usage event "
                "(the API-gateway request_count=missing bug — charges 0)"
            )

    for name, floor in (min_expected_metrics or {}).items():
        if _num(metrics.get(name)) < floor:
            result.ok = False
            result.reasons.append(
                f"metric {name}={metrics.get(name)!r} below expected floor {floor}"
            )

    # (3) recorded charge must match an independent recompute from the metrics.
    observed = _recorded_charge(usage_event)
    result.observed_charge = observed
    try:
        recomputed = recompute_charge(list_price, metrics)
        result.recomputed_charge = recomputed
    except Exception as exc:  # noqa: BLE001 — surface any pricing-parse failure
        result.ok = False
        result.reasons.append(f"could not recompute charge from list_price: {exc}")
        return result

    if observed is None:
        result.ok = False
        result.reasons.append("usage event carries no recorded charge")
    elif abs(observed - recomputed) > tolerance:
        result.ok = False
        result.reasons.append(
            f"charge mismatch: recorded {observed} != recomputed "
            f"{recomputed} (|Δ| > {tolerance}) — gateway pricing disagrees "
            f"with the canonical engine for the observed usage"
        )

    return result


def _coerce_metrics(raw: object) -> dict[str, object]:
    import json

    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return {}
    return dict(raw) if isinstance(raw, dict) else {}


def _recorded_charge(usage_event: dict[str, object]) -> Decimal | None:
    metrics = _coerce_metrics(usage_event.get("usage_metrics") or {})
    for key in ("total_customer_charge", "customer_charge"):
        for src in (usage_event, metrics):
            if src.get(key) is not None:
                try:
                    return Decimal(str(src[key]))
                except (ValueError, ArithmeticError):
                    return None
    return None


def _num(value: object) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
