from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomInvitationCode")


@_attrs_define
class RoomInvitationCode:
    id: UUID
    token: str
    role: str
    status: str
    use_count: int
    expires_at: datetime.datetime
    created_at: datetime.datetime
    max_uses: int | None | Unset = UNSET
    note: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        token = self.token

        role = self.role

        status = self.status

        use_count = self.use_count

        expires_at = self.expires_at.isoformat()

        created_at = self.created_at.isoformat()

        max_uses: int | None | Unset
        if isinstance(self.max_uses, Unset):
            max_uses = UNSET
        else:
            max_uses = self.max_uses

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "token": token,
                "role": role,
                "status": status,
                "use_count": use_count,
                "expires_at": expires_at,
                "created_at": created_at,
            }
        )
        if max_uses is not UNSET:
            field_dict["max_uses"] = max_uses
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        token = d.pop("token")

        role = d.pop("role")

        status = d.pop("status")

        use_count = d.pop("use_count")

        expires_at = isoparse(d.pop("expires_at"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_max_uses(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_uses = _parse_max_uses(d.pop("max_uses", UNSET))

        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        room_invitation_code = cls(
            id=id,
            token=token,
            role=role,
            status=status,
            use_count=use_count,
            expires_at=expires_at,
            created_at=created_at,
            max_uses=max_uses,
            note=note,
        )

        room_invitation_code.additional_properties = d
        return room_invitation_code

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
