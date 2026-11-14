from typing import Literal, cast

LiveStateEnum = Literal["accepting", "draining", "off"]

LIVE_STATE_ENUM_VALUES: set[LiveStateEnum] = {
    "accepting",
    "draining",
    "off",
}


def check_live_state_enum(value: str) -> LiveStateEnum:
    if value in LIVE_STATE_ENUM_VALUES:
        return cast(LiveStateEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LIVE_STATE_ENUM_VALUES!r}")
