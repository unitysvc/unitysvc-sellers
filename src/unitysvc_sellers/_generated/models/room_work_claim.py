from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomWorkClaim")


@_attrs_define
class RoomWorkClaim:
    """The room Next claimed for the caller, or none waiting (#2929). Renew
    the claim while the room is open; it lapses after ``expires_in`` seconds
    without renewal and the room becomes selectable again.

    """

    room_id: None | Unset | UUID = UNSET
    handle: None | str | Unset = UNSET
    """ How the caller's account addresses the room """
    claim_token: None | str | Unset = UNSET
    expires_in: int | Unset = 60
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        room_id: None | str | Unset
        if isinstance(self.room_id, Unset):
            room_id = UNSET
        elif isinstance(self.room_id, UUID):
            room_id = str(self.room_id)
        else:
            room_id = self.room_id

        handle: None | str | Unset
        if isinstance(self.handle, Unset):
            handle = UNSET
        else:
            handle = self.handle

        claim_token: None | str | Unset
        if isinstance(self.claim_token, Unset):
            claim_token = UNSET
        else:
            claim_token = self.claim_token

        expires_in = self.expires_in

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if room_id is not UNSET:
            field_dict["room_id"] = room_id
        if handle is not UNSET:
            field_dict["handle"] = handle
        if claim_token is not UNSET:
            field_dict["claim_token"] = claim_token
        if expires_in is not UNSET:
            field_dict["expires_in"] = expires_in

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_room_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                room_id_type_0 = UUID(data)

                return room_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        room_id = _parse_room_id(d.pop("room_id", UNSET))

        def _parse_handle(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        handle = _parse_handle(d.pop("handle", UNSET))

        def _parse_claim_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        claim_token = _parse_claim_token(d.pop("claim_token", UNSET))

        expires_in = d.pop("expires_in", UNSET)

        room_work_claim = cls(
            room_id=room_id,
            handle=handle,
            claim_token=claim_token,
            expires_in=expires_in,
        )

        room_work_claim.additional_properties = d
        return room_work_claim

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
