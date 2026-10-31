from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.room_settings_update_status_type_0 import (
    RoomSettingsUpdateStatusType0,
    check_room_settings_update_status_type_0,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomSettingsUpdate")


@_attrs_define
class RoomSettingsUpdate:
    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    """ Markdown; null clears the description """
    retention_seconds: int | None | Unset = UNSET
    status: None | RoomSettingsUpdateStatusType0 | Unset = UNSET
    """ The owner's operational status: paused auto-replies with pause_message; readonly lets only the owner and
    moderators post """
    pause_message: None | str | Unset = UNSET
    """ Null clears it """

    def to_dict(self) -> dict[str, Any]:
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        retention_seconds: int | None | Unset
        if isinstance(self.retention_seconds, Unset):
            retention_seconds = UNSET
        else:
            retention_seconds = self.retention_seconds

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, str):
            status = self.status
        else:
            status = self.status

        pause_message: None | str | Unset
        if isinstance(self.pause_message, Unset):
            pause_message = UNSET
        else:
            pause_message = self.pause_message

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if retention_seconds is not UNSET:
            field_dict["retention_seconds"] = retention_seconds
        if status is not UNSET:
            field_dict["status"] = status
        if pause_message is not UNSET:
            field_dict["pause_message"] = pause_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_retention_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        retention_seconds = _parse_retention_seconds(d.pop("retention_seconds", UNSET))

        def _parse_status(data: object) -> None | RoomSettingsUpdateStatusType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = check_room_settings_update_status_type_0(data)

                return status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RoomSettingsUpdateStatusType0 | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_pause_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pause_message = _parse_pause_message(d.pop("pause_message", UNSET))

        room_settings_update = cls(
            name=name,
            description=description,
            retention_seconds=retention_seconds,
            status=status,
            pause_message=pause_message,
        )

        return room_settings_update
