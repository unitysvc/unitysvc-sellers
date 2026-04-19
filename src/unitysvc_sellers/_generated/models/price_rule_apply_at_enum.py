from typing import Literal, cast

PriceRuleApplyAtEnum = Literal["request", "statement"]

PRICE_RULE_APPLY_AT_ENUM_VALUES: set[PriceRuleApplyAtEnum] = {
    "request",
    "statement",
}


def check_price_rule_apply_at_enum(value: str) -> PriceRuleApplyAtEnum:
    if value in PRICE_RULE_APPLY_AT_ENUM_VALUES:
        return cast(PriceRuleApplyAtEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PRICE_RULE_APPLY_AT_ENUM_VALUES!r}")
