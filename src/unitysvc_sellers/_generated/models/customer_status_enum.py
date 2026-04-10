from typing import Literal, cast

CustomerStatusEnum = Literal['active', 'suspended']

CUSTOMER_STATUS_ENUM_VALUES: set[CustomerStatusEnum] = { 'active', 'suspended',  }

def check_customer_status_enum(value: str) -> CustomerStatusEnum:
    if value in CUSTOMER_STATUS_ENUM_VALUES:
        return cast(CustomerStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CUSTOMER_STATUS_ENUM_VALUES!r}")
