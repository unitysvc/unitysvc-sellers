from typing import Literal, cast

ServiceTypeEnum = Literal['analytics', 'compute', 'content', 'database', 'email', 'embedding', 'image_generation', 'llm', 'monitoring', 'notification', 'proxy', 'streaming']

SERVICE_TYPE_ENUM_VALUES: set[ServiceTypeEnum] = { 'analytics', 'compute', 'content', 'database', 'email', 'embedding', 'image_generation', 'llm', 'monitoring', 'notification', 'proxy', 'streaming',  }

def check_service_type_enum(value: str) -> ServiceTypeEnum:
    if value in SERVICE_TYPE_ENUM_VALUES:
        return cast(ServiceTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SERVICE_TYPE_ENUM_VALUES!r}")
