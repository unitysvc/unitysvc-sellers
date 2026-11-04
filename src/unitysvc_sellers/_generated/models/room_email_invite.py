from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="RoomEmailInvite")


@_attrs_define
class RoomEmailInvite:
    emails: list[str]
    """ Up to 10 addresses at a time """

    def to_dict(self) -> dict[str, Any]:
        emails = self.emails

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "emails": emails,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        emails = cast(list[str], d.pop("emails"))

        room_email_invite = cls(
            emails=emails,
        )

        return room_email_invite
