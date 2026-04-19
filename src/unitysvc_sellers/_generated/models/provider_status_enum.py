from typing import Literal, cast

ProviderStatusEnum = Literal["deprecated", "draft", "ready"]

PROVIDER_STATUS_ENUM_VALUES: set[ProviderStatusEnum] = {
    "deprecated",
    "draft",
    "ready",
}


def check_provider_status_enum(value: str) -> ProviderStatusEnum:
    if value in PROVIDER_STATUS_ENUM_VALUES:
        return cast(ProviderStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PROVIDER_STATUS_ENUM_VALUES!r}")
