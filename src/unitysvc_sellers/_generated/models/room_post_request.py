from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.msg_format_enum import MsgFormatEnum, check_msg_format_enum
from ..models.msg_type_enum import MsgTypeEnum, check_msg_type_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.room_post_origin import RoomPostOrigin
    from ..models.room_post_request_links_item import RoomPostRequestLinksItem


T = TypeVar("T", bound="RoomPostRequest")


@_attrs_define
class RoomPostRequest:
    """A message in the msg format."""

    body: str
    title: None | str | Unset = UNSET
    format_: MsgFormatEnum | Unset = UNSET
    """ The msg envelope's ``format`` (``html`` is deprecated). """
    type_: MsgTypeEnum | Unset = UNSET
    """ The msg envelope's ``type`` (notification-services.md §4). """
    links: list[RoomPostRequestLinksItem] | Unset = UNSET
    origin: None | RoomPostOrigin | Unset = UNSET
    client_message_id: None | str | Unset = UNSET
    """ Idempotency key: retries with the same id post once. Defaults to origin.external_id. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.room_post_origin import RoomPostOrigin

        body = self.body

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        format_: str | Unset = UNSET
        if not isinstance(self.format_, Unset):
            format_ = self.format_

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_

        links: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.links, Unset):
            links = []
            for links_item_data in self.links:
                links_item = links_item_data.to_dict()
                links.append(links_item)

        origin: dict[str, Any] | None | Unset
        if isinstance(self.origin, Unset):
            origin = UNSET
        elif isinstance(self.origin, RoomPostOrigin):
            origin = self.origin.to_dict()
        else:
            origin = self.origin

        client_message_id: None | str | Unset
        if isinstance(self.client_message_id, Unset):
            client_message_id = UNSET
        else:
            client_message_id = self.client_message_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "body": body,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if format_ is not UNSET:
            field_dict["format"] = format_
        if type_ is not UNSET:
            field_dict["type"] = type_
        if links is not UNSET:
            field_dict["links"] = links
        if origin is not UNSET:
            field_dict["origin"] = origin
        if client_message_id is not UNSET:
            field_dict["client_message_id"] = client_message_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.room_post_origin import RoomPostOrigin
        from ..models.room_post_request_links_item import RoomPostRequestLinksItem

        d = dict(src_dict)
        body = d.pop("body")

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        _format_ = d.pop("format", UNSET)
        format_: MsgFormatEnum | Unset
        if isinstance(_format_, Unset):
            format_ = UNSET
        else:
            format_ = check_msg_format_enum(_format_)

        _type_ = d.pop("type", UNSET)
        type_: MsgTypeEnum | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = check_msg_type_enum(_type_)

        _links = d.pop("links", UNSET)
        links: list[RoomPostRequestLinksItem] | Unset = UNSET
        if _links is not UNSET:
            links = []
            for links_item_data in _links:
                links_item = RoomPostRequestLinksItem.from_dict(links_item_data)

                links.append(links_item)

        def _parse_origin(data: object) -> None | RoomPostOrigin | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                origin_type_0 = RoomPostOrigin.from_dict(data)

                return origin_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RoomPostOrigin | Unset, data)

        origin = _parse_origin(d.pop("origin", UNSET))

        def _parse_client_message_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        client_message_id = _parse_client_message_id(d.pop("client_message_id", UNSET))

        room_post_request = cls(
            body=body,
            title=title,
            format_=format_,
            type_=type_,
            links=links,
            origin=origin,
            client_message_id=client_message_id,
        )

        room_post_request.additional_properties = d
        return room_post_request

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
