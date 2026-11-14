from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="LiveWaitingRoom")


@_attrs_define
class LiveWaitingRoom:
    room_id: UUID
    handle: str
    generation: str
    first_requested_at: datetime.datetime
    requesters: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        room_id = str(self.room_id)

        handle = self.handle

        generation = self.generation

        first_requested_at = self.first_requested_at.isoformat()

        requesters = self.requesters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "room_id": room_id,
                "handle": handle,
                "generation": generation,
                "first_requested_at": first_requested_at,
                "requesters": requesters,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        room_id = UUID(d.pop("room_id"))

        handle = d.pop("handle")

        generation = d.pop("generation")

        first_requested_at = isoparse(d.pop("first_requested_at"))

        requesters = d.pop("requesters")

        live_waiting_room = cls(
            room_id=room_id,
            handle=handle,
            generation=generation,
            first_requested_at=first_requested_at,
            requesters=requesters,
        )

        live_waiting_room.additional_properties = d
        return live_waiting_room

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
