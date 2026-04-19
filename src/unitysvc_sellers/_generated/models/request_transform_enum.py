from typing import Literal, cast

RequestTransformEnum = Literal["body_transformer", "proxy_rewrite", "set_body"]

REQUEST_TRANSFORM_ENUM_VALUES: set[RequestTransformEnum] = {
    "body_transformer",
    "proxy_rewrite",
    "set_body",
}


def check_request_transform_enum(value: str) -> RequestTransformEnum:
    if value in REQUEST_TRANSFORM_ENUM_VALUES:
        return cast(RequestTransformEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {REQUEST_TRANSFORM_ENUM_VALUES!r}")
