from typing import Literal, cast

WebhookEventStatus = Literal["delivering", "expired", "failed", "pending", "succeeded"]

WEBHOOK_EVENT_STATUS_VALUES: set[WebhookEventStatus] = {
    "delivering",
    "expired",
    "failed",
    "pending",
    "succeeded",
}


def check_webhook_event_status(value: str) -> WebhookEventStatus:
    if value in WEBHOOK_EVENT_STATUS_VALUES:
        return cast(WebhookEventStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {WEBHOOK_EVENT_STATUS_VALUES!r}")
