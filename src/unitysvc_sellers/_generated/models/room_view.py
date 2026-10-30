from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.room_message_page import RoomMessagePage


T = TypeVar("T", bound="RoomView")


@_attrs_define
class RoomView:
    id: UUID
    member_id: UUID
    kind: str
    name: str
    handle: str
    status: str
    role: str
    messages: RoomMessagePage
    description: str | Unset = ""
    owner_name: None | str | Unset = UNSET
    retention_seconds: int | None | Unset = UNSET
    """ Effective message retention; null when kept forever """
    keep_forever: bool | Unset = False
    permanent: bool | Unset = False
    fixed_membership: bool | Unset = False
    invitable: bool | Unset = False
    can_manage: bool | Unset = False
    expires_at: datetime.datetime | None | Unset = UNSET
    idle_expiry_seconds: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        member_id = str(self.member_id)

        kind = self.kind

        name = self.name

        handle = self.handle

        status = self.status

        role = self.role

        messages = self.messages.to_dict()

        description = self.description

        owner_name: None | str | Unset
        if isinstance(self.owner_name, Unset):
            owner_name = UNSET
        else:
            owner_name = self.owner_name

        retention_seconds: int | None | Unset
        if isinstance(self.retention_seconds, Unset):
            retention_seconds = UNSET
        else:
            retention_seconds = self.retention_seconds

        keep_forever = self.keep_forever

        permanent = self.permanent

        fixed_membership = self.fixed_membership

        invitable = self.invitable

        can_manage = self.can_manage

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        idle_expiry_seconds: int | None | Unset
        if isinstance(self.idle_expiry_seconds, Unset):
            idle_expiry_seconds = UNSET
        else:
            idle_expiry_seconds = self.idle_expiry_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "member_id": member_id,
                "kind": kind,
                "name": name,
                "handle": handle,
                "status": status,
                "role": role,
                "messages": messages,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if owner_name is not UNSET:
            field_dict["owner_name"] = owner_name
        if retention_seconds is not UNSET:
            field_dict["retention_seconds"] = retention_seconds
        if keep_forever is not UNSET:
            field_dict["keep_forever"] = keep_forever
        if permanent is not UNSET:
            field_dict["permanent"] = permanent
        if fixed_membership is not UNSET:
            field_dict["fixed_membership"] = fixed_membership
        if invitable is not UNSET:
            field_dict["invitable"] = invitable
        if can_manage is not UNSET:
            field_dict["can_manage"] = can_manage
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if idle_expiry_seconds is not UNSET:
            field_dict["idle_expiry_seconds"] = idle_expiry_seconds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.room_message_page import RoomMessagePage

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        member_id = UUID(d.pop("member_id"))

        kind = d.pop("kind")

        name = d.pop("name")

        handle = d.pop("handle")

        status = d.pop("status")

        role = d.pop("role")

        messages = RoomMessagePage.from_dict(d.pop("messages"))

        description = d.pop("description", UNSET)

        def _parse_owner_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        owner_name = _parse_owner_name(d.pop("owner_name", UNSET))

        def _parse_retention_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        retention_seconds = _parse_retention_seconds(d.pop("retention_seconds", UNSET))

        keep_forever = d.pop("keep_forever", UNSET)

        permanent = d.pop("permanent", UNSET)

        fixed_membership = d.pop("fixed_membership", UNSET)

        invitable = d.pop("invitable", UNSET)

        can_manage = d.pop("can_manage", UNSET)

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

        def _parse_idle_expiry_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        idle_expiry_seconds = _parse_idle_expiry_seconds(d.pop("idle_expiry_seconds", UNSET))

        room_view = cls(
            id=id,
            member_id=member_id,
            kind=kind,
            name=name,
            handle=handle,
            status=status,
            role=role,
            messages=messages,
            description=description,
            owner_name=owner_name,
            retention_seconds=retention_seconds,
            keep_forever=keep_forever,
            permanent=permanent,
            fixed_membership=fixed_membership,
            invitable=invitable,
            can_manage=can_manage,
            expires_at=expires_at,
            idle_expiry_seconds=idle_expiry_seconds,
        )

        room_view.additional_properties = d
        return room_view

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
