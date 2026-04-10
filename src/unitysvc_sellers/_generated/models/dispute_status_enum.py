from typing import Literal, cast

DisputeStatusEnum = Literal['open', 'rejected', 'resolved', 'under_review']

DISPUTE_STATUS_ENUM_VALUES: set[DisputeStatusEnum] = { 'open', 'rejected', 'resolved', 'under_review',  }

def check_dispute_status_enum(value: str) -> DisputeStatusEnum:
    if value in DISPUTE_STATUS_ENUM_VALUES:
        return cast(DisputeStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DISPUTE_STATUS_ENUM_VALUES!r}")
