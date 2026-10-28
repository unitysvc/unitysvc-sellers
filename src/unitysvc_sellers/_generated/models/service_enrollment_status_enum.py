from typing import Literal, cast

ServiceEnrollmentStatusEnum = Literal["active", "cancelled", "incomplete", "paused", "pending"]

SERVICE_ENROLLMENT_STATUS_ENUM_VALUES: set[ServiceEnrollmentStatusEnum] = {
    "active",
    "cancelled",
    "incomplete",
    "paused",
    "pending",
}


def check_service_enrollment_status_enum(value: str) -> ServiceEnrollmentStatusEnum:
    if value in SERVICE_ENROLLMENT_STATUS_ENUM_VALUES:
        return cast(ServiceEnrollmentStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SERVICE_ENROLLMENT_STATUS_ENUM_VALUES!r}")
