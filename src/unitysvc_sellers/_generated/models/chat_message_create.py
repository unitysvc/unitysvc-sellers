from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.chat_message_create_attachments_type_0_item import ChatMessageCreateAttachmentsType0Item





T = TypeVar("T", bound="ChatMessageCreate")



@_attrs_define
class ChatMessageCreate:
    """ Schema for creating a message.

     """

    content: str
    attachments: list[ChatMessageCreateAttachmentsType0Item] | None | Unset = UNSET
    is_internal: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.chat_message_create_attachments_type_0_item import ChatMessageCreateAttachmentsType0Item
        content = self.content

        attachments: list[dict[str, Any]] | None | Unset
        if isinstance(self.attachments, Unset):
            attachments = UNSET
        elif isinstance(self.attachments, list):
            attachments = []
            for attachments_type_0_item_data in self.attachments:
                attachments_type_0_item = attachments_type_0_item_data.to_dict()
                attachments.append(attachments_type_0_item)


        else:
            attachments = self.attachments

        is_internal = self.is_internal


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "content": content,
        })
        if attachments is not UNSET:
            field_dict["attachments"] = attachments
        if is_internal is not UNSET:
            field_dict["is_internal"] = is_internal

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_message_create_attachments_type_0_item import ChatMessageCreateAttachmentsType0Item
        d = dict(src_dict)
        content = d.pop("content")

        def _parse_attachments(data: object) -> list[ChatMessageCreateAttachmentsType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                attachments_type_0 = []
                _attachments_type_0 = data
                for attachments_type_0_item_data in (_attachments_type_0):
                    attachments_type_0_item = ChatMessageCreateAttachmentsType0Item.from_dict(attachments_type_0_item_data)



                    attachments_type_0.append(attachments_type_0_item)

                return attachments_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ChatMessageCreateAttachmentsType0Item] | None | Unset, data)

        attachments = _parse_attachments(d.pop("attachments", UNSET))


        is_internal = d.pop("is_internal", UNSET)

        chat_message_create = cls(
            content=content,
            attachments=attachments,
            is_internal=is_internal,
        )


        chat_message_create.additional_properties = d
        return chat_message_create

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
