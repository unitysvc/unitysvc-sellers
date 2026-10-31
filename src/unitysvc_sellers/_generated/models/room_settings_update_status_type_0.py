from typing import Literal, cast

RoomSettingsUpdateStatusType0 = Literal["active", "paused", "readonly"]

ROOM_SETTINGS_UPDATE_STATUS_TYPE_0_VALUES: set[RoomSettingsUpdateStatusType0] = {
    "active",
    "paused",
    "readonly",
}


def check_room_settings_update_status_type_0(value: str) -> RoomSettingsUpdateStatusType0:
    if value in ROOM_SETTINGS_UPDATE_STATUS_TYPE_0_VALUES:
        return cast(RoomSettingsUpdateStatusType0, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ROOM_SETTINGS_UPDATE_STATUS_TYPE_0_VALUES!r}")
