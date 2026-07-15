"""Tests for the UNITYSVC_EXPERIMENTAL opt-in gate (unitysvc#1540)."""

from __future__ import annotations

import pytest

from unitysvc_sellers import (
    ExperimentalDisabledError,
    experimental_enabled,
    require_experimental,
)


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv("UNITYSVC_EXPERIMENTAL", raising=False)
    assert experimental_enabled() is False
    with pytest.raises(ExperimentalDisabledError, match="UNITYSVC_EXPERIMENTAL=1"):
        require_experimental("Orders")


@pytest.mark.parametrize("val", ["1", "true", "TRUE", "yes", "on"])
def test_truthy_values_enable(monkeypatch, val):
    monkeypatch.setenv("UNITYSVC_EXPERIMENTAL", val)
    assert experimental_enabled() is True
    require_experimental("Orders")  # does not raise


@pytest.mark.parametrize("val", ["", "0", "false", "no", "off", "nope"])
def test_falsey_values_disable(monkeypatch, val):
    monkeypatch.setenv("UNITYSVC_EXPERIMENTAL", val)
    assert experimental_enabled() is False
