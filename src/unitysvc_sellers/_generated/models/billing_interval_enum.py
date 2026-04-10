from typing import Literal, cast

BillingIntervalEnum = Literal['annual', 'monthly']

BILLING_INTERVAL_ENUM_VALUES: set[BillingIntervalEnum] = { 'annual', 'monthly',  }

def check_billing_interval_enum(value: str) -> BillingIntervalEnum:
    if value in BILLING_INTERVAL_ENUM_VALUES:
        return cast(BillingIntervalEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {BILLING_INTERVAL_ENUM_VALUES!r}")
