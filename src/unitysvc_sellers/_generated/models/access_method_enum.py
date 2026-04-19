from typing import Literal, cast

AccessMethodEnum = Literal["grpc", "http", "smtp", "websocket"]

ACCESS_METHOD_ENUM_VALUES: set[AccessMethodEnum] = {
    "grpc",
    "http",
    "smtp",
    "websocket",
}


def check_access_method_enum(value: str) -> AccessMethodEnum:
    if value in ACCESS_METHOD_ENUM_VALUES:
        return cast(AccessMethodEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ACCESS_METHOD_ENUM_VALUES!r}")
