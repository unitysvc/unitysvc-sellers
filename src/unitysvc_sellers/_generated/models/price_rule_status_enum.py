from typing import Literal, cast

PriceRuleStatusEnum = Literal['active', 'draft', 'paused']

PRICE_RULE_STATUS_ENUM_VALUES: set[PriceRuleStatusEnum] = { 'active', 'draft', 'paused',  }

def check_price_rule_status_enum(value: str) -> PriceRuleStatusEnum:
    if value in PRICE_RULE_STATUS_ENUM_VALUES:
        return cast(PriceRuleStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PRICE_RULE_STATUS_ENUM_VALUES!r}")
