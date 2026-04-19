from typing import Literal, cast

OveragePolicyEnum = Literal["block", "charge", "queue", "throttle"]

OVERAGE_POLICY_ENUM_VALUES: set[OveragePolicyEnum] = {
    "block",
    "charge",
    "queue",
    "throttle",
}


def check_overage_policy_enum(value: str) -> OveragePolicyEnum:
    if value in OVERAGE_POLICY_ENUM_VALUES:
        return cast(OveragePolicyEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {OVERAGE_POLICY_ENUM_VALUES!r}")
