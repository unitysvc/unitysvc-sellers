from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.access_method_enum import AccessMethodEnum
from ..models.access_method_enum import check_access_method_enum
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID

if TYPE_CHECKING:
  from ..models.access_interface_public_routing_key_type_0 import AccessInterfacePublicRoutingKeyType0
  from ..models.service_constraints import ServiceConstraints
  from ..models.access_interface_public_request_transformer_type_0 import AccessInterfacePublicRequestTransformerType0
  from ..models.rate_limit import RateLimit
  from ..models.access_interface_public_response_rules_type_0 import AccessInterfacePublicResponseRulesType0





T = TypeVar("T", bound="AccessInterfacePublic")



@_attrs_define
class AccessInterfacePublic:
    """ Public AccessInterface model for API responses.

     """

    id: UUID
    access_method: AccessMethodEnum
    name: str
    is_active: bool
    is_primary: bool
    sort_order: int
    created_at: str
    service_id: Union[None, UUID, Unset] = UNSET
    group_id: Union[None, UUID, Unset] = UNSET
    has_api_key: Union[Unset, bool] = False
    base_url: Union[None, Unset, str] = UNSET
    base_url_pattern: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    request_transformer: Union['AccessInterfacePublicRequestTransformerType0', None, Unset] = UNSET
    rate_limits: Union[None, Unset, list['RateLimit']] = UNSET
    constraint: Union['ServiceConstraints', None, Unset] = UNSET
    response_rules: Union['AccessInterfacePublicResponseRulesType0', None, Unset] = UNSET
    routing_key: Union['AccessInterfacePublicRoutingKeyType0', None, Unset] = UNSET
    enrollment_id: Union[None, UUID, Unset] = UNSET
    updated_at: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.access_interface_public_routing_key_type_0 import AccessInterfacePublicRoutingKeyType0
        from ..models.service_constraints import ServiceConstraints
        from ..models.access_interface_public_request_transformer_type_0 import AccessInterfacePublicRequestTransformerType0
        from ..models.rate_limit import RateLimit
        from ..models.access_interface_public_response_rules_type_0 import AccessInterfacePublicResponseRulesType0
        id = str(self.id)

        access_method: str = self.access_method

        name = self.name

        is_active = self.is_active

        is_primary = self.is_primary

        sort_order = self.sort_order

        created_at = self.created_at

        service_id: Union[None, Unset, str]
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

        group_id: Union[None, Unset, str]
        if isinstance(self.group_id, Unset):
            group_id = UNSET
        elif isinstance(self.group_id, UUID):
            group_id = str(self.group_id)
        else:
            group_id = self.group_id

        has_api_key = self.has_api_key

        base_url: Union[None, Unset, str]
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        base_url_pattern: Union[None, Unset, str]
        if isinstance(self.base_url_pattern, Unset):
            base_url_pattern = UNSET
        else:
            base_url_pattern = self.base_url_pattern

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        request_transformer: Union[None, Unset, dict[str, Any]]
        if isinstance(self.request_transformer, Unset):
            request_transformer = UNSET
        elif isinstance(self.request_transformer, AccessInterfacePublicRequestTransformerType0):
            request_transformer = self.request_transformer.to_dict()
        else:
            request_transformer = self.request_transformer

        rate_limits: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.rate_limits, Unset):
            rate_limits = UNSET
        elif isinstance(self.rate_limits, list):
            rate_limits = []
            for rate_limits_type_0_item_data in self.rate_limits:
                rate_limits_type_0_item = rate_limits_type_0_item_data.to_dict()
                rate_limits.append(rate_limits_type_0_item)


        else:
            rate_limits = self.rate_limits

        constraint: Union[None, Unset, dict[str, Any]]
        if isinstance(self.constraint, Unset):
            constraint = UNSET
        elif isinstance(self.constraint, ServiceConstraints):
            constraint = self.constraint.to_dict()
        else:
            constraint = self.constraint

        response_rules: Union[None, Unset, dict[str, Any]]
        if isinstance(self.response_rules, Unset):
            response_rules = UNSET
        elif isinstance(self.response_rules, AccessInterfacePublicResponseRulesType0):
            response_rules = self.response_rules.to_dict()
        else:
            response_rules = self.response_rules

        routing_key: Union[None, Unset, dict[str, Any]]
        if isinstance(self.routing_key, Unset):
            routing_key = UNSET
        elif isinstance(self.routing_key, AccessInterfacePublicRoutingKeyType0):
            routing_key = self.routing_key.to_dict()
        else:
            routing_key = self.routing_key

        enrollment_id: Union[None, Unset, str]
        if isinstance(self.enrollment_id, Unset):
            enrollment_id = UNSET
        elif isinstance(self.enrollment_id, UUID):
            enrollment_id = str(self.enrollment_id)
        else:
            enrollment_id = self.enrollment_id

        updated_at: Union[None, Unset, str]
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "access_method": access_method,
            "name": name,
            "is_active": is_active,
            "is_primary": is_primary,
            "sort_order": sort_order,
            "created_at": created_at,
        })
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if has_api_key is not UNSET:
            field_dict["has_api_key"] = has_api_key
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if base_url_pattern is not UNSET:
            field_dict["base_url_pattern"] = base_url_pattern
        if description is not UNSET:
            field_dict["description"] = description
        if request_transformer is not UNSET:
            field_dict["request_transformer"] = request_transformer
        if rate_limits is not UNSET:
            field_dict["rate_limits"] = rate_limits
        if constraint is not UNSET:
            field_dict["constraint"] = constraint
        if response_rules is not UNSET:
            field_dict["response_rules"] = response_rules
        if routing_key is not UNSET:
            field_dict["routing_key"] = routing_key
        if enrollment_id is not UNSET:
            field_dict["enrollment_id"] = enrollment_id
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_interface_public_routing_key_type_0 import AccessInterfacePublicRoutingKeyType0
        from ..models.service_constraints import ServiceConstraints
        from ..models.access_interface_public_request_transformer_type_0 import AccessInterfacePublicRequestTransformerType0
        from ..models.rate_limit import RateLimit
        from ..models.access_interface_public_response_rules_type_0 import AccessInterfacePublicResponseRulesType0
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        access_method = check_access_method_enum(d.pop("access_method"))




        name = d.pop("name")

        is_active = d.pop("is_active")

        is_primary = d.pop("is_primary")

        sort_order = d.pop("sort_order")

        created_at = d.pop("created_at")

        def _parse_service_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_id_type_0 = UUID(data)



                return service_id_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        service_id = _parse_service_id(d.pop("service_id", UNSET))


        def _parse_group_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                group_id_type_0 = UUID(data)



                return group_id_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        group_id = _parse_group_id(d.pop("group_id", UNSET))


        has_api_key = d.pop("has_api_key", UNSET)

        def _parse_base_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))


        def _parse_base_url_pattern(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        base_url_pattern = _parse_base_url_pattern(d.pop("base_url_pattern", UNSET))


        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_request_transformer(data: object) -> Union['AccessInterfacePublicRequestTransformerType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                request_transformer_type_0 = AccessInterfacePublicRequestTransformerType0.from_dict(data)



                return request_transformer_type_0
            except: # noqa: E722
                pass
            return cast(Union['AccessInterfacePublicRequestTransformerType0', None, Unset], data)

        request_transformer = _parse_request_transformer(d.pop("request_transformer", UNSET))


        def _parse_rate_limits(data: object) -> Union[None, Unset, list['RateLimit']]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                rate_limits_type_0 = []
                _rate_limits_type_0 = data
                for rate_limits_type_0_item_data in (_rate_limits_type_0):
                    rate_limits_type_0_item = RateLimit.from_dict(rate_limits_type_0_item_data)



                    rate_limits_type_0.append(rate_limits_type_0_item)

                return rate_limits_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, list['RateLimit']], data)

        rate_limits = _parse_rate_limits(d.pop("rate_limits", UNSET))


        def _parse_constraint(data: object) -> Union['ServiceConstraints', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                constraint_type_0 = ServiceConstraints.from_dict(data)



                return constraint_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceConstraints', None, Unset], data)

        constraint = _parse_constraint(d.pop("constraint", UNSET))


        def _parse_response_rules(data: object) -> Union['AccessInterfacePublicResponseRulesType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_rules_type_0 = AccessInterfacePublicResponseRulesType0.from_dict(data)



                return response_rules_type_0
            except: # noqa: E722
                pass
            return cast(Union['AccessInterfacePublicResponseRulesType0', None, Unset], data)

        response_rules = _parse_response_rules(d.pop("response_rules", UNSET))


        def _parse_routing_key(data: object) -> Union['AccessInterfacePublicRoutingKeyType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_key_type_0 = AccessInterfacePublicRoutingKeyType0.from_dict(data)



                return routing_key_type_0
            except: # noqa: E722
                pass
            return cast(Union['AccessInterfacePublicRoutingKeyType0', None, Unset], data)

        routing_key = _parse_routing_key(d.pop("routing_key", UNSET))


        def _parse_enrollment_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                enrollment_id_type_0 = UUID(data)



                return enrollment_id_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        enrollment_id = _parse_enrollment_id(d.pop("enrollment_id", UNSET))


        def _parse_updated_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

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
            group_id=group_id,
            has_api_key=has_api_key,
            base_url=base_url,
            base_url_pattern=base_url_pattern,
            description=description,
            request_transformer=request_transformer,
            rate_limits=rate_limits,
            constraint=constraint,
            response_rules=response_rules,
            routing_key=routing_key,
            enrollment_id=enrollment_id,
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
