from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomSettingsUpdate")


@_attrs_define
class RoomSettingsUpdate:
    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    """ Markdown; null clears the description """
    retention_seconds: int | None | Unset = UNSET
    expires_at: datetime.datetime | None | Unset = UNSET
    idle_expiry_seconds: int | None | Unset = UNSET

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

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        idle_expiry_seconds: int | None | Unset
        if isinstance(self.idle_expiry_seconds, Unset):
            idle_expiry_seconds = UNSET
        else:
            idle_expiry_seconds = self.idle_expiry_seconds

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if retention_seconds is not UNSET:
            field_dict["retention_seconds"] = retention_seconds
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if idle_expiry_seconds is not UNSET:
            field_dict["idle_expiry_seconds"] = idle_expiry_seconds

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

        def _parse_expires_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        def _parse_idle_expiry_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        idle_expiry_seconds = _parse_idle_expiry_seconds(d.pop("idle_expiry_seconds", UNSET))

        room_settings_update = cls(
            name=name,
            description=description,
            retention_seconds=retention_seconds,
            expires_at=expires_at,
            idle_expiry_seconds=idle_expiry_seconds,
        )

        return room_settings_update
