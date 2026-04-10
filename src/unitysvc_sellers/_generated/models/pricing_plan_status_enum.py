from typing import Literal, cast

PricingPlanStatusEnum = Literal['active', 'expired', 'incomplete', 'private']

PRICING_PLAN_STATUS_ENUM_VALUES: set[PricingPlanStatusEnum] = { 'active', 'expired', 'incomplete', 'private',  }

def check_pricing_plan_status_enum(value: str) -> PricingPlanStatusEnum:
    if value in PRICING_PLAN_STATUS_ENUM_VALUES:
        return cast(PricingPlanStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PRICING_PLAN_STATUS_ENUM_VALUES!r}")
