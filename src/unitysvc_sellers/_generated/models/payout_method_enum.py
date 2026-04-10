from typing import Literal, cast

PayoutMethodEnum = Literal['check', 'stripe_connect', 'zelle']

PAYOUT_METHOD_ENUM_VALUES: set[PayoutMethodEnum] = { 'check', 'stripe_connect', 'zelle',  }

def check_payout_method_enum(value: str) -> PayoutMethodEnum:
    if value in PAYOUT_METHOD_ENUM_VALUES:
        return cast(PayoutMethodEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYOUT_METHOD_ENUM_VALUES!r}")
