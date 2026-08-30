from typing import Literal, cast

ServiceKindEnum = Literal["platform", "platform_member", "regular"]

SERVICE_KIND_ENUM_VALUES: set[ServiceKindEnum] = {
    "platform",
    "platform_member",
    "regular",
}


def check_service_kind_enum(value: str) -> ServiceKindEnum:
    if value in SERVICE_KIND_ENUM_VALUES:
        return cast(ServiceKindEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SERVICE_KIND_ENUM_VALUES!r}")
