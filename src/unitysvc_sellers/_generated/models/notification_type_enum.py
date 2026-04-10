from typing import Literal, cast

NotificationTypeEnum = Literal['error', 'info', 'success', 'warning']

NOTIFICATION_TYPE_ENUM_VALUES: set[NotificationTypeEnum] = { 'error', 'info', 'success', 'warning',  }

def check_notification_type_enum(value: str) -> NotificationTypeEnum:
    if value in NOTIFICATION_TYPE_ENUM_VALUES:
        return cast(NotificationTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {NOTIFICATION_TYPE_ENUM_VALUES!r}")
