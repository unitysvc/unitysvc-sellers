from typing import Literal, cast

PlanSubscriptionStatusEnum = Literal['active', 'canceled', 'expired', 'incomplete', 'incomplete_expired', 'past_due', 'paused', 'trialing', 'unpaid']

PLAN_SUBSCRIPTION_STATUS_ENUM_VALUES: set[PlanSubscriptionStatusEnum] = { 'active', 'canceled', 'expired', 'incomplete', 'incomplete_expired', 'past_due', 'paused', 'trialing', 'unpaid',  }

def check_plan_subscription_status_enum(value: str) -> PlanSubscriptionStatusEnum:
    if value in PLAN_SUBSCRIPTION_STATUS_ENUM_VALUES:
        return cast(PlanSubscriptionStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PLAN_SUBSCRIPTION_STATUS_ENUM_VALUES!r}")
