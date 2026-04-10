from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.price_rule_lifecycle_status_enum import check_price_rule_lifecycle_status_enum
from ..models.price_rule_lifecycle_status_enum import PriceRuleLifecycleStatusEnum
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.price_rule_update_pricing_type_0 import PriceRuleUpdatePricingType0
  from ..models.price_rule_update_scope_type_0 import PriceRuleUpdateScopeType0





T = TypeVar("T", bound="PriceRuleUpdate")



@_attrs_define
class PriceRuleUpdate:
    """ Schema for updating a PriceRule.

     """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    service_groups: list[str] | None | Unset = UNSET
    requires_redemption: bool | None | Unset = UNSET
    scope: None | PriceRuleUpdateScopeType0 | Unset = UNSET
    pricing: None | PriceRuleUpdatePricingType0 | Unset = UNSET
    priority: int | None | Unset = UNSET
    status: None | PriceRuleLifecycleStatusEnum | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.price_rule_update_pricing_type_0 import PriceRuleUpdatePricingType0
        from ..models.price_rule_update_scope_type_0 import PriceRuleUpdateScopeType0
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        service_groups: list[str] | None | Unset
        if isinstance(self.service_groups, Unset):
            service_groups = UNSET
        elif isinstance(self.service_groups, list):
            service_groups = self.service_groups


        else:
            service_groups = self.service_groups

        requires_redemption: bool | None | Unset
        if isinstance(self.requires_redemption, Unset):
            requires_redemption = UNSET
        else:
            requires_redemption = self.requires_redemption

        scope: dict[str, Any] | None | Unset
        if isinstance(self.scope, Unset):
            scope = UNSET
        elif isinstance(self.scope, PriceRuleUpdateScopeType0):
            scope = self.scope.to_dict()
        else:
            scope = self.scope

        pricing: dict[str, Any] | None | Unset
        if isinstance(self.pricing, Unset):
            pricing = UNSET
        elif isinstance(self.pricing, PriceRuleUpdatePricingType0):
            pricing = self.pricing.to_dict()
        else:
            pricing = self.pricing

        priority: int | None | Unset
        if isinstance(self.priority, Unset):
            priority = UNSET
        else:
            priority = self.priority

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, str):
            status = self.status
        else:
            status = self.status


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if service_groups is not UNSET:
            field_dict["service_groups"] = service_groups
        if requires_redemption is not UNSET:
            field_dict["requires_redemption"] = requires_redemption
        if scope is not UNSET:
            field_dict["scope"] = scope
        if pricing is not UNSET:
            field_dict["pricing"] = pricing
        if priority is not UNSET:
            field_dict["priority"] = priority
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.price_rule_update_pricing_type_0 import PriceRuleUpdatePricingType0
        from ..models.price_rule_update_scope_type_0 import PriceRuleUpdateScopeType0
        d = dict(src_dict)
        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))


        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_service_groups(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                service_groups_type_0 = cast(list[str], data)

                return service_groups_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        service_groups = _parse_service_groups(d.pop("service_groups", UNSET))


        def _parse_requires_redemption(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        requires_redemption = _parse_requires_redemption(d.pop("requires_redemption", UNSET))


        def _parse_scope(data: object) -> None | PriceRuleUpdateScopeType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scope_type_0 = PriceRuleUpdateScopeType0.from_dict(data)



                return scope_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PriceRuleUpdateScopeType0 | Unset, data)

        scope = _parse_scope(d.pop("scope", UNSET))


        def _parse_pricing(data: object) -> None | PriceRuleUpdatePricingType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                pricing_type_0 = PriceRuleUpdatePricingType0.from_dict(data)



                return pricing_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PriceRuleUpdatePricingType0 | Unset, data)

        pricing = _parse_pricing(d.pop("pricing", UNSET))


        def _parse_priority(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        priority = _parse_priority(d.pop("priority", UNSET))


        def _parse_status(data: object) -> None | PriceRuleLifecycleStatusEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = check_price_rule_lifecycle_status_enum(data)



                return status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PriceRuleLifecycleStatusEnum | Unset, data)

        status = _parse_status(d.pop("status", UNSET))


        price_rule_update = cls(
            name=name,
            description=description,
            service_groups=service_groups,
            requires_redemption=requires_redemption,
            scope=scope,
            pricing=pricing,
            priority=priority,
            status=status,
        )


        price_rule_update.additional_properties = d
        return price_rule_update

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
