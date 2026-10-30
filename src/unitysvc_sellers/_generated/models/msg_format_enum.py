from typing import Literal, cast

MsgFormatEnum = Literal["markdown", "text"]

MSG_FORMAT_ENUM_VALUES: set[MsgFormatEnum] = {
    "markdown",
    "text",
}


def check_msg_format_enum(value: str) -> MsgFormatEnum:
    if value in MSG_FORMAT_ENUM_VALUES:
        return cast(MsgFormatEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MSG_FORMAT_ENUM_VALUES!r}")
