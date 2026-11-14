from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomReturnLater")


@_attrs_define
class RoomReturnLater:
    claim_token: None | str | Unset = UNSET
    """ The caller's claim on the room, released """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        claim_token: None | str | Unset
        if isinstance(self.claim_token, Unset):
            claim_token = UNSET
        else:
            claim_token = self.claim_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if claim_token is not UNSET:
            field_dict["claim_token"] = claim_token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_claim_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        claim_token = _parse_claim_token(d.pop("claim_token", UNSET))

        room_return_later = cls(
            claim_token=claim_token,
        )

        room_return_later.additional_properties = d
        return room_return_later

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
