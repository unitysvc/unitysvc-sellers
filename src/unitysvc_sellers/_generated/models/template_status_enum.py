from typing import Literal, cast

TemplateStatusEnum = Literal["active", "deprecated", "draft"]

TEMPLATE_STATUS_ENUM_VALUES: set[TemplateStatusEnum] = {
    "active",
    "deprecated",
    "draft",
}


def check_template_status_enum(value: str) -> TemplateStatusEnum:
    if value in TEMPLATE_STATUS_ENUM_VALUES:
        return cast(TemplateStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TEMPLATE_STATUS_ENUM_VALUES!r}")
