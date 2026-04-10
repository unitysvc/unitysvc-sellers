from typing import Literal, cast

PriceRuleLifecycleStatusEnum = Literal['active', 'cancelled', 'draft', 'expired', 'paused', 'scheduled']

PRICE_RULE_LIFECYCLE_STATUS_ENUM_VALUES: set[PriceRuleLifecycleStatusEnum] = { 'active', 'cancelled', 'draft', 'expired', 'paused', 'scheduled',  }

def check_price_rule_lifecycle_status_enum(value: str) -> PriceRuleLifecycleStatusEnum:
    if value in PRICE_RULE_LIFECYCLE_STATUS_ENUM_VALUES:
        return cast(PriceRuleLifecycleStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PRICE_RULE_LIFECYCLE_STATUS_ENUM_VALUES!r}")
