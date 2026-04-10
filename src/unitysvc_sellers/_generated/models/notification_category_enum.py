from typing import Literal, cast

NotificationCategoryEnum = Literal['account', 'billing', 'message', 'security', 'service', 'subscription', 'team', 'wallet']

NOTIFICATION_CATEGORY_ENUM_VALUES: set[NotificationCategoryEnum] = { 'account', 'billing', 'message', 'security', 'service', 'subscription', 'team', 'wallet',  }

def check_notification_category_enum(value: str) -> NotificationCategoryEnum:
    if value in NOTIFICATION_CATEGORY_ENUM_VALUES:
        return cast(NotificationCategoryEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {NOTIFICATION_CATEGORY_ENUM_VALUES!r}")
