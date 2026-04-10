from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="DefaultPaymentMethodPublic")



@_attrs_define
class DefaultPaymentMethodPublic:
    """ Public schema for default payment method information

     """

    default_pm_id: None | str | Unset = UNSET
    """ Default payment method ID from Stripe """
    default_pm_details: None | str | Unset = UNSET
    """ Formatted details (e.g., 'Visa ending in 4242') """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        default_pm_id: None | str | Unset
        if isinstance(self.default_pm_id, Unset):
            default_pm_id = UNSET
        else:
            default_pm_id = self.default_pm_id

        default_pm_details: None | str | Unset
        if isinstance(self.default_pm_details, Unset):
            default_pm_details = UNSET
        else:
            default_pm_details = self.default_pm_details


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if default_pm_id is not UNSET:
            field_dict["default_pm_id"] = default_pm_id
        if default_pm_details is not UNSET:
            field_dict["default_pm_details"] = default_pm_details

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_default_pm_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        default_pm_id = _parse_default_pm_id(d.pop("default_pm_id", UNSET))


        def _parse_default_pm_details(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        default_pm_details = _parse_default_pm_details(d.pop("default_pm_details", UNSET))


        default_payment_method_public = cls(
            default_pm_id=default_pm_id,
            default_pm_details=default_pm_details,
        )


        default_payment_method_public.additional_properties = d
        return default_payment_method_public

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
