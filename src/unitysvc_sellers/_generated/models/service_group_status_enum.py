from typing import Literal, cast

ServiceGroupStatusEnum = Literal["active", "archived", "draft", "private"]

SERVICE_GROUP_STATUS_ENUM_VALUES: set[ServiceGroupStatusEnum] = {
    "active",
    "archived",
    "draft",
    "private",
}


def check_service_group_status_enum(value: str) -> ServiceGroupStatusEnum:
    if value in SERVICE_GROUP_STATUS_ENUM_VALUES:
        return cast(ServiceGroupStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SERVICE_GROUP_STATUS_ENUM_VALUES!r}")
