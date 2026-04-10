from typing import Literal, cast

SellerStatusEnum = Literal['active', 'disabled', 'draft', 'pending']

SELLER_STATUS_ENUM_VALUES: set[SellerStatusEnum] = { 'active', 'disabled', 'draft', 'pending',  }

def check_seller_status_enum(value: str) -> SellerStatusEnum:
    if value in SELLER_STATUS_ENUM_VALUES:
        return cast(SellerStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SELLER_STATUS_ENUM_VALUES!r}")
