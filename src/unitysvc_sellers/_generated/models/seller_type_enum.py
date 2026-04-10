from typing import Literal, cast

SellerTypeEnum = Literal['corporation', 'individual', 'organization', 'partnership']

SELLER_TYPE_ENUM_VALUES: set[SellerTypeEnum] = { 'corporation', 'individual', 'organization', 'partnership',  }

def check_seller_type_enum(value: str) -> SellerTypeEnum:
    if value in SELLER_TYPE_ENUM_VALUES:
        return cast(SellerTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SELLER_TYPE_ENUM_VALUES!r}")
