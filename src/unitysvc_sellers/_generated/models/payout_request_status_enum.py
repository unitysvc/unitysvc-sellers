from typing import Literal, cast

PayoutRequestStatusEnum = Literal['cancelled', 'completed', 'failed', 'pending', 'processing']

PAYOUT_REQUEST_STATUS_ENUM_VALUES: set[PayoutRequestStatusEnum] = { 'cancelled', 'completed', 'failed', 'pending', 'processing',  }

def check_payout_request_status_enum(value: str) -> PayoutRequestStatusEnum:
    if value in PAYOUT_REQUEST_STATUS_ENUM_VALUES:
        return cast(PayoutRequestStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PAYOUT_REQUEST_STATUS_ENUM_VALUES!r}")
