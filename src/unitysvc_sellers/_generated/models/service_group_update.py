from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.service_group_status_enum import ServiceGroupStatusEnum, check_service_group_status_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_group_update_membership_rules_type_0 import ServiceGroupUpdateMembershipRulesType0
    from ..models.service_group_update_routing_policy_type_0 import ServiceGroupUpdateRoutingPolicyType0
    from ..models.service_group_update_user_access_interfaces_type_0 import ServiceGroupUpdateUserAccessInterfacesType0


T = TypeVar("T", bound="ServiceGroupUpdate")


@_attrs_define
class ServiceGroupUpdate:
    """Schema for updating a ServiceGroup."""

    display_name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    membership_rules: None | ServiceGroupUpdateMembershipRulesType0 | Unset = UNSET
    user_access_interfaces: None | ServiceGroupUpdateUserAccessInterfacesType0 | Unset = UNSET
    routing_policy: None | ServiceGroupUpdateRoutingPolicyType0 | Unset = UNSET
    status: None | ServiceGroupStatusEnum | Unset = UNSET
    sort_order: int | None | Unset = UNSET
    parent_group_name: None | str | Unset = UNSET
    """ Parent group name. Resolved to ancestor_path based on owner context. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_group_update_membership_rules_type_0 import ServiceGroupUpdateMembershipRulesType0
        from ..models.service_group_update_routing_policy_type_0 import ServiceGroupUpdateRoutingPolicyType0
        from ..models.service_group_update_user_access_interfaces_type_0 import (
            ServiceGroupUpdateUserAccessInterfacesType0,
        )

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        membership_rules: dict[str, Any] | None | Unset
        if isinstance(self.membership_rules, Unset):
            membership_rules = UNSET
        elif isinstance(self.membership_rules, ServiceGroupUpdateMembershipRulesType0):
            membership_rules = self.membership_rules.to_dict()
        else:
            membership_rules = self.membership_rules

        user_access_interfaces: dict[str, Any] | None | Unset
        if isinstance(self.user_access_interfaces, Unset):
            user_access_interfaces = UNSET
        elif isinstance(self.user_access_interfaces, ServiceGroupUpdateUserAccessInterfacesType0):
            user_access_interfaces = self.user_access_interfaces.to_dict()
        else:
            user_access_interfaces = self.user_access_interfaces

        routing_policy: dict[str, Any] | None | Unset
        if isinstance(self.routing_policy, Unset):
            routing_policy = UNSET
        elif isinstance(self.routing_policy, ServiceGroupUpdateRoutingPolicyType0):
            routing_policy = self.routing_policy.to_dict()
        else:
            routing_policy = self.routing_policy

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, str):
            status = self.status
        else:
            status = self.status

        sort_order: int | None | Unset
        if isinstance(self.sort_order, Unset):
            sort_order = UNSET
        else:
            sort_order = self.sort_order

        parent_group_name: None | str | Unset
        if isinstance(self.parent_group_name, Unset):
            parent_group_name = UNSET
        else:
            parent_group_name = self.parent_group_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
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
        from ..models.service_group_update_membership_rules_type_0 import ServiceGroupUpdateMembershipRulesType0
        from ..models.service_group_update_routing_policy_type_0 import ServiceGroupUpdateRoutingPolicyType0
        from ..models.service_group_update_user_access_interfaces_type_0 import (
            ServiceGroupUpdateUserAccessInterfacesType0,
        )

        d = dict(src_dict)

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_membership_rules(data: object) -> None | ServiceGroupUpdateMembershipRulesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                membership_rules_type_0 = ServiceGroupUpdateMembershipRulesType0.from_dict(data)

                return membership_rules_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupUpdateMembershipRulesType0 | Unset, data)

        membership_rules = _parse_membership_rules(d.pop("membership_rules", UNSET))

        def _parse_user_access_interfaces(data: object) -> None | ServiceGroupUpdateUserAccessInterfacesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_access_interfaces_type_0 = ServiceGroupUpdateUserAccessInterfacesType0.from_dict(data)

                return user_access_interfaces_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupUpdateUserAccessInterfacesType0 | Unset, data)

        user_access_interfaces = _parse_user_access_interfaces(d.pop("user_access_interfaces", UNSET))

        def _parse_routing_policy(data: object) -> None | ServiceGroupUpdateRoutingPolicyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_policy_type_0 = ServiceGroupUpdateRoutingPolicyType0.from_dict(data)

                return routing_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupUpdateRoutingPolicyType0 | Unset, data)

        routing_policy = _parse_routing_policy(d.pop("routing_policy", UNSET))

        def _parse_status(data: object) -> None | ServiceGroupStatusEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = check_service_group_status_enum(data)

                return status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupStatusEnum | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_sort_order(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        sort_order = _parse_sort_order(d.pop("sort_order", UNSET))

        def _parse_parent_group_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

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
