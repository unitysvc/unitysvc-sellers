from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.service_alias_update_request_routing_key_type_0 import ServiceAliasUpdateRequestRoutingKeyType0
  from ..models.service_alias_update_routing_key_override_type_0 import ServiceAliasUpdateRoutingKeyOverrideType0





T = TypeVar("T", bound="ServiceAliasUpdate")



@_attrs_define
class ServiceAliasUpdate:
    """ Schema for updating a ServiceAlias.

    The alias name cannot be changed (it's the URL path segment).
    All other fields — including request_routing_key — are updatable.
    A unique constraint check runs at save time; conflicts return 409.

     """

    description: None | str | Unset = UNSET
    request_routing_key: None | ServiceAliasUpdateRequestRoutingKeyType0 | Unset = UNSET
    target_path: None | str | Unset = UNSET
    routing_key_override: None | ServiceAliasUpdateRoutingKeyOverrideType0 | Unset = UNSET
    is_routing: bool | None | Unset = UNSET
    """ Flip the routing state. Setting this to True will automatically demote any other alias currently routing the
    same (name, routing_key) combo. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_alias_update_request_routing_key_type_0 import ServiceAliasUpdateRequestRoutingKeyType0
        from ..models.service_alias_update_routing_key_override_type_0 import ServiceAliasUpdateRoutingKeyOverrideType0
        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        request_routing_key: dict[str, Any] | None | Unset
        if isinstance(self.request_routing_key, Unset):
            request_routing_key = UNSET
        elif isinstance(self.request_routing_key, ServiceAliasUpdateRequestRoutingKeyType0):
            request_routing_key = self.request_routing_key.to_dict()
        else:
            request_routing_key = self.request_routing_key

        target_path: None | str | Unset
        if isinstance(self.target_path, Unset):
            target_path = UNSET
        else:
            target_path = self.target_path

        routing_key_override: dict[str, Any] | None | Unset
        if isinstance(self.routing_key_override, Unset):
            routing_key_override = UNSET
        elif isinstance(self.routing_key_override, ServiceAliasUpdateRoutingKeyOverrideType0):
            routing_key_override = self.routing_key_override.to_dict()
        else:
            routing_key_override = self.routing_key_override

        is_routing: bool | None | Unset
        if isinstance(self.is_routing, Unset):
            is_routing = UNSET
        else:
            is_routing = self.is_routing


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if description is not UNSET:
            field_dict["description"] = description
        if request_routing_key is not UNSET:
            field_dict["request_routing_key"] = request_routing_key
        if target_path is not UNSET:
            field_dict["target_path"] = target_path
        if routing_key_override is not UNSET:
            field_dict["routing_key_override"] = routing_key_override
        if is_routing is not UNSET:
            field_dict["is_routing"] = is_routing

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_alias_update_request_routing_key_type_0 import ServiceAliasUpdateRequestRoutingKeyType0
        from ..models.service_alias_update_routing_key_override_type_0 import ServiceAliasUpdateRoutingKeyOverrideType0
        d = dict(src_dict)
        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_request_routing_key(data: object) -> None | ServiceAliasUpdateRequestRoutingKeyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                request_routing_key_type_0 = ServiceAliasUpdateRequestRoutingKeyType0.from_dict(data)



                return request_routing_key_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceAliasUpdateRequestRoutingKeyType0 | Unset, data)

        request_routing_key = _parse_request_routing_key(d.pop("request_routing_key", UNSET))


        def _parse_target_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        target_path = _parse_target_path(d.pop("target_path", UNSET))


        def _parse_routing_key_override(data: object) -> None | ServiceAliasUpdateRoutingKeyOverrideType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_override_type_0 = ServiceAliasUpdateRoutingKeyOverrideType0.from_dict(data)



                return routing_key_override_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceAliasUpdateRoutingKeyOverrideType0 | Unset, data)

        routing_key_override = _parse_routing_key_override(d.pop("routing_key_override", UNSET))


        def _parse_is_routing(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_routing = _parse_is_routing(d.pop("is_routing", UNSET))


        service_alias_update = cls(
            description=description,
            request_routing_key=request_routing_key,
            target_path=target_path,
            routing_key_override=routing_key_override,
            is_routing=is_routing,
        )


        service_alias_update.additional_properties = d
        return service_alias_update

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
