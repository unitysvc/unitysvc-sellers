from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

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
from typing import cast, Union
from typing import Union
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.price_rule_public_scope_type_0 import PriceRulePublicScopeType0
  from ..models.price_rule_pricing_spec import PriceRulePricingSpec





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
    pricing: 'PriceRulePricingSpec'
    """ Pricing specification (percentage, fixed_amount, graduated, etc.) """
    id: UUID
    created_by_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: Union[None, Unset, str] = UNSET
    """ Optional description """
    service_groups: Union[None, Unset, list[str]] = UNSET
    """ Service group UUIDs this rule applies to. null = all services. """
    apply_at: Union[Unset, PriceRuleApplyAtEnum] = UNSET
    """ When the price rule is applied. """
    priority: Union[Unset, int] = 0
    """ Higher priority rules are applied first """
    status: Union[Unset, PriceRuleStatusEnum] = UNSET
    """ Seller-facing status values for promotions.

    The backend may define additional statuses (scheduled, expired,
    cancelled) for internal lifecycle management, but sellers only
    interact with these three. """
    requires_redemption: Union[Unset, bool] = True
    """ Derived from scope: False when scope.customers is '*' or omitted """
    scope: Union['PriceRulePublicScopeType0', None, Unset] = UNSET
    """ Customer and service targeting (null = all customers, all services) """
    seller_id: Union[None, UUID, Unset] = UNSET
    """ Seller ID for seller-funded promotions (None = platform rule) """





    def to_dict(self) -> dict[str, Any]:
        from ..models.price_rule_public_scope_type_0 import PriceRulePublicScopeType0
        from ..models.price_rule_pricing_spec import PriceRulePricingSpec
        name = self.name

        source: str = self.source

        code = self.code

        pricing = self.pricing.to_dict()

        id = str(self.id)

        created_by_id = str(self.created_by_id)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        service_groups: Union[None, Unset, list[str]]
        if isinstance(self.service_groups, Unset):
            service_groups = UNSET
        elif isinstance(self.service_groups, list):
            service_groups = self.service_groups


        else:
            service_groups = self.service_groups

        apply_at: Union[Unset, str] = UNSET
        if not isinstance(self.apply_at, Unset):
            apply_at = self.apply_at


        priority = self.priority

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status


        requires_redemption = self.requires_redemption

        scope: Union[None, Unset, dict[str, Any]]
        if isinstance(self.scope, Unset):
            scope = UNSET
        elif isinstance(self.scope, PriceRulePublicScopeType0):
            scope = self.scope.to_dict()
        else:
            scope = self.scope

        seller_id: Union[None, Unset, str]
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
        from ..models.price_rule_public_scope_type_0 import PriceRulePublicScopeType0
        from ..models.price_rule_pricing_spec import PriceRulePricingSpec
        d = dict(src_dict)
        name = d.pop("name")

        source = check_price_rule_source_enum(d.pop("source"))




        code = d.pop("code")

        pricing = PriceRulePricingSpec.from_dict(d.pop("pricing"))




        id = UUID(d.pop("id"))




        created_by_id = UUID(d.pop("created_by_id"))




        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_service_groups(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                service_groups_type_0 = cast(list[str], data)

                return service_groups_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        service_groups = _parse_service_groups(d.pop("service_groups", UNSET))


        _apply_at = d.pop("apply_at", UNSET)
        apply_at: Union[Unset, PriceRuleApplyAtEnum]
        if isinstance(_apply_at,  Unset):
            apply_at = UNSET
        else:
            apply_at = check_price_rule_apply_at_enum(_apply_at)




        priority = d.pop("priority", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, PriceRuleStatusEnum]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_price_rule_status_enum(_status)




        requires_redemption = d.pop("requires_redemption", UNSET)

        def _parse_scope(data: object) -> Union['PriceRulePublicScopeType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scope_type_0 = PriceRulePublicScopeType0.from_dict(data)



                return scope_type_0
            except: # noqa: E722
                pass
            return cast(Union['PriceRulePublicScopeType0', None, Unset], data)

        scope = _parse_scope(d.pop("scope", UNSET))


        def _parse_seller_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                seller_id_type_0 = UUID(data)



                return seller_id_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

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

