from typing import Literal, cast

GroupTypeEnum = Literal['category', 'collection', 'misc', 'routable']

GROUP_TYPE_ENUM_VALUES: set[GroupTypeEnum] = { 'category', 'collection', 'misc', 'routable',  }

def check_group_type_enum(value: str) -> GroupTypeEnum:
    if value in GROUP_TYPE_ENUM_VALUES:
        return cast(GroupTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GROUP_TYPE_ENUM_VALUES!r}")
