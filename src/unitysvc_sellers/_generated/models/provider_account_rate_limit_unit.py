from typing import Literal, cast

ProviderAccountRateLimitUnit = Literal["bytes", "concurrent", "input_tokens", "output_tokens", "requests", "tokens"]

PROVIDER_ACCOUNT_RATE_LIMIT_UNIT_VALUES: set[ProviderAccountRateLimitUnit] = {
    "bytes",
    "concurrent",
    "input_tokens",
    "output_tokens",
    "requests",
    "tokens",
}


def check_provider_account_rate_limit_unit(value: str) -> ProviderAccountRateLimitUnit:
    if value in PROVIDER_ACCOUNT_RATE_LIMIT_UNIT_VALUES:
        return cast(ProviderAccountRateLimitUnit, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PROVIDER_ACCOUNT_RATE_LIMIT_UNIT_VALUES!r}")
