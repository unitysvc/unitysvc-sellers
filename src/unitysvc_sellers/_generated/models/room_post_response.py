from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.room_post_response_routed import RoomPostResponseRouted, check_room_post_response_routed
from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomPostResponse")


@_attrs_define
class RoomPostResponse:
    room_id: UUID
    message_id: UUID
    offset: int
    routed: RoomPostResponseRouted
    reason: None | str | Unset = UNSET
    duplicate: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        room_id = str(self.room_id)

        message_id = str(self.message_id)

        offset = self.offset

        routed: str = self.routed

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        duplicate = self.duplicate

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "room_id": room_id,
                "message_id": message_id,
                "offset": offset,
                "routed": routed,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason
        if duplicate is not UNSET:
            field_dict["duplicate"] = duplicate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        room_id = UUID(d.pop("room_id"))

        message_id = UUID(d.pop("message_id"))

        offset = d.pop("offset")

        routed = check_room_post_response_routed(d.pop("routed"))

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        duplicate = d.pop("duplicate", UNSET)

        room_post_response = cls(
            room_id=room_id,
            message_id=message_id,
            offset=offset,
            routed=routed,
            reason=reason,
            duplicate=duplicate,
        )

        room_post_response.additional_properties = d
        return room_post_response

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
