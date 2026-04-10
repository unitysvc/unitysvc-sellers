from typing import Literal, cast

AuthMethodEnum = Literal['api_key', 'basic_auth', 'bearer_token', 'jwt', 'oauth']

AUTH_METHOD_ENUM_VALUES: set[AuthMethodEnum] = { 'api_key', 'basic_auth', 'bearer_token', 'jwt', 'oauth',  }

def check_auth_method_enum(value: str) -> AuthMethodEnum:
    if value in AUTH_METHOD_ENUM_VALUES:
        return cast(AuthMethodEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {AUTH_METHOD_ENUM_VALUES!r}")
