from typing import Literal, cast

SecretOwnerTypeEnum = Literal['customer', 'platform', 'seller']

SECRET_OWNER_TYPE_ENUM_VALUES: set[SecretOwnerTypeEnum] = { 'customer', 'platform', 'seller',  }

def check_secret_owner_type_enum(value: str) -> SecretOwnerTypeEnum:
    if value in SECRET_OWNER_TYPE_ENUM_VALUES:
        return cast(SecretOwnerTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SECRET_OWNER_TYPE_ENUM_VALUES!r}")
