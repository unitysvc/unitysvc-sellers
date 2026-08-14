from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group_service_member_routing_key_type_0 import GroupServiceMemberRoutingKeyType0


T = TypeVar("T", bound="GroupServiceMember")


@_attrs_define
class GroupServiceMember:
    """One explicitly-listed member of a manually-curated service group
    (unitysvc#1733).

    ``name`` is the member service's stable name (the same handle rules match on).
    ``routing_key`` is loaded straight into ``ServiceGroupMembership.routing_key``
    — specify it only when the member should be addressed by a key that differs
    from its native one; omit it (``None``) to keep the service's own key. Catalog
    (rule-based) groups don't use this at all — their members are keyless.

    """

    name: str
    routing_key: GroupServiceMemberRoutingKeyType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.group_service_member_routing_key_type_0 import GroupServiceMemberRoutingKeyType0

        name = self.name

        routing_key: dict[str, Any] | None | Unset
        if isinstance(self.routing_key, Unset):
            routing_key = UNSET
        elif isinstance(self.routing_key, GroupServiceMemberRoutingKeyType0):
            routing_key = self.routing_key.to_dict()
        else:
            routing_key = self.routing_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if routing_key is not UNSET:
            field_dict["routing_key"] = routing_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group_service_member_routing_key_type_0 import GroupServiceMemberRoutingKeyType0

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_routing_key(data: object) -> GroupServiceMemberRoutingKeyType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_type_0 = GroupServiceMemberRoutingKeyType0.from_dict(data)

                return routing_key_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GroupServiceMemberRoutingKeyType0 | None | Unset, data)

        routing_key = _parse_routing_key(d.pop("routing_key", UNSET))

        group_service_member = cls(
            name=name,
            routing_key=routing_key,
        )

        group_service_member.additional_properties = d
        return group_service_member

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
