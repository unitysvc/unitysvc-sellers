from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.group_owner_type_enum import check_group_owner_type_enum
from ..models.group_owner_type_enum import GroupOwnerTypeEnum
from ..models.group_type_enum import check_group_type_enum
from ..models.group_type_enum import GroupTypeEnum
from ..models.service_group_status_enum import check_service_group_status_enum
from ..models.service_group_status_enum import ServiceGroupStatusEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.service_group_public_membership_rules_type_0 import ServiceGroupPublicMembershipRulesType0
  from ..models.service_group_public_routing_policy_type_0 import ServiceGroupPublicRoutingPolicyType0
  from ..models.service_group_public_user_access_interfaces_type_0 import ServiceGroupPublicUserAccessInterfacesType0





T = TypeVar("T", bound="ServiceGroupPublic")



@_attrs_define
class ServiceGroupPublic:
    """ Public response model for ServiceGroup.

     """

    id: UUID
    owner_id: UUID
    owner_type: GroupOwnerTypeEnum
    """ Owner type for service groups. """
    name: str
    display_name: str
    status: ServiceGroupStatusEnum
    """ Status of a service group. """
    created_at: datetime.datetime
    description: None | str | Unset = UNSET
    membership_rules: None | ServiceGroupPublicMembershipRulesType0 | Unset = UNSET
    user_access_interfaces: None | ServiceGroupPublicUserAccessInterfacesType0 | Unset = UNSET
    routing_policy: None | ServiceGroupPublicRoutingPolicyType0 | Unset = UNSET
    group_type: GroupTypeEnum | Unset = UNSET
    """ Type of service group — derived from configuration, not set directly.

    Derivation rules:
    - No rules, no access interfaces → category (organizes descendants)
    - Rules, no access interfaces → collection (curated set for browsing)
    - Rules + access interfaces → group (has own API endpoint + routing)
    - System-generated catch-all → misc """
    sort_order: int | Unset = 0
    ancestor_path: str | Unset = '/'
    service_count: int | None | Unset = UNSET
    enrolled_count: int | None | Unset = UNSET
    unenrolled_count: int | None | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_group_public_membership_rules_type_0 import ServiceGroupPublicMembershipRulesType0
        from ..models.service_group_public_routing_policy_type_0 import ServiceGroupPublicRoutingPolicyType0
        from ..models.service_group_public_user_access_interfaces_type_0 import ServiceGroupPublicUserAccessInterfacesType0
        id = str(self.id)

        owner_id = str(self.owner_id)

        owner_type: str = self.owner_type

        name = self.name

        display_name = self.display_name

        status: str = self.status

        created_at = self.created_at.isoformat()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        membership_rules: dict[str, Any] | None | Unset
        if isinstance(self.membership_rules, Unset):
            membership_rules = UNSET
        elif isinstance(self.membership_rules, ServiceGroupPublicMembershipRulesType0):
            membership_rules = self.membership_rules.to_dict()
        else:
            membership_rules = self.membership_rules

        user_access_interfaces: dict[str, Any] | None | Unset
        if isinstance(self.user_access_interfaces, Unset):
            user_access_interfaces = UNSET
        elif isinstance(self.user_access_interfaces, ServiceGroupPublicUserAccessInterfacesType0):
            user_access_interfaces = self.user_access_interfaces.to_dict()
        else:
            user_access_interfaces = self.user_access_interfaces

        routing_policy: dict[str, Any] | None | Unset
        if isinstance(self.routing_policy, Unset):
            routing_policy = UNSET
        elif isinstance(self.routing_policy, ServiceGroupPublicRoutingPolicyType0):
            routing_policy = self.routing_policy.to_dict()
        else:
            routing_policy = self.routing_policy

        group_type: str | Unset = UNSET
        if not isinstance(self.group_type, Unset):
            group_type = self.group_type


        sort_order = self.sort_order

        ancestor_path = self.ancestor_path

        service_count: int | None | Unset
        if isinstance(self.service_count, Unset):
            service_count = UNSET
        else:
            service_count = self.service_count

        enrolled_count: int | None | Unset
        if isinstance(self.enrolled_count, Unset):
            enrolled_count = UNSET
        else:
            enrolled_count = self.enrolled_count

        unenrolled_count: int | None | Unset
        if isinstance(self.unenrolled_count, Unset):
            unenrolled_count = UNSET
        else:
            unenrolled_count = self.unenrolled_count

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "owner_id": owner_id,
            "owner_type": owner_type,
            "name": name,
            "display_name": display_name,
            "status": status,
            "created_at": created_at,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if membership_rules is not UNSET:
            field_dict["membership_rules"] = membership_rules
        if user_access_interfaces is not UNSET:
            field_dict["user_access_interfaces"] = user_access_interfaces
        if routing_policy is not UNSET:
            field_dict["routing_policy"] = routing_policy
        if group_type is not UNSET:
            field_dict["group_type"] = group_type
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order
        if ancestor_path is not UNSET:
            field_dict["ancestor_path"] = ancestor_path
        if service_count is not UNSET:
            field_dict["service_count"] = service_count
        if enrolled_count is not UNSET:
            field_dict["enrolled_count"] = enrolled_count
        if unenrolled_count is not UNSET:
            field_dict["unenrolled_count"] = unenrolled_count
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_group_public_membership_rules_type_0 import ServiceGroupPublicMembershipRulesType0
        from ..models.service_group_public_routing_policy_type_0 import ServiceGroupPublicRoutingPolicyType0
        from ..models.service_group_public_user_access_interfaces_type_0 import ServiceGroupPublicUserAccessInterfacesType0
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        owner_id = UUID(d.pop("owner_id"))




        owner_type = check_group_owner_type_enum(d.pop("owner_type"))




        name = d.pop("name")

        display_name = d.pop("display_name")

        status = check_service_group_status_enum(d.pop("status"))




        created_at = isoparse(d.pop("created_at"))




        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_membership_rules(data: object) -> None | ServiceGroupPublicMembershipRulesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                membership_rules_type_0 = ServiceGroupPublicMembershipRulesType0.from_dict(data)



                return membership_rules_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupPublicMembershipRulesType0 | Unset, data)

        membership_rules = _parse_membership_rules(d.pop("membership_rules", UNSET))


        def _parse_user_access_interfaces(data: object) -> None | ServiceGroupPublicUserAccessInterfacesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_access_interfaces_type_0 = ServiceGroupPublicUserAccessInterfacesType0.from_dict(data)



                return user_access_interfaces_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupPublicUserAccessInterfacesType0 | Unset, data)

        user_access_interfaces = _parse_user_access_interfaces(d.pop("user_access_interfaces", UNSET))


        def _parse_routing_policy(data: object) -> None | ServiceGroupPublicRoutingPolicyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_policy_type_0 = ServiceGroupPublicRoutingPolicyType0.from_dict(data)



                return routing_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceGroupPublicRoutingPolicyType0 | Unset, data)

        routing_policy = _parse_routing_policy(d.pop("routing_policy", UNSET))


        _group_type = d.pop("group_type", UNSET)
        group_type: GroupTypeEnum | Unset
        if isinstance(_group_type,  Unset):
            group_type = UNSET
        else:
            group_type = check_group_type_enum(_group_type)




        sort_order = d.pop("sort_order", UNSET)

        ancestor_path = d.pop("ancestor_path", UNSET)

        def _parse_service_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        service_count = _parse_service_count(d.pop("service_count", UNSET))


        def _parse_enrolled_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        enrolled_count = _parse_enrolled_count(d.pop("enrolled_count", UNSET))


        def _parse_unenrolled_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        unenrolled_count = _parse_unenrolled_count(d.pop("unenrolled_count", UNSET))


        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)



                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))


        service_group_public = cls(
            id=id,
            owner_id=owner_id,
            owner_type=owner_type,
            name=name,
            display_name=display_name,
            status=status,
            created_at=created_at,
            description=description,
            membership_rules=membership_rules,
            user_access_interfaces=user_access_interfaces,
            routing_policy=routing_policy,
            group_type=group_type,
            sort_order=sort_order,
            ancestor_path=ancestor_path,
            service_count=service_count,
            enrolled_count=enrolled_count,
            unenrolled_count=unenrolled_count,
            updated_at=updated_at,
        )


        service_group_public.additional_properties = d
        return service_group_public

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
