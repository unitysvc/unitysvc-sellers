from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RoomActiveResponse")


@_attrs_define
class RoomActiveResponse:
    """What was recorded. ``capped``: ``offset`` was past the room's latest
    conversation message as recorded so far, so less was stored. Recording
    lags delivery briefly, so retry once a few seconds later. A room with no
    conversation message yet always reports ``capped`` (it may be lag), and a
    retry that is capped again means there is nothing more to record.

    """

    last_active_offset: int | None
    capped: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        last_active_offset: int | None
        last_active_offset = self.last_active_offset

        capped = self.capped

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "last_active_offset": last_active_offset,
                "capped": capped,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_last_active_offset(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        last_active_offset = _parse_last_active_offset(d.pop("last_active_offset"))

        capped = d.pop("capped")

        room_active_response = cls(
            last_active_offset=last_active_offset,
            capped=capped,
        )

        room_active_response.additional_properties = d
        return room_active_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
