from typing import Literal, cast

MsgTypeEnum = Literal["failure", "info", "success", "warning"]

MSG_TYPE_ENUM_VALUES: set[MsgTypeEnum] = {
    "failure",
    "info",
    "success",
    "warning",
}


def check_msg_type_enum(value: str) -> MsgTypeEnum:
    if value in MSG_TYPE_ENUM_VALUES:
        return cast(MsgTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MSG_TYPE_ENUM_VALUES!r}")
