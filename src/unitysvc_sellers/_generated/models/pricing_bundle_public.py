from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.pricing_bundle_public_list_price import PricingBundlePublicListPrice
  from ..models.pricing_bundle_public_platform_price_rules_item import PricingBundlePublicPlatformPriceRulesItem
  from ..models.pricing_bundle_public_seller_price_rules_item import PricingBundlePublicSellerPriceRulesItem





T = TypeVar("T", bound="PricingBundlePublic")



@_attrs_define
class PricingBundlePublic:
    """ Public response schema for a pricing bundle.

     """

    id: UUID
    content_hash: str
    currency: str
    list_price: PricingBundlePublicListPrice
    seller_price_rules: list[PricingBundlePublicSellerPriceRulesItem]
    platform_price_rules: list[PricingBundlePublicPlatformPriceRulesItem]
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.pricing_bundle_public_list_price import PricingBundlePublicListPrice
        from ..models.pricing_bundle_public_platform_price_rules_item import PricingBundlePublicPlatformPriceRulesItem
        from ..models.pricing_bundle_public_seller_price_rules_item import PricingBundlePublicSellerPriceRulesItem
        id = str(self.id)

        content_hash = self.content_hash

        currency = self.currency

        list_price = self.list_price.to_dict()

        seller_price_rules = []
        for seller_price_rules_item_data in self.seller_price_rules:
            seller_price_rules_item = seller_price_rules_item_data.to_dict()
            seller_price_rules.append(seller_price_rules_item)



        platform_price_rules = []
        for platform_price_rules_item_data in self.platform_price_rules:
            platform_price_rules_item = platform_price_rules_item_data.to_dict()
            platform_price_rules.append(platform_price_rules_item)



        created_at = self.created_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "content_hash": content_hash,
            "currency": currency,
            "list_price": list_price,
            "seller_price_rules": seller_price_rules,
            "platform_price_rules": platform_price_rules,
            "created_at": created_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pricing_bundle_public_list_price import PricingBundlePublicListPrice
        from ..models.pricing_bundle_public_platform_price_rules_item import PricingBundlePublicPlatformPriceRulesItem
        from ..models.pricing_bundle_public_seller_price_rules_item import PricingBundlePublicSellerPriceRulesItem
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        content_hash = d.pop("content_hash")

        currency = d.pop("currency")

        list_price = PricingBundlePublicListPrice.from_dict(d.pop("list_price"))




        seller_price_rules = []
        _seller_price_rules = d.pop("seller_price_rules")
        for seller_price_rules_item_data in (_seller_price_rules):
            seller_price_rules_item = PricingBundlePublicSellerPriceRulesItem.from_dict(seller_price_rules_item_data)



            seller_price_rules.append(seller_price_rules_item)


        platform_price_rules = []
        _platform_price_rules = d.pop("platform_price_rules")
        for platform_price_rules_item_data in (_platform_price_rules):
            platform_price_rules_item = PricingBundlePublicPlatformPriceRulesItem.from_dict(platform_price_rules_item_data)



            platform_price_rules.append(platform_price_rules_item)


        created_at = isoparse(d.pop("created_at"))




        pricing_bundle_public = cls(
            id=id,
            content_hash=content_hash,
            currency=currency,
            list_price=list_price,
            seller_price_rules=seller_price_rules,
            platform_price_rules=platform_price_rules,
            created_at=created_at,
        )


        pricing_bundle_public.additional_properties = d
        return pricing_bundle_public

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
