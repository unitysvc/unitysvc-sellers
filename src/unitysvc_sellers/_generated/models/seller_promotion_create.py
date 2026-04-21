from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.price_rule_apply_at_enum import PriceRuleApplyAtEnum, check_price_rule_apply_at_enum
from ..models.price_rule_status_enum import PriceRuleStatusEnum, check_price_rule_status_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pricing import Pricing
    from ..models.seller_promotion_create_scope_type_0 import SellerPromotionCreateScopeType0


T = TypeVar("T", bound="SellerPromotionCreate")


@_attrs_define
class SellerPromotionCreate:
    """Schema for sellers creating a promotion.

    Inherits all fields from PromotionData (unitysvc-core).
    The backend auto-sets source=seller_code and seller_id from
    the authenticated user, and decomposes scope into internal fields
    (code, requires_redemption, service_groups,
    PriceRuleServiceTarget) during ingestion.

    """

    name: str
    """ Display name of the promotion (unique per seller) """
    pricing: Pricing
    """ Pricing specification (e.g., multiply, constant, add) """
    description: None | str | Unset = UNSET
    """ Human-readable description """
    scope: None | SellerPromotionCreateScopeType0 | Unset = UNSET
    """ Customer and service targeting. null = all customers, all services (blanket promotion). """
    apply_at: PriceRuleApplyAtEnum | Unset = UNSET
    """ When the price rule is applied. """
    priority: int | Unset = 0
    """ Higher priority rules are applied first """
    status: PriceRuleStatusEnum | Unset = UNSET
    """ Seller-facing status values for promotions.

    The backend may define additional statuses (scheduled, expired,
    cancelled) for internal lifecycle management, but sellers only
    interact with these three. """
    expires_at: datetime.datetime | None | Unset = UNSET
    """ When the promotion expires (code-based only) """
    max_uses: int | None | Unset = UNSET
    """ Maximum total redemptions (code-based only) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.seller_promotion_create_scope_type_0 import SellerPromotionCreateScopeType0

        name = self.name

        pricing = self.pricing.to_dict()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        scope: dict[str, Any] | None | Unset
        if isinstance(self.scope, Unset):
            scope = UNSET
        elif isinstance(self.scope, SellerPromotionCreateScopeType0):
            scope = self.scope.to_dict()
        else:
            scope = self.scope

        apply_at: str | Unset = UNSET
        if not isinstance(self.apply_at, Unset):
            apply_at = self.apply_at

        priority = self.priority

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

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
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "pricing": pricing,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if scope is not UNSET:
            field_dict["scope"] = scope
        if apply_at is not UNSET:
            field_dict["apply_at"] = apply_at
        if priority is not UNSET:
            field_dict["priority"] = priority
        if status is not UNSET:
            field_dict["status"] = status
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if max_uses is not UNSET:
            field_dict["max_uses"] = max_uses

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pricing import Pricing
        from ..models.seller_promotion_create_scope_type_0 import SellerPromotionCreateScopeType0

        d = dict(src_dict)
        name = d.pop("name")

        pricing = Pricing.from_dict(d.pop("pricing"))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_scope(data: object) -> None | SellerPromotionCreateScopeType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scope_type_0 = SellerPromotionCreateScopeType0.from_dict(data)

                return scope_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SellerPromotionCreateScopeType0 | Unset, data)

        scope = _parse_scope(d.pop("scope", UNSET))

        _apply_at = d.pop("apply_at", UNSET)
        apply_at: PriceRuleApplyAtEnum | Unset
        if isinstance(_apply_at, Unset):
            apply_at = UNSET
        else:
            apply_at = check_price_rule_apply_at_enum(_apply_at)

        priority = d.pop("priority", UNSET)

        _status = d.pop("status", UNSET)
        status: PriceRuleStatusEnum | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_price_rule_status_enum(_status)

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

        seller_promotion_create = cls(
            name=name,
            pricing=pricing,
            description=description,
            scope=scope,
            apply_at=apply_at,
            priority=priority,
            status=status,
            expires_at=expires_at,
            max_uses=max_uses,
        )

        seller_promotion_create.additional_properties = d
        return seller_promotion_create

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
