from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.access_method_enum import AccessMethodEnum, check_access_method_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_interface_public_routing_key_type_0 import AccessInterfacePublicRoutingKeyType0


T = TypeVar("T", bound="AccessInterfacePublic")


@_attrs_define
class AccessInterfacePublic:
    """Public AccessInterface model for API responses."""

    id: UUID
    access_method: AccessMethodEnum
    name: str
    is_active: bool
    is_primary: bool
    sort_order: int
    created_at: str
    service_id: None | Unset | UUID = UNSET
    base_url: None | str | Unset = UNSET
    base_url_pattern: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    routing_key: AccessInterfacePublicRoutingKeyType0 | None | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_interface_public_routing_key_type_0 import AccessInterfacePublicRoutingKeyType0

        id = str(self.id)

        access_method: str = self.access_method

        name = self.name

        is_active = self.is_active

        is_primary = self.is_primary

        sort_order = self.sort_order

        created_at = self.created_at

        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

        base_url: None | str | Unset
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        base_url_pattern: None | str | Unset
        if isinstance(self.base_url_pattern, Unset):
            base_url_pattern = UNSET
        else:
            base_url_pattern = self.base_url_pattern

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        routing_key: dict[str, Any] | None | Unset
        if isinstance(self.routing_key, Unset):
            routing_key = UNSET
        elif isinstance(self.routing_key, AccessInterfacePublicRoutingKeyType0):
            routing_key = self.routing_key.to_dict()
        else:
            routing_key = self.routing_key

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "access_method": access_method,
                "name": name,
                "is_active": is_active,
                "is_primary": is_primary,
                "sort_order": sort_order,
                "created_at": created_at,
            }
        )
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if base_url_pattern is not UNSET:
            field_dict["base_url_pattern"] = base_url_pattern
        if description is not UNSET:
            field_dict["description"] = description
        if routing_key is not UNSET:
            field_dict["routing_key"] = routing_key
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_interface_public_routing_key_type_0 import AccessInterfacePublicRoutingKeyType0

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        access_method = check_access_method_enum(d.pop("access_method"))

        name = d.pop("name")

        is_active = d.pop("is_active")

        is_primary = d.pop("is_primary")

        sort_order = d.pop("sort_order")

        created_at = d.pop("created_at")

        def _parse_service_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_id_type_0 = UUID(data)

                return service_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        service_id = _parse_service_id(d.pop("service_id", UNSET))

        def _parse_base_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))

        def _parse_base_url_pattern(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_url_pattern = _parse_base_url_pattern(d.pop("base_url_pattern", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_routing_key(data: object) -> AccessInterfacePublicRoutingKeyType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_type_0 = AccessInterfacePublicRoutingKeyType0.from_dict(data)

                return routing_key_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AccessInterfacePublicRoutingKeyType0 | None | Unset, data)

        routing_key = _parse_routing_key(d.pop("routing_key", UNSET))

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        access_interface_public = cls(
            id=id,
            access_method=access_method,
            name=name,
            is_active=is_active,
            is_primary=is_primary,
            sort_order=sort_order,
            created_at=created_at,
            service_id=service_id,
            base_url=base_url,
            base_url_pattern=base_url_pattern,
            description=description,
            routing_key=routing_key,
            updated_at=updated_at,
        )

        access_interface_public.additional_properties = d
        return access_interface_public

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
