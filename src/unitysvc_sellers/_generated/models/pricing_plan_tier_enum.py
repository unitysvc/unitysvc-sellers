from typing import Literal, cast

PricingPlanTierEnum = Literal['enterprise', 'free', 'individual', 'team']

PRICING_PLAN_TIER_ENUM_VALUES: set[PricingPlanTierEnum] = { 'enterprise', 'free', 'individual', 'team',  }

def check_pricing_plan_tier_enum(value: str) -> PricingPlanTierEnum:
    if value in PRICING_PLAN_TIER_ENUM_VALUES:
        return cast(PricingPlanTierEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PRICING_PLAN_TIER_ENUM_VALUES!r}")
