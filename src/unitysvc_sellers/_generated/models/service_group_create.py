from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.service_group_create_membership_rules_type_0 import ServiceGroupCreateMembershipRulesType0
  from ..models.service_group_create_user_access_interfaces_type_0 import ServiceGroupCreateUserAccessInterfacesType0
  from ..models.service_group_create_routing_policy_type_0 import ServiceGroupCreateRoutingPolicyType0





T = TypeVar("T", bound="ServiceGroupCreate")



@_attrs_define
class ServiceGroupCreate:
    """ Schema for creating a ServiceGroup.

     """

    name: str
    display_name: str
    description: Union[None, Unset, str] = UNSET
    membership_rules: Union['ServiceGroupCreateMembershipRulesType0', None, Unset] = UNSET
    user_access_interfaces: Union['ServiceGroupCreateUserAccessInterfacesType0', None, Unset] = UNSET
    routing_policy: Union['ServiceGroupCreateRoutingPolicyType0', None, Unset] = UNSET
    sort_order: Union[Unset, int] = 0
    parent_group_name: Union[None, Unset, str] = UNSET
    """ Parent group name. Resolved to ancestor_path based on owner context. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_group_create_membership_rules_type_0 import ServiceGroupCreateMembershipRulesType0
        from ..models.service_group_create_user_access_interfaces_type_0 import ServiceGroupCreateUserAccessInterfacesType0
        from ..models.service_group_create_routing_policy_type_0 import ServiceGroupCreateRoutingPolicyType0
        name = self.name

        display_name = self.display_name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        membership_rules: Union[None, Unset, dict[str, Any]]
        if isinstance(self.membership_rules, Unset):
            membership_rules = UNSET
        elif isinstance(self.membership_rules, ServiceGroupCreateMembershipRulesType0):
            membership_rules = self.membership_rules.to_dict()
        else:
            membership_rules = self.membership_rules

        user_access_interfaces: Union[None, Unset, dict[str, Any]]
        if isinstance(self.user_access_interfaces, Unset):
            user_access_interfaces = UNSET
        elif isinstance(self.user_access_interfaces, ServiceGroupCreateUserAccessInterfacesType0):
            user_access_interfaces = self.user_access_interfaces.to_dict()
        else:
            user_access_interfaces = self.user_access_interfaces

        routing_policy: Union[None, Unset, dict[str, Any]]
        if isinstance(self.routing_policy, Unset):
            routing_policy = UNSET
        elif isinstance(self.routing_policy, ServiceGroupCreateRoutingPolicyType0):
            routing_policy = self.routing_policy.to_dict()
        else:
            routing_policy = self.routing_policy

        sort_order = self.sort_order

        parent_group_name: Union[None, Unset, str]
        if isinstance(self.parent_group_name, Unset):
            parent_group_name = UNSET
        else:
            parent_group_name = self.parent_group_name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "display_name": display_name,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if membership_rules is not UNSET:
            field_dict["membership_rules"] = membership_rules
        if user_access_interfaces is not UNSET:
            field_dict["user_access_interfaces"] = user_access_interfaces
        if routing_policy is not UNSET:
            field_dict["routing_policy"] = routing_policy
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order
        if parent_group_name is not UNSET:
            field_dict["parent_group_name"] = parent_group_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_group_create_membership_rules_type_0 import ServiceGroupCreateMembershipRulesType0
        from ..models.service_group_create_user_access_interfaces_type_0 import ServiceGroupCreateUserAccessInterfacesType0
        from ..models.service_group_create_routing_policy_type_0 import ServiceGroupCreateRoutingPolicyType0
        d = dict(src_dict)
        name = d.pop("name")

        display_name = d.pop("display_name")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_membership_rules(data: object) -> Union['ServiceGroupCreateMembershipRulesType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                membership_rules_type_0 = ServiceGroupCreateMembershipRulesType0.from_dict(data)



                return membership_rules_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceGroupCreateMembershipRulesType0', None, Unset], data)

        membership_rules = _parse_membership_rules(d.pop("membership_rules", UNSET))


        def _parse_user_access_interfaces(data: object) -> Union['ServiceGroupCreateUserAccessInterfacesType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_access_interfaces_type_0 = ServiceGroupCreateUserAccessInterfacesType0.from_dict(data)



                return user_access_interfaces_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceGroupCreateUserAccessInterfacesType0', None, Unset], data)

        user_access_interfaces = _parse_user_access_interfaces(d.pop("user_access_interfaces", UNSET))


        def _parse_routing_policy(data: object) -> Union['ServiceGroupCreateRoutingPolicyType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_policy_type_0 = ServiceGroupCreateRoutingPolicyType0.from_dict(data)



                return routing_policy_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceGroupCreateRoutingPolicyType0', None, Unset], data)

        routing_policy = _parse_routing_policy(d.pop("routing_policy", UNSET))


        sort_order = d.pop("sort_order", UNSET)

        def _parse_parent_group_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_group_name = _parse_parent_group_name(d.pop("parent_group_name", UNSET))


        service_group_create = cls(
            name=name,
            display_name=display_name,
            description=description,
            membership_rules=membership_rules,
            user_access_interfaces=user_access_interfaces,
            routing_policy=routing_policy,
            sort_order=sort_order,
            parent_group_name=parent_group_name,
        )


        service_group_create.additional_properties = d
        return service_group_create

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
