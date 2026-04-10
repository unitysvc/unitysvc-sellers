from typing import Literal, cast

DisputeReasonEnum = Literal['billing', 'no_response', 'other', 'service_quality', 'unauthorized']

DISPUTE_REASON_ENUM_VALUES: set[DisputeReasonEnum] = { 'billing', 'no_response', 'other', 'service_quality', 'unauthorized',  }

def check_dispute_reason_enum(value: str) -> DisputeReasonEnum:
    if value in DISPUTE_REASON_ENUM_VALUES:
        return cast(DisputeReasonEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DISPUTE_REASON_ENUM_VALUES!r}")
