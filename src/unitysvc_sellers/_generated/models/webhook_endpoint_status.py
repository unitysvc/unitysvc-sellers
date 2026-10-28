from typing import Literal, cast

WebhookEndpointStatus = Literal["disabled", "enabled"]

WEBHOOK_ENDPOINT_STATUS_VALUES: set[WebhookEndpointStatus] = {
    "disabled",
    "enabled",
}


def check_webhook_endpoint_status(value: str) -> WebhookEndpointStatus:
    if value in WEBHOOK_ENDPOINT_STATUS_VALUES:
        return cast(WebhookEndpointStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {WEBHOOK_ENDPOINT_STATUS_VALUES!r}")
