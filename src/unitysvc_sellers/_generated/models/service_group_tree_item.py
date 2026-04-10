from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.group_type_enum import check_group_type_enum
from ..models.group_type_enum import GroupTypeEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID






T = TypeVar("T", bound="ServiceGroupTreeItem")



@_attrs_define
class ServiceGroupTreeItem:
    """ Minimal response model for service group tree view.

     """

    id: UUID
    name: str
    display_name: str
    ancestor_path: str | Unset = '/'
    group_type: GroupTypeEnum | Unset = UNSET
    """ Type of service group — derived from configuration, not set directly.

    Derivation rules:
    - No rules, no access interfaces → category (organizes descendants)
    - Rules, no access interfaces → collection (curated set for browsing)
    - Rules + access interfaces → group (has own API endpoint + routing)
    - System-generated catch-all → misc """
    sort_order: int | Unset = 0
    service_count: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        display_name = self.display_name

        ancestor_path = self.ancestor_path

        group_type: str | Unset = UNSET
        if not isinstance(self.group_type, Unset):
            group_type = self.group_type


        sort_order = self.sort_order

        service_count = self.service_count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "display_name": display_name,
        })
        if ancestor_path is not UNSET:
            field_dict["ancestor_path"] = ancestor_path
        if group_type is not UNSET:
            field_dict["group_type"] = group_type
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order
        if service_count is not UNSET:
            field_dict["service_count"] = service_count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        name = d.pop("name")

        display_name = d.pop("display_name")

        ancestor_path = d.pop("ancestor_path", UNSET)

        _group_type = d.pop("group_type", UNSET)
        group_type: GroupTypeEnum | Unset
        if isinstance(_group_type,  Unset):
            group_type = UNSET
        else:
            group_type = check_group_type_enum(_group_type)




        sort_order = d.pop("sort_order", UNSET)

        service_count = d.pop("service_count", UNSET)

        service_group_tree_item = cls(
            id=id,
            name=name,
            display_name=display_name,
            ancestor_path=ancestor_path,
            group_type=group_type,
            sort_order=sort_order,
            service_count=service_count,
        )


        service_group_tree_item.additional_properties = d
        return service_group_tree_item

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
