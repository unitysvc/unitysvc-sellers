from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomSummary")


@_attrs_define
class RoomSummary:
    """A room the account is in, and the account's place in it."""

    id: UUID
    member_id: UUID
    kind: str
    name: str
    handle: str
    status: str
    role: str
    created_at: datetime.datetime
    description: str | Unset = ""
    owner_name: None | str | Unset = UNSET
    retention_seconds: int | None | Unset = UNSET
    """ Effective message retention; null when kept indefinitely """
    max_retention_seconds: int | None | Unset = UNSET
    """ The kind's longest retention; null when it has none """
    keep_forever: bool | Unset = False
    owner_sets_retention: bool | Unset = True
    fixed_membership: bool | Unset = False
    invitable: bool | Unset = False
    can_manage: bool | Unset = False
    status_changed_at: datetime.datetime | None | Unset = UNSET
    pause_message: None | str | Unset = UNSET
    last_message_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        member_id = str(self.member_id)

        kind = self.kind

        name = self.name

        handle = self.handle

        status = self.status

        role = self.role

        created_at = self.created_at.isoformat()

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

        max_retention_seconds: int | None | Unset
        if isinstance(self.max_retention_seconds, Unset):
            max_retention_seconds = UNSET
        else:
            max_retention_seconds = self.max_retention_seconds

        keep_forever = self.keep_forever

        owner_sets_retention = self.owner_sets_retention

        fixed_membership = self.fixed_membership

        invitable = self.invitable

        can_manage = self.can_manage

        status_changed_at: None | str | Unset
        if isinstance(self.status_changed_at, Unset):
            status_changed_at = UNSET
        elif isinstance(self.status_changed_at, datetime.datetime):
            status_changed_at = self.status_changed_at.isoformat()
        else:
            status_changed_at = self.status_changed_at

        pause_message: None | str | Unset
        if isinstance(self.pause_message, Unset):
            pause_message = UNSET
        else:
            pause_message = self.pause_message

        last_message_at: None | str | Unset
        if isinstance(self.last_message_at, Unset):
            last_message_at = UNSET
        elif isinstance(self.last_message_at, datetime.datetime):
            last_message_at = self.last_message_at.isoformat()
        else:
            last_message_at = self.last_message_at

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
                "created_at": created_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if owner_name is not UNSET:
            field_dict["owner_name"] = owner_name
        if retention_seconds is not UNSET:
            field_dict["retention_seconds"] = retention_seconds
        if max_retention_seconds is not UNSET:
            field_dict["max_retention_seconds"] = max_retention_seconds
        if keep_forever is not UNSET:
            field_dict["keep_forever"] = keep_forever
        if owner_sets_retention is not UNSET:
            field_dict["owner_sets_retention"] = owner_sets_retention
        if fixed_membership is not UNSET:
            field_dict["fixed_membership"] = fixed_membership
        if invitable is not UNSET:
            field_dict["invitable"] = invitable
        if can_manage is not UNSET:
            field_dict["can_manage"] = can_manage
        if status_changed_at is not UNSET:
            field_dict["status_changed_at"] = status_changed_at
        if pause_message is not UNSET:
            field_dict["pause_message"] = pause_message
        if last_message_at is not UNSET:
            field_dict["last_message_at"] = last_message_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        member_id = UUID(d.pop("member_id"))

        kind = d.pop("kind")

        name = d.pop("name")

        handle = d.pop("handle")

        status = d.pop("status")

        role = d.pop("role")

        created_at = isoparse(d.pop("created_at"))

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

        def _parse_max_retention_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_retention_seconds = _parse_max_retention_seconds(d.pop("max_retention_seconds", UNSET))

        keep_forever = d.pop("keep_forever", UNSET)

        owner_sets_retention = d.pop("owner_sets_retention", UNSET)

        fixed_membership = d.pop("fixed_membership", UNSET)

        invitable = d.pop("invitable", UNSET)

        can_manage = d.pop("can_manage", UNSET)

        def _parse_status_changed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_changed_at_type_0 = isoparse(data)

                return status_changed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        status_changed_at = _parse_status_changed_at(d.pop("status_changed_at", UNSET))

        def _parse_pause_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pause_message = _parse_pause_message(d.pop("pause_message", UNSET))

        def _parse_last_message_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_message_at_type_0 = isoparse(data)

                return last_message_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_message_at = _parse_last_message_at(d.pop("last_message_at", UNSET))

        room_summary = cls(
            id=id,
            member_id=member_id,
            kind=kind,
            name=name,
            handle=handle,
            status=status,
            role=role,
            created_at=created_at,
            description=description,
            owner_name=owner_name,
            retention_seconds=retention_seconds,
            max_retention_seconds=max_retention_seconds,
            keep_forever=keep_forever,
            owner_sets_retention=owner_sets_retention,
            fixed_membership=fixed_membership,
            invitable=invitable,
            can_manage=can_manage,
            status_changed_at=status_changed_at,
            pause_message=pause_message,
            last_message_at=last_message_at,
        )

        room_summary.additional_properties = d
        return room_summary

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
