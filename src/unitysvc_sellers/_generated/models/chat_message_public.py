from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.chat_message_public_attachments_type_0_item import ChatMessagePublicAttachmentsType0Item





T = TypeVar("T", bound="ChatMessagePublic")



@_attrs_define
class ChatMessagePublic:
    """ Public message for API responses.

     """

    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    attachments: list[ChatMessagePublicAttachmentsType0Item] | None
    is_internal: bool
    is_system: bool
    created_at: datetime.datetime
    sender_name: None | str | Unset = UNSET
    sender_role: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.chat_message_public_attachments_type_0_item import ChatMessagePublicAttachmentsType0Item
        id = str(self.id)

        conversation_id = str(self.conversation_id)

        sender_id = str(self.sender_id)

        content = self.content

        attachments: list[dict[str, Any]] | None
        if isinstance(self.attachments, list):
            attachments = []
            for attachments_type_0_item_data in self.attachments:
                attachments_type_0_item = attachments_type_0_item_data.to_dict()
                attachments.append(attachments_type_0_item)


        else:
            attachments = self.attachments

        is_internal = self.is_internal

        is_system = self.is_system

        created_at = self.created_at.isoformat()

        sender_name: None | str | Unset
        if isinstance(self.sender_name, Unset):
            sender_name = UNSET
        else:
            sender_name = self.sender_name

        sender_role: None | str | Unset
        if isinstance(self.sender_role, Unset):
            sender_role = UNSET
        else:
            sender_role = self.sender_role


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "conversation_id": conversation_id,
            "sender_id": sender_id,
            "content": content,
            "attachments": attachments,
            "is_internal": is_internal,
            "is_system": is_system,
            "created_at": created_at,
        })
        if sender_name is not UNSET:
            field_dict["sender_name"] = sender_name
        if sender_role is not UNSET:
            field_dict["sender_role"] = sender_role

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_message_public_attachments_type_0_item import ChatMessagePublicAttachmentsType0Item
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        conversation_id = UUID(d.pop("conversation_id"))




        sender_id = UUID(d.pop("sender_id"))




        content = d.pop("content")

        def _parse_attachments(data: object) -> list[ChatMessagePublicAttachmentsType0Item] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                attachments_type_0 = []
                _attachments_type_0 = data
                for attachments_type_0_item_data in (_attachments_type_0):
                    attachments_type_0_item = ChatMessagePublicAttachmentsType0Item.from_dict(attachments_type_0_item_data)



                    attachments_type_0.append(attachments_type_0_item)

                return attachments_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ChatMessagePublicAttachmentsType0Item] | None, data)

        attachments = _parse_attachments(d.pop("attachments"))


        is_internal = d.pop("is_internal")

        is_system = d.pop("is_system")

        created_at = isoparse(d.pop("created_at"))




        def _parse_sender_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sender_name = _parse_sender_name(d.pop("sender_name", UNSET))


        def _parse_sender_role(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sender_role = _parse_sender_role(d.pop("sender_role", UNSET))


        chat_message_public = cls(
            id=id,
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            attachments=attachments,
            is_internal=is_internal,
            is_system=is_system,
            created_at=created_at,
            sender_name=sender_name,
            sender_role=sender_role,
        )


        chat_message_public.additional_properties = d
        return chat_message_public

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
