from typing import Literal, cast

ListingStatusEnum = Literal['deprecated', 'draft', 'ready']

LISTING_STATUS_ENUM_VALUES: set[ListingStatusEnum] = { 'deprecated', 'draft', 'ready',  }

def check_listing_status_enum(value: str) -> ListingStatusEnum:
    if value in LISTING_STATUS_ENUM_VALUES:
        return cast(ListingStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LISTING_STATUS_ENUM_VALUES!r}")
