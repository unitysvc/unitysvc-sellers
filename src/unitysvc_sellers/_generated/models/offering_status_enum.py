from typing import Literal, cast

OfferingStatusEnum = Literal["deprecated", "draft", "ready"]

OFFERING_STATUS_ENUM_VALUES: set[OfferingStatusEnum] = {
    "deprecated",
    "draft",
    "ready",
}


def check_offering_status_enum(value: str) -> OfferingStatusEnum:
    if value in OFFERING_STATUS_ENUM_VALUES:
        return cast(OfferingStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {OFFERING_STATUS_ENUM_VALUES!r}")
