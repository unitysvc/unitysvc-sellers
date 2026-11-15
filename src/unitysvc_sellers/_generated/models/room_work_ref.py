from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomWorkRef")


@_attrs_define
class RoomWorkRef:
    """The room a worker is finishing (#2929)."""

    room_id: UUID
    claim_token: None | str | Unset = UNSET
    """ The claim Next or a renewal returned """
    offset: int | None | Unset = UNSET
    """ The highest message offset the worker's client displayed; completion covers only messages through it """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        room_id = str(self.room_id)

        claim_token: None | str | Unset
        if isinstance(self.claim_token, Unset):
            claim_token = UNSET
        else:
            claim_token = self.claim_token

        offset: int | None | Unset
        if isinstance(self.offset, Unset):
            offset = UNSET
        else:
            offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "room_id": room_id,
            }
        )
        if claim_token is not UNSET:
            field_dict["claim_token"] = claim_token
        if offset is not UNSET:
            field_dict["offset"] = offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        room_id = UUID(d.pop("room_id"))

        def _parse_claim_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        claim_token = _parse_claim_token(d.pop("claim_token", UNSET))

        def _parse_offset(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        offset = _parse_offset(d.pop("offset", UNSET))

        room_work_ref = cls(
            room_id=room_id,
            claim_token=claim_token,
            offset=offset,
        )

        room_work_ref.additional_properties = d
        return room_work_ref

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
