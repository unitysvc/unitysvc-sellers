from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.price_rule_apply_at_enum import check_price_rule_apply_at_enum
from ..models.price_rule_apply_at_enum import PriceRuleApplyAtEnum
from ..models.price_rule_lifecycle_status_enum import check_price_rule_lifecycle_status_enum
from ..models.price_rule_lifecycle_status_enum import PriceRuleLifecycleStatusEnum
from ..models.price_rule_source_enum import check_price_rule_source_enum
from ..models.price_rule_source_enum import PriceRuleSourceEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.price_rule_create_pricing import PriceRuleCreatePricing
  from ..models.price_rule_create_scope_type_0 import PriceRuleCreateScopeType0





T = TypeVar("T", bound="PriceRuleCreate")



@_attrs_define
class PriceRuleCreate:
    """ Schema for creating a new PriceRule.

    For pricing_code source, expires_at and max_uses control the ActionCode.

     """

    name: str
    """ Display name of the price rule """
    source: PriceRuleSourceEnum
    """ Source of code matching for price rules. """
    code: str
    """ The code to match (e.g., 'pro', 'BF2025') """
    pricing: PriceRuleCreatePricing
    """ Pricing specification (percentage, fixed_amount, graduated, etc.) """
    description: None | str | Unset = UNSET
    """ Optional description """
    service_groups: list[str] | None | Unset = UNSET
    """ Service group UUIDs this rule applies to. null = all services. """
    apply_at: PriceRuleApplyAtEnum | Unset = UNSET
    """ When the price rule is applied. """
    priority: int | Unset = 0
    """ Higher priority rules are applied first """
    status: PriceRuleLifecycleStatusEnum | Unset = UNSET
    """ Status of a price rule in its lifecycle. """
    requires_redemption: bool | Unset = True
    """ Derived from scope: False when scope.customers is '*' or omitted """
    scope: None | PriceRuleCreateScopeType0 | Unset = UNSET
    """ Customer and service targeting (null = all customers, all services) """
    seller_id: None | Unset | UUID = UNSET
    """ Seller ID for seller-funded promotions (None = platform rule) """
    expires_at: datetime.datetime | None | Unset = UNSET
    """ When the pricing code expires (pricing_code source only) """
    max_uses: int | None | Unset = UNSET
    """ Maximum total redemptions (pricing_code source only) """





    def to_dict(self) -> dict[str, Any]:
        from ..models.price_rule_create_pricing import PriceRuleCreatePricing
        from ..models.price_rule_create_scope_type_0 import PriceRuleCreateScopeType0
        name = self.name

        source: str = self.source

        code = self.code

        pricing = self.pricing.to_dict()

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
        elif isinstance(self.scope, PriceRuleCreateScopeType0):
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

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        max_uses: int | None | Unset
        if isinstance(self.max_uses, Unset):
            max_uses = UNSET
        else:
            max_uses = self.max_uses


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "name": name,
            "source": source,
            "code": code,
            "pricing": pricing,
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
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if max_uses is not UNSET:
            field_dict["max_uses"] = max_uses

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.price_rule_create_pricing import PriceRuleCreatePricing
        from ..models.price_rule_create_scope_type_0 import PriceRuleCreateScopeType0
        d = dict(src_dict)
        name = d.pop("name")

        source = check_price_rule_source_enum(d.pop("source"))




        code = d.pop("code")

        pricing = PriceRuleCreatePricing.from_dict(d.pop("pricing"))




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
        status: PriceRuleLifecycleStatusEnum | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_price_rule_lifecycle_status_enum(_status)




        requires_redemption = d.pop("requires_redemption", UNSET)

        def _parse_scope(data: object) -> None | PriceRuleCreateScopeType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scope_type_0 = PriceRuleCreateScopeType0.from_dict(data)



                return scope_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PriceRuleCreateScopeType0 | Unset, data)

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


        def _parse_expires_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)



                return expires_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))


        def _parse_max_uses(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_uses = _parse_max_uses(d.pop("max_uses", UNSET))


        price_rule_create = cls(
            name=name,
            source=source,
            code=code,
            pricing=pricing,
            description=description,
            service_groups=service_groups,
            apply_at=apply_at,
            priority=priority,
            status=status,
            requires_redemption=requires_redemption,
            scope=scope,
            seller_id=seller_id,
            expires_at=expires_at,
            max_uses=max_uses,
        )

        return price_rule_create

