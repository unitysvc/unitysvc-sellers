from typing import Literal, cast

CustomerTypeEnum = Literal['business', 'corporate', 'individual']

CUSTOMER_TYPE_ENUM_VALUES: set[CustomerTypeEnum] = { 'business', 'corporate', 'individual',  }

def check_customer_type_enum(value: str) -> CustomerTypeEnum:
    if value in CUSTOMER_TYPE_ENUM_VALUES:
        return cast(CustomerTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CUSTOMER_TYPE_ENUM_VALUES!r}")
