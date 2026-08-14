from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.group_owner_type_enum import GroupOwnerTypeEnum, check_group_owner_type_enum
from ..models.group_type_enum import GroupTypeEnum, check_group_type_enum
from ..models.service_group_status_enum import ServiceGroupStatusEnum, check_service_group_status_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_group_public_membership_rules_type_0 import ServiceGroupPublicMembershipRulesType0
    from ..models.service_group_public_routing_policy_type_0 import ServiceGroupPublicRoutingPolicyType0


T = TypeVar("T", bound="ServiceGroupPublic")


@_attrs_define
class ServiceGroupPublic:
    """Public response model for ServiceGroup."""

    id: UUID
    role_id: UUID
    owner_type: GroupOwnerTypeEnum
    """ Owner type for service groups. """
    name: str
    display_name: str
    status: ServiceGroupStatusEnum
    """ Status of a service group. """
    created_at: datetime.datetime
    owner_id: None | Unset | UUID = UNSET
    description: None | str | Unset = UNSET
    membership_rules: None | ServiceGroupPublicMembershipRulesType0 | Unset = UNSET
    routing_policy: None | ServiceGroupPublicRoutingPolicyType0 | Unset = UNSET
    group_type: GroupTypeEnum | Unset = UNSET
    """ Type of service group. Derived from members, not authored (unitysvc#1686).

    Two of the five types are routable (a ``/g/<name>`` endpoint); the rest are
    not:

    A quick-characterization spectrum derived from ``routable_keys``
    (unitysvc#1730); the gateway routes off ``routable_keys`` itself, not this:

    - ``keyed`` — one extreme: a clean menu, every service addressable by its own
      distinct routing key (each key maps to a single service); keyless access an
      optional feature. Serves ``/v1/models`` and is tool-explorable.
    - ``open`` — the middle: routable, but not a clean per-service menu — a
      keyless-only pool, partial keying, or a key that fans to several services.
    - ``collection`` — the other extreme: **not** a routing endpoint at all
      (empty ``routable_keys`` — no members, or every bucket format-collides).

    Routability is exactly ``group_type in {open, keyed}`` (``collection`` =
    empty ``routable_keys``), so the routing gate is unchanged; #1730 only re-cut
    the open↔keyed boundary. Whether a keyless request is served is a
    ``routable_keys`` fact, not a type fact.
    - ``category`` — a parent with no members of its own; its membership is the
      union of its descendants, for browsing only.
    - ``capability_pool`` (#1244) — the ``/p/<name>`` namespace; membership is
      claim-driven (services instantiated from a ServiceTemplate whose
      ``pool_name`` matches), set by a dedicated refresh.

    ``open`` / ``keyed`` / ``collection`` are derived from the members at
    membership refresh; ``category`` and ``capability_pool`` are set explicitly
    and never re-derived. (The former ``routable`` value was split into
    ``open`` / ``keyed``, and the ``misc`` catch-all removed — unitysvc#1686.) """
    sort_order: int | Unset = 0
    ancestor_path: str | Unset = "/"
    service_count: int | None | Unset = UNSET
    enrolled_count: int | None | Unset = UNSET
    unenrolled_count: int | None | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_group_public_membership_rules_type_0 import ServiceGroupPublicMembershipRulesType0
        from ..models.service_group_public_routing_policy_type_0 import ServiceGroupPublicRoutingPolicyType0

        id = str(self.id)

        role_id = str(self.role_id)

        owner_type: str = self.owner_type

        name = self.name

        display_name = self.display_name

        status: str = self.status

        created_at = self.created_at.isoformat()

        owner_id: None | str | Unset
        if isinstance(self.owner_id, Unset):
            owner_id = UNSET
        elif isinstance(self.owner_id, UUID):
            owner_id = str(self.owner_id)
        else:
            owner_id = self.owner_id

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
        field_dict.update(
            {
                "id": id,
                "role_id": role_id,
                "owner_type": owner_type,
                "name": name,
                "display_name": display_name,
                "status": status,
                "created_at": created_at,
            }
        )
        if owner_id is not UNSET:
            field_dict["owner_id"] = owner_id
        if description is not UNSET:
            field_dict["description"] = description
        if membership_rules is not UNSET:
            field_dict["membership_rules"] = membership_rules
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

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        role_id = UUID(d.pop("role_id"))

        owner_type = check_group_owner_type_enum(d.pop("owner_type"))

        name = d.pop("name")

        display_name = d.pop("display_name")

        status = check_service_group_status_enum(d.pop("status"))

        created_at = isoparse(d.pop("created_at"))

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
        if isinstance(_group_type, Unset):
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
            role_id=role_id,
            owner_type=owner_type,
            name=name,
            display_name=display_name,
            status=status,
            created_at=created_at,
            owner_id=owner_id,
            description=description,
            membership_rules=membership_rules,
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
