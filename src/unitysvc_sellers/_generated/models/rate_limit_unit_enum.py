from typing import Literal, cast

RateLimitUnitEnum = Literal['bytes', 'concurrent', 'input_tokens', 'output_tokens', 'requests', 'tokens']

RATE_LIMIT_UNIT_ENUM_VALUES: set[RateLimitUnitEnum] = { 'bytes', 'concurrent', 'input_tokens', 'output_tokens', 'requests', 'tokens',  }

def check_rate_limit_unit_enum(value: str) -> RateLimitUnitEnum:
    if value in RATE_LIMIT_UNIT_ENUM_VALUES:
        return cast(RateLimitUnitEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RATE_LIMIT_UNIT_ENUM_VALUES!r}")
