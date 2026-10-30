from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WebhookRollSecret")


@_attrs_define
class WebhookRollSecret:
    expires_in_hours: int | Unset = 0
    """ How long the old secret keeps signing """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expires_in_hours = self.expires_in_hours

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if expires_in_hours is not UNSET:
            field_dict["expires_in_hours"] = expires_in_hours

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        expires_in_hours = d.pop("expires_in_hours", UNSET)

        webhook_roll_secret = cls(
            expires_in_hours=expires_in_hours,
        )

        webhook_roll_secret.additional_properties = d
        return webhook_roll_secret

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
