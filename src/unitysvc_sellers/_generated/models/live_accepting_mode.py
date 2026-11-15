from typing import Literal, cast

LiveAcceptingMode = Literal["accepting", "draining"]

LIVE_ACCEPTING_MODE_VALUES: set[LiveAcceptingMode] = {
    "accepting",
    "draining",
}


def check_live_accepting_mode(value: str) -> LiveAcceptingMode:
    if value in LIVE_ACCEPTING_MODE_VALUES:
        return cast(LiveAcceptingMode, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LIVE_ACCEPTING_MODE_VALUES!r}")
