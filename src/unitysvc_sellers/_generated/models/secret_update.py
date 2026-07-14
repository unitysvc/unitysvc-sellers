from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SecretUpdate")


@_attrs_define
class SecretUpdate:
    """Request body for variable-capable ``PUT /secrets/{name}`` endpoints.

    ``sensitive`` is only honored when creating rows; an existing row cannot be
    changed between secret and variable in place.

    """

    value: str
    """ Secret value (will be encrypted). May be empty. """
    sensitive: bool | None | Unset = UNSET
    """ Whether the value is write-only. Defaults to true on create and cannot be changed after creation. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        sensitive: bool | None | Unset
        if isinstance(self.sensitive, Unset):
            sensitive = UNSET
        else:
            sensitive = self.sensitive

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
            }
        )
        if sensitive is not UNSET:
            field_dict["sensitive"] = sensitive

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value")

        def _parse_sensitive(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        sensitive = _parse_sensitive(d.pop("sensitive", UNSET))

        secret_update = cls(
            value=value,
            sensitive=sensitive,
        )

        secret_update.additional_properties = d
        return secret_update

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
