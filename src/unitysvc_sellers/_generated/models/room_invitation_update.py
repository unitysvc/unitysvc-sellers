from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.room_invitation_update_role_type_0 import (
    RoomInvitationUpdateRoleType0,
    check_room_invitation_update_role_type_0,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomInvitationUpdate")


@_attrs_define
class RoomInvitationUpdate:
    """Change a code in place; its link keeps working."""

    role: None | RoomInvitationUpdateRoleType0 | Unset = UNSET
    expires_in_days: int | None | Unset = UNSET
    """ Reset the expiry to this many days from now """
    max_uses: int | None | Unset = UNSET
    """ None = unlimited; omit to keep the limit """

    def to_dict(self) -> dict[str, Any]:
        role: None | str | Unset
        if isinstance(self.role, Unset):
            role = UNSET
        elif isinstance(self.role, str):
            role = self.role
        else:
            role = self.role

        expires_in_days: int | None | Unset
        if isinstance(self.expires_in_days, Unset):
            expires_in_days = UNSET
        else:
            expires_in_days = self.expires_in_days

        max_uses: int | None | Unset
        if isinstance(self.max_uses, Unset):
            max_uses = UNSET
        else:
            max_uses = self.max_uses

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if role is not UNSET:
            field_dict["role"] = role
        if expires_in_days is not UNSET:
            field_dict["expires_in_days"] = expires_in_days
        if max_uses is not UNSET:
            field_dict["max_uses"] = max_uses

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_role(data: object) -> None | RoomInvitationUpdateRoleType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                role_type_0 = check_room_invitation_update_role_type_0(data)

                return role_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RoomInvitationUpdateRoleType0 | Unset, data)

        role = _parse_role(d.pop("role", UNSET))

        def _parse_expires_in_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expires_in_days = _parse_expires_in_days(d.pop("expires_in_days", UNSET))

        def _parse_max_uses(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_uses = _parse_max_uses(d.pop("max_uses", UNSET))

        room_invitation_update = cls(
            role=role,
            expires_in_days=expires_in_days,
            max_uses=max_uses,
        )

        return room_invitation_update
