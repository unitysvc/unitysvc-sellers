from typing import Literal, cast

SellerTierEnum = Literal['partner', 'standard', 'trusted']

SELLER_TIER_ENUM_VALUES: set[SellerTierEnum] = { 'partner', 'standard', 'trusted',  }

def check_seller_tier_enum(value: str) -> SellerTierEnum:
    if value in SELLER_TIER_ENUM_VALUES:
        return cast(SellerTierEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SELLER_TIER_ENUM_VALUES!r}")
