from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.group_owner_type_enum import check_group_owner_type_enum
from ..models.group_owner_type_enum import GroupOwnerTypeEnum
from ..models.service_group_status_enum import check_service_group_status_enum
from ..models.service_group_status_enum import ServiceGroupStatusEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.service_group_ingest_data_membership_rules_type_0 import ServiceGroupIngestDataMembershipRulesType0
  from ..models.service_group_ingest_data_routing_policy_type_0 import ServiceGroupIngestDataRoutingPolicyType0
  from ..models.service_group_ingest_data_user_access_interfaces_type_0 import ServiceGroupIngestDataUserAccessInterfacesType0





T = TypeVar("T", bound="ServiceGroupIngestData")



@_attrs_define
class ServiceGroupIngestData:
    """ Schema for ingesting a service group from admin CLI.

    Extends ServiceGroupCreate with optional owner_id, owner_type, and status.
    Parent group can be specified by name (parent_group_name) for CLI convenience.

     """

    name: str
    display_name: str
    description: None | str | Unset = UNSET
    membership_rules: None | ServiceGroupIngestDataMembershipRulesType0 | Unset = UNSET
    user_access_interfaces: None | ServiceGroupIngestDataUserAccessInterfacesType0 | Unset = UNSET
    routing_policy: None | ServiceGroupIngestDataRoutingPolicyType0 | Unset = UNSET
    sort_order: int | Unset = 0
    parent_group_name: None | str | Unset = UNSET
    """ Parent group name. Resolved to ancestor_path based on owner context. """
    owner_id: None | Unset | UUID = UNSET
    owner_type: GroupOwnerTypeEnum | Unset = UNSET
    """ Owner type for service groups. """
    status: ServiceGroupStatusEnum | Unset = UNSET
    """ Status of a service group. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_group_ingest_data_membership_rules_type_0 import ServiceGroupIngestDataMembershipRulesType0
        from ..models.service_group_ingest_data_routing_policy_type_0 import ServiceGroupIngestDataRoutingPolicyType0
        from ..models.service_group_ingest_data_user_access_interfaces_type_0 import ServiceGroupIngestDataUserAccessInterfacesType0
        name = self.name

        display_name = self.display_name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        membership_rules: dict[str, Any] | None | Unset
        if isinstance(self.membership_rules, Unset):
            membership_rules = UNSET
        elif isinstance(self.membership_rules, ServiceGroupIngestDataMembershipRulesType0):
            membership_rules = self.membership_rules.to_dict()
        else:
            membership_rules = self.membership_rules

        user_access_interfaces: dict[str, Any] | None | Unset
        if isinstance(self.user_access_interfaces, Unset):
            user_access_interfaces = UNSET
        elif isinstance(self.user_access_interfaces, ServiceGroupIngestDataUserAccessInterfacesType0):
            user_access_interfaces = self.user_access_interfaces.to_dict()
        else:
            user_access_interfaces = self.user_access_interfaces

        routing_policy: dict[str, Any] | None | Unset
        if isinstance(self.routing_policy, Unset):
            routing_policy = UNSET
        elif isinstance(self.routing_policy, ServiceGroupIngestDataRoutingPolicyType0):
            routing_policy = self.routing_policy.to_dict()
        else:
            routing_policy = self.routing_policy

        sort_order = self.sort_order

        parent_group_name: None | str | Unset
        if isinstance(self.parent_group_name, Unset):
            parent_group_name = UNSET
        else:
            parent_group_name = self.parent_group_name

        owner_id: None | str | Unset
        if isinstance(self.owner_id, Unset):
            owner_id = UNSET
        elif isinstance(self.owner_id, UUID):
            owner_id = str(self.owner_id)
        else:
            owner_id = self.owner_id

        owner_type: str | Unset = UNSET
        if not isinstance(self.owner_type, Unset):
            owner_type = self.owner_type


        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status



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
        if owner_id is not UNSET:
            field_dict["owner_id"] = owner_id
        if owner_type is not UNSET:
            field_dict["owner_type"] = owner_type
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_group_ingest_data_membership_rules_type_0 import ServiceGroupIngestDataMembershipRulesType0
        from ..models.service_group_ingest_data_routing_policy_type_0 import ServiceGroupIngestDataRoutingPolicyType0
        from ..models.service_group_ingest_data_user_access_interfaces_type_0 import ServiceGroupIngestDataUserAccessInterfacesType0
        d = dict(src_dict)
        name = d.pop("name")

        display_name = d.pop("display_name")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_membership_rules(data: object) -> None | ServiceGroupIngestDataMembershipRulesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                membership_rules_type_0 = ServiceGroupIngestDataMembershipRulesType0.from_dict(data)



                return membership_rules_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupIngestDataMembershipRulesType0 | Unset, data)

        membership_rules = _parse_membership_rules(d.pop("membership_rules", UNSET))


        def _parse_user_access_interfaces(data: object) -> None | ServiceGroupIngestDataUserAccessInterfacesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_access_interfaces_type_0 = ServiceGroupIngestDataUserAccessInterfacesType0.from_dict(data)



                return user_access_interfaces_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupIngestDataUserAccessInterfacesType0 | Unset, data)

        user_access_interfaces = _parse_user_access_interfaces(d.pop("user_access_interfaces", UNSET))


        def _parse_routing_policy(data: object) -> None | ServiceGroupIngestDataRoutingPolicyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_policy_type_0 = ServiceGroupIngestDataRoutingPolicyType0.from_dict(data)



                return routing_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupIngestDataRoutingPolicyType0 | Unset, data)

        routing_policy = _parse_routing_policy(d.pop("routing_policy", UNSET))


        sort_order = d.pop("sort_order", UNSET)

        def _parse_parent_group_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_group_name = _parse_parent_group_name(d.pop("parent_group_name", UNSET))


        def _parse_owner_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                owner_id_type_0 = UUID(data)



                return owner_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        owner_id = _parse_owner_id(d.pop("owner_id", UNSET))


        _owner_type = d.pop("owner_type", UNSET)
        owner_type: GroupOwnerTypeEnum | Unset
        if isinstance(_owner_type,  Unset):
            owner_type = UNSET
        else:
            owner_type = check_group_owner_type_enum(_owner_type)




        _status = d.pop("status", UNSET)
        status: ServiceGroupStatusEnum | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_service_group_status_enum(_status)




        service_group_ingest_data = cls(
            name=name,
            display_name=display_name,
            description=description,
            membership_rules=membership_rules,
            user_access_interfaces=user_access_interfaces,
            routing_policy=routing_policy,
            sort_order=sort_order,
            parent_group_name=parent_group_name,
            owner_id=owner_id,
            owner_type=owner_type,
            status=status,
        )


        service_group_ingest_data.additional_properties = d
        return service_group_ingest_data

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
