from typing import Literal, cast

ProviderAccountRateLimitWindowType0 = Literal["day", "hour", "minute", "month", "second"]

PROVIDER_ACCOUNT_RATE_LIMIT_WINDOW_TYPE_0_VALUES: set[ProviderAccountRateLimitWindowType0] = {
    "day",
    "hour",
    "minute",
    "month",
    "second",
}


def check_provider_account_rate_limit_window_type_0(value: str) -> ProviderAccountRateLimitWindowType0:
    if value in PROVIDER_ACCOUNT_RATE_LIMIT_WINDOW_TYPE_0_VALUES:
        return cast(ProviderAccountRateLimitWindowType0, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PROVIDER_ACCOUNT_RATE_LIMIT_WINDOW_TYPE_0_VALUES!r}")
