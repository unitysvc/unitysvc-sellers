from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.conversation_type_enum import check_conversation_type_enum
from ..models.conversation_type_enum import ConversationTypeEnum
from ..models.dispute_reason_enum import check_dispute_reason_enum
from ..models.dispute_reason_enum import DisputeReasonEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID






T = TypeVar("T", bound="ConversationCreate")



@_attrs_define
class ConversationCreate:
    """ Schema for creating a conversation.

     """

    subject: str
    initial_message: str
    """ First message content """
    customer_id: None | Unset | UUID = UNSET
    seller_id: None | Unset | UUID = UNSET
    is_admin_participant: bool | Unset = False
    assigned_admin_id: None | Unset | UUID = UNSET
    type_: ConversationTypeEnum | Unset = UNSET
    """ Type of conversation. """
    related_entity_type: None | str | Unset = UNSET
    related_entity_id: None | Unset | UUID = UNSET
    dispute_reason: DisputeReasonEnum | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        subject = self.subject

        initial_message = self.initial_message

        customer_id: None | str | Unset
        if isinstance(self.customer_id, Unset):
            customer_id = UNSET
        elif isinstance(self.customer_id, UUID):
            customer_id = str(self.customer_id)
        else:
            customer_id = self.customer_id

        seller_id: None | str | Unset
        if isinstance(self.seller_id, Unset):
            seller_id = UNSET
        elif isinstance(self.seller_id, UUID):
            seller_id = str(self.seller_id)
        else:
            seller_id = self.seller_id

        is_admin_participant = self.is_admin_participant

        assigned_admin_id: None | str | Unset
        if isinstance(self.assigned_admin_id, Unset):
            assigned_admin_id = UNSET
        elif isinstance(self.assigned_admin_id, UUID):
            assigned_admin_id = str(self.assigned_admin_id)
        else:
            assigned_admin_id = self.assigned_admin_id

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_


        related_entity_type: None | str | Unset
        if isinstance(self.related_entity_type, Unset):
            related_entity_type = UNSET
        else:
            related_entity_type = self.related_entity_type

        related_entity_id: None | str | Unset
        if isinstance(self.related_entity_id, Unset):
            related_entity_id = UNSET
        elif isinstance(self.related_entity_id, UUID):
            related_entity_id = str(self.related_entity_id)
        else:
            related_entity_id = self.related_entity_id

        dispute_reason: None | str | Unset
        if isinstance(self.dispute_reason, Unset):
            dispute_reason = UNSET
        elif isinstance(self.dispute_reason, str):
            dispute_reason = self.dispute_reason
        else:
            dispute_reason = self.dispute_reason


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "subject": subject,
            "initial_message": initial_message,
        })
        if customer_id is not UNSET:
            field_dict["customer_id"] = customer_id
        if seller_id is not UNSET:
            field_dict["seller_id"] = seller_id
        if is_admin_participant is not UNSET:
            field_dict["is_admin_participant"] = is_admin_participant
        if assigned_admin_id is not UNSET:
            field_dict["assigned_admin_id"] = assigned_admin_id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if related_entity_type is not UNSET:
            field_dict["related_entity_type"] = related_entity_type
        if related_entity_id is not UNSET:
            field_dict["related_entity_id"] = related_entity_id
        if dispute_reason is not UNSET:
            field_dict["dispute_reason"] = dispute_reason

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        subject = d.pop("subject")

        initial_message = d.pop("initial_message")

        def _parse_customer_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                customer_id_type_0 = UUID(data)



                return customer_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        customer_id = _parse_customer_id(d.pop("customer_id", UNSET))


        def _parse_seller_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                seller_id_type_0 = UUID(data)



                return seller_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        seller_id = _parse_seller_id(d.pop("seller_id", UNSET))


        is_admin_participant = d.pop("is_admin_participant", UNSET)

        def _parse_assigned_admin_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                assigned_admin_id_type_0 = UUID(data)



                return assigned_admin_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        assigned_admin_id = _parse_assigned_admin_id(d.pop("assigned_admin_id", UNSET))


        _type_ = d.pop("type", UNSET)
        type_: ConversationTypeEnum | Unset
        if isinstance(_type_,  Unset):
            type_ = UNSET
        else:
            type_ = check_conversation_type_enum(_type_)




        def _parse_related_entity_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        related_entity_type = _parse_related_entity_type(d.pop("related_entity_type", UNSET))


        def _parse_related_entity_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                related_entity_id_type_0 = UUID(data)



                return related_entity_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        related_entity_id = _parse_related_entity_id(d.pop("related_entity_id", UNSET))


        def _parse_dispute_reason(data: object) -> DisputeReasonEnum | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                dispute_reason_type_0 = check_dispute_reason_enum(data)



                return dispute_reason_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DisputeReasonEnum | None | Unset, data)

        dispute_reason = _parse_dispute_reason(d.pop("dispute_reason", UNSET))


        conversation_create = cls(
            subject=subject,
            initial_message=initial_message,
            customer_id=customer_id,
            seller_id=seller_id,
            is_admin_participant=is_admin_participant,
            assigned_admin_id=assigned_admin_id,
            type_=type_,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            dispute_reason=dispute_reason,
        )


        conversation_create.additional_properties = d
        return conversation_create

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
