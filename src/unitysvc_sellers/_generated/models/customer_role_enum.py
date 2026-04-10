from typing import Literal, cast

CustomerRoleEnum = Literal['billing_manager', 'member', 'owner']

CUSTOMER_ROLE_ENUM_VALUES: set[CustomerRoleEnum] = { 'billing_manager', 'member', 'owner',  }

def check_customer_role_enum(value: str) -> CustomerRoleEnum:
    if value in CUSTOMER_ROLE_ENUM_VALUES:
        return cast(CustomerRoleEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CUSTOMER_ROLE_ENUM_VALUES!r}")
