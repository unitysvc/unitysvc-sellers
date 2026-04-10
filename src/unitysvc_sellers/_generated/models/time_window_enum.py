from typing import Literal, cast

TimeWindowEnum = Literal['day', 'hour', 'minute', 'month', 'second']

TIME_WINDOW_ENUM_VALUES: set[TimeWindowEnum] = { 'day', 'hour', 'minute', 'month', 'second',  }

def check_time_window_enum(value: str) -> TimeWindowEnum:
    if value in TIME_WINDOW_ENUM_VALUES:
        return cast(TimeWindowEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TIME_WINDOW_ENUM_VALUES!r}")
