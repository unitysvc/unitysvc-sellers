from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.conversation_status_enum import check_conversation_status_enum
from ..models.conversation_status_enum import ConversationStatusEnum
from ..models.conversation_type_enum import check_conversation_type_enum
from ..models.conversation_type_enum import ConversationTypeEnum
from ..models.dispute_reason_enum import check_dispute_reason_enum
from ..models.dispute_reason_enum import DisputeReasonEnum
from ..models.dispute_status_enum import check_dispute_status_enum
from ..models.dispute_status_enum import DisputeStatusEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="ConversationPublic")



@_attrs_define
class ConversationPublic:
    """ Public conversation for API responses.

     """

    id: UUID
    customer_id: None | UUID
    seller_id: None | UUID
    is_admin_participant: bool
    assigned_admin_id: None | UUID
    type_: ConversationTypeEnum
    """ Type of conversation. """
    status: ConversationStatusEnum
    """ Status of a conversation. """
    subject: str
    related_entity_type: None | str
    related_entity_id: None | UUID
    dispute_status: DisputeStatusEnum | None
    dispute_reason: DisputeReasonEnum | None
    dispute_resolution: None | str
    dispute_resolved_at: datetime.datetime | None
    last_message_at: datetime.datetime | None
    last_message_preview: None | str
    unread_count_customer: int
    unread_count_seller: int
    unread_count_admin: int
    tags: list[str] | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    customer_name: None | str | Unset = UNSET
    seller_name: None | str | Unset = UNSET
    assigned_admin_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        customer_id: None | str
        if isinstance(self.customer_id, UUID):
            customer_id = str(self.customer_id)
        else:
            customer_id = self.customer_id

        seller_id: None | str
        if isinstance(self.seller_id, UUID):
            seller_id = str(self.seller_id)
        else:
            seller_id = self.seller_id

        is_admin_participant = self.is_admin_participant

        assigned_admin_id: None | str
        if isinstance(self.assigned_admin_id, UUID):
            assigned_admin_id = str(self.assigned_admin_id)
        else:
            assigned_admin_id = self.assigned_admin_id

        type_: str = self.type_

        status: str = self.status

        subject = self.subject

        related_entity_type: None | str
        related_entity_type = self.related_entity_type

        related_entity_id: None | str
        if isinstance(self.related_entity_id, UUID):
            related_entity_id = str(self.related_entity_id)
        else:
            related_entity_id = self.related_entity_id

        dispute_status: None | str
        if isinstance(self.dispute_status, str):
            dispute_status = self.dispute_status
        else:
            dispute_status = self.dispute_status

        dispute_reason: None | str
        if isinstance(self.dispute_reason, str):
            dispute_reason = self.dispute_reason
        else:
            dispute_reason = self.dispute_reason

        dispute_resolution: None | str
        dispute_resolution = self.dispute_resolution

        dispute_resolved_at: None | str
        if isinstance(self.dispute_resolved_at, datetime.datetime):
            dispute_resolved_at = self.dispute_resolved_at.isoformat()
        else:
            dispute_resolved_at = self.dispute_resolved_at

        last_message_at: None | str
        if isinstance(self.last_message_at, datetime.datetime):
            last_message_at = self.last_message_at.isoformat()
        else:
            last_message_at = self.last_message_at

        last_message_preview: None | str
        last_message_preview = self.last_message_preview

        unread_count_customer = self.unread_count_customer

        unread_count_seller = self.unread_count_seller

        unread_count_admin = self.unread_count_admin

        tags: list[str] | None
        if isinstance(self.tags, list):
            tags = self.tags


        else:
            tags = self.tags

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        customer_name: None | str | Unset
        if isinstance(self.customer_name, Unset):
            customer_name = UNSET
        else:
            customer_name = self.customer_name

        seller_name: None | str | Unset
        if isinstance(self.seller_name, Unset):
            seller_name = UNSET
        else:
            seller_name = self.seller_name

        assigned_admin_name: None | str | Unset
        if isinstance(self.assigned_admin_name, Unset):
            assigned_admin_name = UNSET
        else:
            assigned_admin_name = self.assigned_admin_name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "customer_id": customer_id,
            "seller_id": seller_id,
            "is_admin_participant": is_admin_participant,
            "assigned_admin_id": assigned_admin_id,
            "type": type_,
            "status": status,
            "subject": subject,
            "related_entity_type": related_entity_type,
            "related_entity_id": related_entity_id,
            "dispute_status": dispute_status,
            "dispute_reason": dispute_reason,
            "dispute_resolution": dispute_resolution,
            "dispute_resolved_at": dispute_resolved_at,
            "last_message_at": last_message_at,
            "last_message_preview": last_message_preview,
            "unread_count_customer": unread_count_customer,
            "unread_count_seller": unread_count_seller,
            "unread_count_admin": unread_count_admin,
            "tags": tags,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if customer_name is not UNSET:
            field_dict["customer_name"] = customer_name
        if seller_name is not UNSET:
            field_dict["seller_name"] = seller_name
        if assigned_admin_name is not UNSET:
            field_dict["assigned_admin_name"] = assigned_admin_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        def _parse_customer_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                customer_id_type_0 = UUID(data)



                return customer_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        customer_id = _parse_customer_id(d.pop("customer_id"))


        def _parse_seller_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                seller_id_type_0 = UUID(data)



                return seller_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        seller_id = _parse_seller_id(d.pop("seller_id"))


        is_admin_participant = d.pop("is_admin_participant")

        def _parse_assigned_admin_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                assigned_admin_id_type_0 = UUID(data)



                return assigned_admin_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        assigned_admin_id = _parse_assigned_admin_id(d.pop("assigned_admin_id"))


        type_ = check_conversation_type_enum(d.pop("type"))




        status = check_conversation_status_enum(d.pop("status"))




        subject = d.pop("subject")

        def _parse_related_entity_type(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        related_entity_type = _parse_related_entity_type(d.pop("related_entity_type"))


        def _parse_related_entity_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                related_entity_id_type_0 = UUID(data)



                return related_entity_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        related_entity_id = _parse_related_entity_id(d.pop("related_entity_id"))


        def _parse_dispute_status(data: object) -> DisputeStatusEnum | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                dispute_status_type_0 = check_dispute_status_enum(data)



                return dispute_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DisputeStatusEnum | None, data)

        dispute_status = _parse_dispute_status(d.pop("dispute_status"))


        def _parse_dispute_reason(data: object) -> DisputeReasonEnum | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                dispute_reason_type_0 = check_dispute_reason_enum(data)



                return dispute_reason_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DisputeReasonEnum | None, data)

        dispute_reason = _parse_dispute_reason(d.pop("dispute_reason"))


        def _parse_dispute_resolution(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        dispute_resolution = _parse_dispute_resolution(d.pop("dispute_resolution"))


        def _parse_dispute_resolved_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                dispute_resolved_at_type_0 = isoparse(data)



                return dispute_resolved_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        dispute_resolved_at = _parse_dispute_resolved_at(d.pop("dispute_resolved_at"))


        def _parse_last_message_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_message_at_type_0 = isoparse(data)



                return last_message_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        last_message_at = _parse_last_message_at(d.pop("last_message_at"))


        def _parse_last_message_preview(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_message_preview = _parse_last_message_preview(d.pop("last_message_preview"))


        unread_count_customer = d.pop("unread_count_customer")

        unread_count_seller = d.pop("unread_count_seller")

        unread_count_admin = d.pop("unread_count_admin")

        def _parse_tags(data: object) -> list[str] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = cast(list[str], data)

                return tags_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None, data)

        tags = _parse_tags(d.pop("tags"))


        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        def _parse_customer_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        customer_name = _parse_customer_name(d.pop("customer_name", UNSET))


        def _parse_seller_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        seller_name = _parse_seller_name(d.pop("seller_name", UNSET))


        def _parse_assigned_admin_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        assigned_admin_name = _parse_assigned_admin_name(d.pop("assigned_admin_name", UNSET))


        conversation_public = cls(
            id=id,
            customer_id=customer_id,
            seller_id=seller_id,
            is_admin_participant=is_admin_participant,
            assigned_admin_id=assigned_admin_id,
            type_=type_,
            status=status,
            subject=subject,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            dispute_status=dispute_status,
            dispute_reason=dispute_reason,
            dispute_resolution=dispute_resolution,
            dispute_resolved_at=dispute_resolved_at,
            last_message_at=last_message_at,
            last_message_preview=last_message_preview,
            unread_count_customer=unread_count_customer,
            unread_count_seller=unread_count_seller,
            unread_count_admin=unread_count_admin,
            tags=tags,
            created_at=created_at,
            updated_at=updated_at,
            customer_name=customer_name,
            seller_name=seller_name,
            assigned_admin_name=assigned_admin_name,
        )


        conversation_public.additional_properties = d
        return conversation_public

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
