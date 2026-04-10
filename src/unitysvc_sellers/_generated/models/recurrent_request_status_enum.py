from typing import Literal, cast

RecurrentRequestStatusEnum = Literal['active', 'cancelled', 'draft', 'paused']

RECURRENT_REQUEST_STATUS_ENUM_VALUES: set[RecurrentRequestStatusEnum] = { 'active', 'cancelled', 'draft', 'paused',  }

def check_recurrent_request_status_enum(value: str) -> RecurrentRequestStatusEnum:
    if value in RECURRENT_REQUEST_STATUS_ENUM_VALUES:
        return cast(RecurrentRequestStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RECURRENT_REQUEST_STATUS_ENUM_VALUES!r}")
