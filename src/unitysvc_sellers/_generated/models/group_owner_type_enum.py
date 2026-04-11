from typing import Literal, cast

GroupOwnerTypeEnum = Literal['customer', 'platform', 'seller']

GROUP_OWNER_TYPE_ENUM_VALUES: set[GroupOwnerTypeEnum] = { 'customer', 'platform', 'seller',  }

def check_group_owner_type_enum(value: str) -> GroupOwnerTypeEnum:
    if value in GROUP_OWNER_TYPE_ENUM_VALUES:
        return cast(GroupOwnerTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GROUP_OWNER_TYPE_ENUM_VALUES!r}")
