from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SecretUpdate")


@_attrs_define
class SecretUpdate:
    """Request body for ``PUT /secrets/{name}``.

    Carries only the value — the name comes from the URL path. The same
    schema is used for both create and update because ``PUT`` is
    idempotent (see issue #798).

    Empty string is allowed: a customer may deliberately store ``""``
    to override a non-empty default in a ``${ secrets.X ?? default }``
    reference. ``??`` coalesces on null only, so the explicit empty
    value is preserved.

    """

    value: str
    """ Secret value (will be encrypted). May be empty. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value")

        secret_update = cls(
            value=value,
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
