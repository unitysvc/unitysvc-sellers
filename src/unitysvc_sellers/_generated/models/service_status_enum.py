from typing import Literal, cast

ServiceStatusEnum = Literal['active', 'deprecated', 'draft', 'pending', 'rejected', 'review', 'suspended']

SERVICE_STATUS_ENUM_VALUES: set[ServiceStatusEnum] = { 'active', 'deprecated', 'draft', 'pending', 'rejected', 'review', 'suspended',  }

def check_service_status_enum(value: str) -> ServiceStatusEnum:
    if value in SERVICE_STATUS_ENUM_VALUES:
        return cast(ServiceStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SERVICE_STATUS_ENUM_VALUES!r}")
