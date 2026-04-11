from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.price_rule_apply_at_enum import check_price_rule_apply_at_enum
from ..models.price_rule_apply_at_enum import PriceRuleApplyAtEnum
from ..models.price_rule_source_enum import check_price_rule_source_enum
from ..models.price_rule_source_enum import PriceRuleSourceEnum
from ..models.price_rule_status_enum import check_price_rule_status_enum
from ..models.price_rule_status_enum import PriceRuleStatusEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.price_rule_pricing_spec import PriceRulePricingSpec
  from ..models.price_rule_public_scope_type_0 import PriceRulePublicScopeType0





T = TypeVar("T", bound="PriceRulePublic")



@_attrs_define
class PriceRulePublic:
    """ Public schema for PriceRule API responses.

     """

    name: str
    """ Display name of the price rule """
    source: PriceRuleSourceEnum
    """ Source of code matching for price rules. """
    code: str
    """ The code to match (e.g., 'pro', 'BF2025') """
    pricing: PriceRulePricingSpec
    """ Pricing specification (percentage, fixed_amount, graduated, etc.) """
    id: UUID
    created_by_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: None | str | Unset = UNSET
    """ Optional description """
    service_groups: list[str] | None | Unset = UNSET
    """ Service group UUIDs this rule applies to. null = all services. """
    apply_at: PriceRuleApplyAtEnum | Unset = UNSET
    """ When the price rule is applied. """
    priority: int | Unset = 0
    """ Higher priority rules are applied first """
    status: PriceRuleStatusEnum | Unset = UNSET
    """ Seller-facing status values for promotions.

    The backend may define additional statuses (scheduled, expired,
    cancelled) for internal lifecycle management, but sellers only
    interact with these three. """
    requires_redemption: bool | Unset = True
    """ Derived from scope: False when scope.customers is '*' or omitted """
    scope: None | PriceRulePublicScopeType0 | Unset = UNSET
    """ Customer and service targeting (null = all customers, all services) """
    seller_id: None | Unset | UUID = UNSET
    """ Seller ID for seller-funded promotions (None = platform rule) """





    def to_dict(self) -> dict[str, Any]:
        from ..models.price_rule_pricing_spec import PriceRulePricingSpec
        from ..models.price_rule_public_scope_type_0 import PriceRulePublicScopeType0
        name = self.name

        source: str = self.source

        code = self.code

        pricing = self.pricing.to_dict()

        id = str(self.id)

        created_by_id = str(self.created_by_id)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

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

        apply_at: str | Unset = UNSET
        if not isinstance(self.apply_at, Unset):
            apply_at = self.apply_at


        priority = self.priority

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status


        requires_redemption = self.requires_redemption

        scope: dict[str, Any] | None | Unset
        if isinstance(self.scope, Unset):
            scope = UNSET
        elif isinstance(self.scope, PriceRulePublicScopeType0):
            scope = self.scope.to_dict()
        else:
            scope = self.scope

        seller_id: None | str | Unset
        if isinstance(self.seller_id, Unset):
            seller_id = UNSET
        elif isinstance(self.seller_id, UUID):
            seller_id = str(self.seller_id)
        else:
            seller_id = self.seller_id


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "name": name,
            "source": source,
            "code": code,
            "pricing": pricing,
            "id": id,
            "created_by_id": created_by_id,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if service_groups is not UNSET:
            field_dict["service_groups"] = service_groups
        if apply_at is not UNSET:
            field_dict["apply_at"] = apply_at
        if priority is not UNSET:
            field_dict["priority"] = priority
        if status is not UNSET:
            field_dict["status"] = status
        if requires_redemption is not UNSET:
            field_dict["requires_redemption"] = requires_redemption
        if scope is not UNSET:
            field_dict["scope"] = scope
        if seller_id is not UNSET:
            field_dict["seller_id"] = seller_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.price_rule_pricing_spec import PriceRulePricingSpec
        from ..models.price_rule_public_scope_type_0 import PriceRulePublicScopeType0
        d = dict(src_dict)
        name = d.pop("name")

        source = check_price_rule_source_enum(d.pop("source"))




        code = d.pop("code")

        pricing = PriceRulePricingSpec.from_dict(d.pop("pricing"))




        id = UUID(d.pop("id"))




        created_by_id = UUID(d.pop("created_by_id"))




        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




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


        _apply_at = d.pop("apply_at", UNSET)
        apply_at: PriceRuleApplyAtEnum | Unset
        if isinstance(_apply_at,  Unset):
            apply_at = UNSET
        else:
            apply_at = check_price_rule_apply_at_enum(_apply_at)




        priority = d.pop("priority", UNSET)

        _status = d.pop("status", UNSET)
        status: PriceRuleStatusEnum | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_price_rule_status_enum(_status)




        requires_redemption = d.pop("requires_redemption", UNSET)

        def _parse_scope(data: object) -> None | PriceRulePublicScopeType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scope_type_0 = PriceRulePublicScopeType0.from_dict(data)



                return scope_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PriceRulePublicScopeType0 | Unset, data)

        scope = _parse_scope(d.pop("scope", UNSET))


        def _parse_seller_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                seller_id_type_0 = UUID(data)



                return seller_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        seller_id = _parse_seller_id(d.pop("seller_id", UNSET))


        price_rule_public = cls(
            name=name,
            source=source,
            code=code,
            pricing=pricing,
            id=id,
            created_by_id=created_by_id,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            service_groups=service_groups,
            apply_at=apply_at,
            priority=priority,
            status=status,
            requires_redemption=requires_redemption,
            scope=scope,
            seller_id=seller_id,
        )

        return price_rule_public

