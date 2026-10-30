from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.room_message_view import RoomMessageView


T = TypeVar("T", bound="RoomMessagePage")


@_attrs_define
class RoomMessagePage:
    data: list[RoomMessageView]
    next_: int | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        next_: int | None
        next_ = self.next_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "next": next_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.room_message_view import RoomMessageView

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = RoomMessageView.from_dict(data_item_data)

            data.append(data_item)

        def _parse_next_(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        next_ = _parse_next_(d.pop("next"))

        room_message_page = cls(
            data=data,
            next_=next_,
        )

        room_message_page.additional_properties = d
        return room_message_page

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
