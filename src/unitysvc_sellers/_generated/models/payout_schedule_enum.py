from typing import Literal, cast

PayoutScheduleEnum = Literal['automatic', 'on_demand']

PAYOUT_SCHEDULE_ENUM_VALUES: set[PayoutScheduleEnum] = { 'automatic', 'on_demand',  }

def check_payout_schedule_enum(value: str) -> PayoutScheduleEnum:
    if value in PAYOUT_SCHEDULE_ENUM_VALUES:
        return cast(PayoutScheduleEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYOUT_SCHEDULE_ENUM_VALUES!r}")
