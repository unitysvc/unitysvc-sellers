from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.room_feed_message import RoomFeedMessage


T = TypeVar("T", bound="RoomFeed")


@_attrs_define
class RoomFeed:
    """New messages across every room the account can reach (#2885). ``cursor``
    carries the per-room read position; pass it back as ``since``.

    """

    messages: list[RoomFeedMessage]
    cursor: str
    rooms_with_new_activity: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        cursor = self.cursor

        rooms_with_new_activity = self.rooms_with_new_activity

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messages": messages,
                "cursor": cursor,
                "rooms_with_new_activity": rooms_with_new_activity,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.room_feed_message import RoomFeedMessage

        d = dict(src_dict)
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = RoomFeedMessage.from_dict(messages_item_data)

            messages.append(messages_item)

        cursor = d.pop("cursor")

        rooms_with_new_activity = d.pop("rooms_with_new_activity")

        room_feed = cls(
            messages=messages,
            cursor=cursor,
            rooms_with_new_activity=rooms_with_new_activity,
        )

        room_feed.additional_properties = d
        return room_feed

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
