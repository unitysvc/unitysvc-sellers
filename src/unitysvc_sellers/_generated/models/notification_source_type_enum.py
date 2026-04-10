from typing import Literal, cast

NotificationSourceTypeEnum = Literal['admin', 'bot', 'integration', 'service', 'user']

NOTIFICATION_SOURCE_TYPE_ENUM_VALUES: set[NotificationSourceTypeEnum] = { 'admin', 'bot', 'integration', 'service', 'user',  }

def check_notification_source_type_enum(value: str) -> NotificationSourceTypeEnum:
    if value in NOTIFICATION_SOURCE_TYPE_ENUM_VALUES:
        return cast(NotificationSourceTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {NOTIFICATION_SOURCE_TYPE_ENUM_VALUES!r}")
