from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.notification_category_enum import check_notification_category_enum
from ..models.notification_category_enum import NotificationCategoryEnum
from ..models.notification_source_type_enum import check_notification_source_type_enum
from ..models.notification_source_type_enum import NotificationSourceTypeEnum
from ..models.notification_type_enum import check_notification_type_enum
from ..models.notification_type_enum import NotificationTypeEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.notification_public_actions_type_0_item import NotificationPublicActionsType0Item
  from ..models.notification_public_event_metadata_type_0 import NotificationPublicEventMetadataType0





T = TypeVar("T", bound="NotificationPublic")



@_attrs_define
class NotificationPublic:
    """ Public notification for API responses.

     """

    recipient_user_id: UUID
    """ User who receives this notification """
    category: NotificationCategoryEnum
    """ Categorization for filtering and preferences. """
    title: str
    """ Notification title """
    message: str
    """ Notification message body (plain text only) """
    id: UUID
    created_at: datetime.datetime
    type_: NotificationTypeEnum | Unset = UNSET
    """ Visual style of notification. """
    link: None | str | Unset = UNSET
    """ Fallback link for simple notifications (overridden by actions if present) """
    actions: list[NotificationPublicActionsType0Item] | None | Unset = UNSET
    """ Action buttons (e.g., 'Pay Now', 'View Details'). Overrides link if present. """
    source_entity_type: None | NotificationSourceTypeEnum | Unset = UNSET
    """ Type of entity that created notification. NULL for system-generated notifications. """
    source_entity_id: None | Unset | UUID = UNSET
    """ ID of entity that created notification. NULL for system-generated notifications. """
    read_at: datetime.datetime | None | Unset = UNSET
    """ When notification was marked as read. NULL = unread, NOT NULL = read. """
    expires_at: datetime.datetime | None | Unset = UNSET
    """ Optional expiration (for temporary notifications) """
    event_metadata: None | NotificationPublicEventMetadataType0 | Unset = UNSET
    """ Optional structured data (IDs, counts, etc.) """





    def to_dict(self) -> dict[str, Any]:
        from ..models.notification_public_actions_type_0_item import NotificationPublicActionsType0Item
        from ..models.notification_public_event_metadata_type_0 import NotificationPublicEventMetadataType0
        recipient_user_id = str(self.recipient_user_id)

        category: str = self.category

        title = self.title

        message = self.message

        id = str(self.id)

        created_at = self.created_at.isoformat()

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_


        link: None | str | Unset
        if isinstance(self.link, Unset):
            link = UNSET
        else:
            link = self.link

        actions: list[dict[str, Any]] | None | Unset
        if isinstance(self.actions, Unset):
            actions = UNSET
        elif isinstance(self.actions, list):
            actions = []
            for actions_type_0_item_data in self.actions:
                actions_type_0_item = actions_type_0_item_data.to_dict()
                actions.append(actions_type_0_item)


        else:
            actions = self.actions

        source_entity_type: None | str | Unset
        if isinstance(self.source_entity_type, Unset):
            source_entity_type = UNSET
        elif isinstance(self.source_entity_type, str):
            source_entity_type = self.source_entity_type
        else:
            source_entity_type = self.source_entity_type

        source_entity_id: None | str | Unset
        if isinstance(self.source_entity_id, Unset):
            source_entity_id = UNSET
        elif isinstance(self.source_entity_id, UUID):
            source_entity_id = str(self.source_entity_id)
        else:
            source_entity_id = self.source_entity_id

        read_at: None | str | Unset
        if isinstance(self.read_at, Unset):
            read_at = UNSET
        elif isinstance(self.read_at, datetime.datetime):
            read_at = self.read_at.isoformat()
        else:
            read_at = self.read_at

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        event_metadata: dict[str, Any] | None | Unset
        if isinstance(self.event_metadata, Unset):
            event_metadata = UNSET
        elif isinstance(self.event_metadata, NotificationPublicEventMetadataType0):
            event_metadata = self.event_metadata.to_dict()
        else:
            event_metadata = self.event_metadata


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "recipient_user_id": recipient_user_id,
            "category": category,
            "title": title,
            "message": message,
            "id": id,
            "created_at": created_at,
        })
        if type_ is not UNSET:
            field_dict["type"] = type_
        if link is not UNSET:
            field_dict["link"] = link
        if actions is not UNSET:
            field_dict["actions"] = actions
        if source_entity_type is not UNSET:
            field_dict["source_entity_type"] = source_entity_type
        if source_entity_id is not UNSET:
            field_dict["source_entity_id"] = source_entity_id
        if read_at is not UNSET:
            field_dict["read_at"] = read_at
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if event_metadata is not UNSET:
            field_dict["event_metadata"] = event_metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.notification_public_actions_type_0_item import NotificationPublicActionsType0Item
        from ..models.notification_public_event_metadata_type_0 import NotificationPublicEventMetadataType0
        d = dict(src_dict)
        recipient_user_id = UUID(d.pop("recipient_user_id"))




        category = check_notification_category_enum(d.pop("category"))




        title = d.pop("title")

        message = d.pop("message")

        id = UUID(d.pop("id"))




        created_at = isoparse(d.pop("created_at"))




        _type_ = d.pop("type", UNSET)
        type_: NotificationTypeEnum | Unset
        if isinstance(_type_,  Unset):
            type_ = UNSET
        else:
            type_ = check_notification_type_enum(_type_)




        def _parse_link(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        link = _parse_link(d.pop("link", UNSET))


        def _parse_actions(data: object) -> list[NotificationPublicActionsType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                actions_type_0 = []
                _actions_type_0 = data
                for actions_type_0_item_data in (_actions_type_0):
                    actions_type_0_item = NotificationPublicActionsType0Item.from_dict(actions_type_0_item_data)



                    actions_type_0.append(actions_type_0_item)

                return actions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[NotificationPublicActionsType0Item] | None | Unset, data)

        actions = _parse_actions(d.pop("actions", UNSET))


        def _parse_source_entity_type(data: object) -> None | NotificationSourceTypeEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                source_entity_type_type_0 = check_notification_source_type_enum(data)



                return source_entity_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | NotificationSourceTypeEnum | Unset, data)

        source_entity_type = _parse_source_entity_type(d.pop("source_entity_type", UNSET))


        def _parse_source_entity_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                source_entity_id_type_0 = UUID(data)



                return source_entity_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        source_entity_id = _parse_source_entity_id(d.pop("source_entity_id", UNSET))


        def _parse_read_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                read_at_type_0 = isoparse(data)



                return read_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        read_at = _parse_read_at(d.pop("read_at", UNSET))


        def _parse_expires_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)



                return expires_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))


        def _parse_event_metadata(data: object) -> None | NotificationPublicEventMetadataType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                event_metadata_type_0 = NotificationPublicEventMetadataType0.from_dict(data)



                return event_metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | NotificationPublicEventMetadataType0 | Unset, data)

        event_metadata = _parse_event_metadata(d.pop("event_metadata", UNSET))


        notification_public = cls(
            recipient_user_id=recipient_user_id,
            category=category,
            title=title,
            message=message,
            id=id,
            created_at=created_at,
            type_=type_,
            link=link,
            actions=actions,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            read_at=read_at,
            expires_at=expires_at,
            event_metadata=event_metadata,
        )

        return notification_public

