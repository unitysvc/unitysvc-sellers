from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_offering_data_upstream_access_config_type_0_additional_property import (
        ServiceOfferingDataUpstreamAccessConfigType0AdditionalProperty,
    )


T = TypeVar("T", bound="ServiceOfferingDataUpstreamAccessConfigType0")


@_attrs_define
class ServiceOfferingDataUpstreamAccessConfigType0:
    additional_properties: dict[str, ServiceOfferingDataUpstreamAccessConfigType0AdditionalProperty] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_offering_data_upstream_access_config_type_0_additional_property import (
            ServiceOfferingDataUpstreamAccessConfigType0AdditionalProperty,
        )

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_offering_data_upstream_access_config_type_0_additional_property import (
            ServiceOfferingDataUpstreamAccessConfigType0AdditionalProperty,
        )

        d = dict(src_dict)
        service_offering_data_upstream_access_config_type_0 = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = ServiceOfferingDataUpstreamAccessConfigType0AdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        service_offering_data_upstream_access_config_type_0.additional_properties = additional_properties
        return service_offering_data_upstream_access_config_type_0

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> ServiceOfferingDataUpstreamAccessConfigType0AdditionalProperty:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: ServiceOfferingDataUpstreamAccessConfigType0AdditionalProperty) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
