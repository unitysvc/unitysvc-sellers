from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_interface_public_response_rules_type_0_additional_property_type_0 import (
        AccessInterfacePublicResponseRulesType0AdditionalPropertyType0,
    )


T = TypeVar("T", bound="AccessInterfacePublicResponseRulesType0")


@_attrs_define
class AccessInterfacePublicResponseRulesType0:
    additional_properties: dict[str, AccessInterfacePublicResponseRulesType0AdditionalPropertyType0 | str] = (
        _attrs_field(init=False, factory=dict)
    )

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_interface_public_response_rules_type_0_additional_property_type_0 import (
            AccessInterfacePublicResponseRulesType0AdditionalPropertyType0,
        )

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, AccessInterfacePublicResponseRulesType0AdditionalPropertyType0):
                field_dict[prop_name] = prop.to_dict()
            else:
                field_dict[prop_name] = prop

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_interface_public_response_rules_type_0_additional_property_type_0 import (
            AccessInterfacePublicResponseRulesType0AdditionalPropertyType0,
        )

        d = dict(src_dict)
        access_interface_public_response_rules_type_0 = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(
                data: object,
            ) -> AccessInterfacePublicResponseRulesType0AdditionalPropertyType0 | str:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_0 = (
                        AccessInterfacePublicResponseRulesType0AdditionalPropertyType0.from_dict(data)
                    )

                    return additional_property_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                return cast(AccessInterfacePublicResponseRulesType0AdditionalPropertyType0 | str, data)

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        access_interface_public_response_rules_type_0.additional_properties = additional_properties
        return access_interface_public_response_rules_type_0

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> AccessInterfacePublicResponseRulesType0AdditionalPropertyType0 | str:
        return self.additional_properties[key]

    def __setitem__(
        self, key: str, value: AccessInterfacePublicResponseRulesType0AdditionalPropertyType0 | str
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
