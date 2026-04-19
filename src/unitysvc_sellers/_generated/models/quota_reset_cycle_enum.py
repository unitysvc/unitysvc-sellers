from typing import Literal, cast

QuotaResetCycleEnum = Literal["daily", "monthly", "weekly", "yearly"]

QUOTA_RESET_CYCLE_ENUM_VALUES: set[QuotaResetCycleEnum] = {
    "daily",
    "monthly",
    "weekly",
    "yearly",
}


def check_quota_reset_cycle_enum(value: str) -> QuotaResetCycleEnum:
    if value in QUOTA_RESET_CYCLE_ENUM_VALUES:
        return cast(QuotaResetCycleEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {QUOTA_RESET_CYCLE_ENUM_VALUES!r}")
