from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.room_message_view_attachments_item import RoomMessageViewAttachmentsItem
    from ..models.room_message_view_event_data_type_0 import RoomMessageViewEventDataType0
    from ..models.room_message_view_links_item import RoomMessageViewLinksItem


T = TypeVar("T", bound="RoomMessageView")


@_attrs_define
class RoomMessageView:
    id: UUID
    offset: int
    sent_at: datetime.datetime
    sender_type: str
    sender_member_id: None | UUID
    sender_name: str
    via: None | str
    origin_service: None | str
    origin_author: None | str
    reply_to_id: None | UUID
    event: None | str
    event_data: None | RoomMessageViewEventDataType0
    title: None | str
    body: str
    type_: str
    format_: str
    links: list[RoomMessageViewLinksItem]
    attachments: list[RoomMessageViewAttachmentsItem]
    is_internal: bool
    is_system: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.room_message_view_event_data_type_0 import RoomMessageViewEventDataType0

        id = str(self.id)

        offset = self.offset

        sent_at = self.sent_at.isoformat()

        sender_type = self.sender_type

        sender_member_id: None | str
        if isinstance(self.sender_member_id, UUID):
            sender_member_id = str(self.sender_member_id)
        else:
            sender_member_id = self.sender_member_id

        sender_name = self.sender_name

        via: None | str
        via = self.via

        origin_service: None | str
        origin_service = self.origin_service

        origin_author: None | str
        origin_author = self.origin_author

        reply_to_id: None | str
        if isinstance(self.reply_to_id, UUID):
            reply_to_id = str(self.reply_to_id)
        else:
            reply_to_id = self.reply_to_id

        event: None | str
        event = self.event

        event_data: dict[str, Any] | None
        if isinstance(self.event_data, RoomMessageViewEventDataType0):
            event_data = self.event_data.to_dict()
        else:
            event_data = self.event_data

        title: None | str
        title = self.title

        body = self.body

        type_ = self.type_

        format_ = self.format_

        links = []
        for links_item_data in self.links:
            links_item = links_item_data.to_dict()
            links.append(links_item)

        attachments = []
        for attachments_item_data in self.attachments:
            attachments_item = attachments_item_data.to_dict()
            attachments.append(attachments_item)

        is_internal = self.is_internal

        is_system = self.is_system

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "offset": offset,
                "sent_at": sent_at,
                "sender_type": sender_type,
                "sender_member_id": sender_member_id,
                "sender_name": sender_name,
                "via": via,
                "origin_service": origin_service,
                "origin_author": origin_author,
                "reply_to_id": reply_to_id,
                "event": event,
                "event_data": event_data,
                "title": title,
                "body": body,
                "type": type_,
                "format": format_,
                "links": links,
                "attachments": attachments,
                "is_internal": is_internal,
                "is_system": is_system,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.room_message_view_attachments_item import RoomMessageViewAttachmentsItem
        from ..models.room_message_view_event_data_type_0 import RoomMessageViewEventDataType0
        from ..models.room_message_view_links_item import RoomMessageViewLinksItem

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        offset = d.pop("offset")

        sent_at = isoparse(d.pop("sent_at"))

        sender_type = d.pop("sender_type")

        def _parse_sender_member_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                sender_member_id_type_0 = UUID(data)

                return sender_member_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        sender_member_id = _parse_sender_member_id(d.pop("sender_member_id"))

        sender_name = d.pop("sender_name")

        def _parse_via(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        via = _parse_via(d.pop("via"))

        def _parse_origin_service(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        origin_service = _parse_origin_service(d.pop("origin_service"))

        def _parse_origin_author(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        origin_author = _parse_origin_author(d.pop("origin_author"))

        def _parse_reply_to_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reply_to_id_type_0 = UUID(data)

                return reply_to_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        reply_to_id = _parse_reply_to_id(d.pop("reply_to_id"))

        def _parse_event(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        event = _parse_event(d.pop("event"))

        def _parse_event_data(data: object) -> None | RoomMessageViewEventDataType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                event_data_type_0 = RoomMessageViewEventDataType0.from_dict(data)

                return event_data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RoomMessageViewEventDataType0, data)

        event_data = _parse_event_data(d.pop("event_data"))

        def _parse_title(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        title = _parse_title(d.pop("title"))

        body = d.pop("body")

        type_ = d.pop("type")

        format_ = d.pop("format")

        links = []
        _links = d.pop("links")
        for links_item_data in _links:
            links_item = RoomMessageViewLinksItem.from_dict(links_item_data)

            links.append(links_item)

        attachments = []
        _attachments = d.pop("attachments")
        for attachments_item_data in _attachments:
            attachments_item = RoomMessageViewAttachmentsItem.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        is_internal = d.pop("is_internal")

        is_system = d.pop("is_system")

        room_message_view = cls(
            id=id,
            offset=offset,
            sent_at=sent_at,
            sender_type=sender_type,
            sender_member_id=sender_member_id,
            sender_name=sender_name,
            via=via,
            origin_service=origin_service,
            origin_author=origin_author,
            reply_to_id=reply_to_id,
            event=event,
            event_data=event_data,
            title=title,
            body=body,
            type_=type_,
            format_=format_,
            links=links,
            attachments=attachments,
            is_internal=is_internal,
            is_system=is_system,
        )

        room_message_view.additional_properties = d
        return room_message_view

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
