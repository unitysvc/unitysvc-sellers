from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="RoomMemberView")


@_attrs_define
class RoomMemberView:
    id: UUID
    account_type: str
    account_id: None | UUID
    name: str
    role: str
    joined_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        account_type = self.account_type

        account_id: None | str
        if isinstance(self.account_id, UUID):
            account_id = str(self.account_id)
        else:
            account_id = self.account_id

        name = self.name

        role = self.role

        joined_at = self.joined_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "account_type": account_type,
                "account_id": account_id,
                "name": name,
                "role": role,
                "joined_at": joined_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        account_type = d.pop("account_type")

        def _parse_account_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                account_id_type_0 = UUID(data)

                return account_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        account_id = _parse_account_id(d.pop("account_id"))

        name = d.pop("name")

        role = d.pop("role")

        joined_at = isoparse(d.pop("joined_at"))

        room_member_view = cls(
            id=id,
            account_type=account_type,
            account_id=account_id,
            name=name,
            role=role,
            joined_at=joined_at,
        )

        room_member_view.additional_properties = d
        return room_member_view

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
