from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.service_group_status_enum import check_service_group_status_enum
from ..models.service_group_status_enum import ServiceGroupStatusEnum
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.service_group_update_user_access_interfaces_type_0 import ServiceGroupUpdateUserAccessInterfacesType0
  from ..models.service_group_update_routing_policy_type_0 import ServiceGroupUpdateRoutingPolicyType0
  from ..models.service_group_update_membership_rules_type_0 import ServiceGroupUpdateMembershipRulesType0





T = TypeVar("T", bound="ServiceGroupUpdate")



@_attrs_define
class ServiceGroupUpdate:
    """ Schema for updating a ServiceGroup.

     """

    display_name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    membership_rules: Union['ServiceGroupUpdateMembershipRulesType0', None, Unset] = UNSET
    user_access_interfaces: Union['ServiceGroupUpdateUserAccessInterfacesType0', None, Unset] = UNSET
    routing_policy: Union['ServiceGroupUpdateRoutingPolicyType0', None, Unset] = UNSET
    status: Union[None, ServiceGroupStatusEnum, Unset] = UNSET
    sort_order: Union[None, Unset, int] = UNSET
    parent_group_name: Union[None, Unset, str] = UNSET
    """ Parent group name. Resolved to ancestor_path based on owner context. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_group_update_user_access_interfaces_type_0 import ServiceGroupUpdateUserAccessInterfacesType0
        from ..models.service_group_update_routing_policy_type_0 import ServiceGroupUpdateRoutingPolicyType0
        from ..models.service_group_update_membership_rules_type_0 import ServiceGroupUpdateMembershipRulesType0
        display_name: Union[None, Unset, str]
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        membership_rules: Union[None, Unset, dict[str, Any]]
        if isinstance(self.membership_rules, Unset):
            membership_rules = UNSET
        elif isinstance(self.membership_rules, ServiceGroupUpdateMembershipRulesType0):
            membership_rules = self.membership_rules.to_dict()
        else:
            membership_rules = self.membership_rules

        user_access_interfaces: Union[None, Unset, dict[str, Any]]
        if isinstance(self.user_access_interfaces, Unset):
            user_access_interfaces = UNSET
        elif isinstance(self.user_access_interfaces, ServiceGroupUpdateUserAccessInterfacesType0):
            user_access_interfaces = self.user_access_interfaces.to_dict()
        else:
            user_access_interfaces = self.user_access_interfaces

        routing_policy: Union[None, Unset, dict[str, Any]]
        if isinstance(self.routing_policy, Unset):
            routing_policy = UNSET
        elif isinstance(self.routing_policy, ServiceGroupUpdateRoutingPolicyType0):
            routing_policy = self.routing_policy.to_dict()
        else:
            routing_policy = self.routing_policy

        status: Union[None, Unset, str]
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, str):
            status = self.status
        else:
            status = self.status

        sort_order: Union[None, Unset, int]
        if isinstance(self.sort_order, Unset):
            sort_order = UNSET
        else:
            sort_order = self.sort_order

        parent_group_name: Union[None, Unset, str]
        if isinstance(self.parent_group_name, Unset):
            parent_group_name = UNSET
        else:
            parent_group_name = self.parent_group_name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if membership_rules is not UNSET:
            field_dict["membership_rules"] = membership_rules
        if user_access_interfaces is not UNSET:
            field_dict["user_access_interfaces"] = user_access_interfaces
        if routing_policy is not UNSET:
            field_dict["routing_policy"] = routing_policy
        if status is not UNSET:
            field_dict["status"] = status
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order
        if parent_group_name is not UNSET:
            field_dict["parent_group_name"] = parent_group_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_group_update_user_access_interfaces_type_0 import ServiceGroupUpdateUserAccessInterfacesType0
        from ..models.service_group_update_routing_policy_type_0 import ServiceGroupUpdateRoutingPolicyType0
        from ..models.service_group_update_membership_rules_type_0 import ServiceGroupUpdateMembershipRulesType0
        d = dict(src_dict)
        def _parse_display_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))


        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_membership_rules(data: object) -> Union['ServiceGroupUpdateMembershipRulesType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                membership_rules_type_0 = ServiceGroupUpdateMembershipRulesType0.from_dict(data)



                return membership_rules_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceGroupUpdateMembershipRulesType0', None, Unset], data)

        membership_rules = _parse_membership_rules(d.pop("membership_rules", UNSET))


        def _parse_user_access_interfaces(data: object) -> Union['ServiceGroupUpdateUserAccessInterfacesType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_access_interfaces_type_0 = ServiceGroupUpdateUserAccessInterfacesType0.from_dict(data)



                return user_access_interfaces_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceGroupUpdateUserAccessInterfacesType0', None, Unset], data)

        user_access_interfaces = _parse_user_access_interfaces(d.pop("user_access_interfaces", UNSET))


        def _parse_routing_policy(data: object) -> Union['ServiceGroupUpdateRoutingPolicyType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_policy_type_0 = ServiceGroupUpdateRoutingPolicyType0.from_dict(data)



                return routing_policy_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceGroupUpdateRoutingPolicyType0', None, Unset], data)

        routing_policy = _parse_routing_policy(d.pop("routing_policy", UNSET))


        def _parse_status(data: object) -> Union[None, ServiceGroupStatusEnum, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = check_service_group_status_enum(data)



                return status_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, ServiceGroupStatusEnum, Unset], data)

        status = _parse_status(d.pop("status", UNSET))


        def _parse_sort_order(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        sort_order = _parse_sort_order(d.pop("sort_order", UNSET))


        def _parse_parent_group_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_group_name = _parse_parent_group_name(d.pop("parent_group_name", UNSET))


        service_group_update = cls(
            display_name=display_name,
            description=description,
            membership_rules=membership_rules,
            user_access_interfaces=user_access_interfaces,
            routing_policy=routing_policy,
            status=status,
            sort_order=sort_order,
            parent_group_name=parent_group_name,
        )


        service_group_update.additional_properties = d
        return service_group_update

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
