from typing import Literal, cast

ServiceVisibilityEnum = Literal['private', 'public', 'unlisted']

SERVICE_VISIBILITY_ENUM_VALUES: set[ServiceVisibilityEnum] = { 'private', 'public', 'unlisted',  }

def check_service_visibility_enum(value: str) -> ServiceVisibilityEnum:
    if value in SERVICE_VISIBILITY_ENUM_VALUES:
        return cast(ServiceVisibilityEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SERVICE_VISIBILITY_ENUM_VALUES!r}")
