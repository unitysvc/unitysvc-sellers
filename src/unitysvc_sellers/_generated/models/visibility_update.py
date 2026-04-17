from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.service_visibility_enum import check_service_visibility_enum
from ..models.service_visibility_enum import ServiceVisibilityEnum
from typing import cast






T = TypeVar("T", bound="VisibilityUpdate")



@_attrs_define
class VisibilityUpdate:
    """ Request body for updating visibility on a service.

     """

    visibility: ServiceVisibilityEnum
    """ Visibility of a service in the catalog.

    - unlisted: Live and routable, not in catalog, accessible via direct link
    - public: In catalog, fully discoverable
    - private: Live and routable, ops/internal use only """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        visibility: str = self.visibility


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "visibility": visibility,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        visibility = check_service_visibility_enum(d.pop("visibility"))




        visibility_update = cls(
            visibility=visibility,
        )


        visibility_update.additional_properties = d
        return visibility_update

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
