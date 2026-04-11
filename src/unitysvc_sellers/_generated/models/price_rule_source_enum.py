from typing import Literal, cast

PriceRuleSourceEnum = Literal['plan_name', 'plan_tier', 'platform_code', 'seller_code']

PRICE_RULE_SOURCE_ENUM_VALUES: set[PriceRuleSourceEnum] = { 'plan_name', 'plan_tier', 'platform_code', 'seller_code',  }

def check_price_rule_source_enum(value: str) -> PriceRuleSourceEnum:
    if value in PRICE_RULE_SOURCE_ENUM_VALUES:
        return cast(PriceRuleSourceEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PRICE_RULE_SOURCE_ENUM_VALUES!r}")
