from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.service_alias_create_request_routing_key import ServiceAliasCreateRequestRoutingKey
  from ..models.service_alias_create_routing_key_override_type_0 import ServiceAliasCreateRoutingKeyOverrideType0





T = TypeVar("T", bound="ServiceAliasCreate")



@_attrs_define
class ServiceAliasCreate:
    """ Schema for creating a ServiceAlias.

     """

    name: str
    """ URL-safe alias name (lowercase, alphanumeric, hyphens, underscores) """
    target_path: str
    """ Target path (e.g. 'p/openai' or 'g/my-llm-group') """
    description: None | str | Unset = UNSET
    request_routing_key: ServiceAliasCreateRequestRoutingKey | Unset = UNSET
    is_routing: bool | Unset = True
    """ Whether to make this alias the active routing one for its (name, routing_key) combo. Fails with 409 if
    another alias is already routing. """
    routing_key_override: None | ServiceAliasCreateRoutingKeyOverrideType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_alias_create_request_routing_key import ServiceAliasCreateRequestRoutingKey
        from ..models.service_alias_create_routing_key_override_type_0 import ServiceAliasCreateRoutingKeyOverrideType0
        name = self.name

        target_path = self.target_path

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        request_routing_key: dict[str, Any] | Unset = UNSET
        if not isinstance(self.request_routing_key, Unset):
            request_routing_key = self.request_routing_key.to_dict()

        is_routing = self.is_routing

        routing_key_override: dict[str, Any] | None | Unset
        if isinstance(self.routing_key_override, Unset):
            routing_key_override = UNSET
        elif isinstance(self.routing_key_override, ServiceAliasCreateRoutingKeyOverrideType0):
            routing_key_override = self.routing_key_override.to_dict()
        else:
            routing_key_override = self.routing_key_override


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "target_path": target_path,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if request_routing_key is not UNSET:
            field_dict["request_routing_key"] = request_routing_key
        if is_routing is not UNSET:
            field_dict["is_routing"] = is_routing
        if routing_key_override is not UNSET:
            field_dict["routing_key_override"] = routing_key_override

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_alias_create_request_routing_key import ServiceAliasCreateRequestRoutingKey
        from ..models.service_alias_create_routing_key_override_type_0 import ServiceAliasCreateRoutingKeyOverrideType0
        d = dict(src_dict)
        name = d.pop("name")

        target_path = d.pop("target_path")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        _request_routing_key = d.pop("request_routing_key", UNSET)
        request_routing_key: ServiceAliasCreateRequestRoutingKey | Unset
        if isinstance(_request_routing_key,  Unset):
            request_routing_key = UNSET
        else:
            request_routing_key = ServiceAliasCreateRequestRoutingKey.from_dict(_request_routing_key)




        is_routing = d.pop("is_routing", UNSET)

        def _parse_routing_key_override(data: object) -> None | ServiceAliasCreateRoutingKeyOverrideType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_override_type_0 = ServiceAliasCreateRoutingKeyOverrideType0.from_dict(data)



                return routing_key_override_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceAliasCreateRoutingKeyOverrideType0 | Unset, data)

        routing_key_override = _parse_routing_key_override(d.pop("routing_key_override", UNSET))


        service_alias_create = cls(
            name=name,
            target_path=target_path,
            description=description,
            request_routing_key=request_routing_key,
            is_routing=is_routing,
            routing_key_override=routing_key_override,
        )


        service_alias_create.additional_properties = d
        return service_alias_create

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
