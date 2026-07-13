"""Tests for test-time billing verification (unitysvc#1522).

Drives the three failure modes it must catch — missing usage event, missing
priced metric (charges 0), and a charge that disagrees with the canonical
recompute — plus the happy path, for both token-metered and per-request pricing.
"""

from decimal import Decimal

from unitysvc_sellers.billing_verify import recompute_charge, verify_billing

TOKEN_PRICE = {"input": "1.0", "output": "2.0", "type": "one_million_tokens"}
CONST_PRICE = {"price": "0.01", "type": "constant"}


def _event(metrics):
    return {"usage_metrics": metrics}


def test_recompute_matches_hand_computation():
    # 500 in / 1000 out at 1.0/2.0 per 1M = 0.0005 + 0.002 = 0.0025
    got = recompute_charge(TOKEN_PRICE, {"input_tokens": 500, "output_tokens": 1000})
    assert got == Decimal("0.0025")


def test_happy_path_token_service():
    ev = _event({"input_tokens": 500, "output_tokens": 1000,
                 "total_customer_charge": "0.0025"})
    r = verify_billing(service="llm", list_price=TOKEN_PRICE, usage_event=ev)
    assert r.ok, r.summary()


def test_missing_usage_event_fails():  # Q2: the translate skip class
    r = verify_billing(service="llm", list_price=TOKEN_PRICE, usage_event=None)
    assert not r.ok
    assert "no usage event" in r.summary()


def test_metered_zero_tokens_fails():  # priced dimension absent/zero
    ev = _event({"input_tokens": 0, "output_tokens": 0,
                 "total_customer_charge": "0"})
    r = verify_billing(service="llm", list_price=TOKEN_PRICE, usage_event=ev)
    assert not r.ok
    assert "not metered" in r.summary()


def test_charge_mismatch_fails():  # gateway disagrees with canonical engine
    ev = _event({"input_tokens": 500, "output_tokens": 1000,
                 "total_customer_charge": "0.0009"})  # wrong (should be 0.0025)
    r = verify_billing(service="llm", list_price=TOKEN_PRICE, usage_event=ev)
    assert not r.ok
    assert "charge mismatch" in r.summary()


def test_per_request_missing_count_fails():  # Q1: the request_count=missing bug
    # constant pricing but the API-gateway event carries no count → would charge 0
    ev = _event({"bytes_in": 100, "bytes_out": 200, "total_customer_charge": "0"})
    r = verify_billing(service="proxy", list_price=CONST_PRICE, usage_event=ev)
    assert not r.ok
    assert "request count" in r.summary()


def test_per_request_happy_path():
    ev = _event({"count": 1, "total_customer_charge": "0.01"})
    r = verify_billing(service="proxy", list_price=CONST_PRICE, usage_event=ev)
    assert r.ok, r.summary()


def test_free_service_passes_trivially():
    r = verify_billing(service="free", list_price=None, usage_event=None)
    assert r.ok


def test_min_expected_metrics_floor():
    ev = _event({"input_tokens": 5, "output_tokens": 0,
                 "total_customer_charge": "0.000005"})
    r = verify_billing(service="llm", list_price=TOKEN_PRICE, usage_event=ev,
                       min_expected_metrics={"output_tokens": 1})
    assert not r.ok
    assert "below expected floor" in r.summary()
