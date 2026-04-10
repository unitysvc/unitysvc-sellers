from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.billing_interval_enum import BillingIntervalEnum
from ..models.billing_interval_enum import check_billing_interval_enum
from ..models.pricing_plan_tier_enum import check_pricing_plan_tier_enum
from ..models.pricing_plan_tier_enum import PricingPlanTierEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID






T = TypeVar("T", bound="SubscriptionCreateRequest")



@_attrs_define
class SubscriptionCreateRequest:
    """ Request for creating a subscription.

     """

    customer_id: UUID
    """ Customer ID (created via POST /billing/setup-payment) """
    tier: PricingPlanTierEnum
    """ High-level usage plan tier categories. """
    billing_interval: BillingIntervalEnum | Unset = UNSET
    """ Billing cycle interval. """
    quantity: int | Unset = 1
    """ Number of seats (for per-seat plans) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        customer_id = str(self.customer_id)

        tier: str = self.tier

        billing_interval: str | Unset = UNSET
        if not isinstance(self.billing_interval, Unset):
            billing_interval = self.billing_interval


        quantity = self.quantity


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "customer_id": customer_id,
            "tier": tier,
        })
        if billing_interval is not UNSET:
            field_dict["billing_interval"] = billing_interval
        if quantity is not UNSET:
            field_dict["quantity"] = quantity

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        customer_id = UUID(d.pop("customer_id"))




        tier = check_pricing_plan_tier_enum(d.pop("tier"))




        _billing_interval = d.pop("billing_interval", UNSET)
        billing_interval: BillingIntervalEnum | Unset
        if isinstance(_billing_interval,  Unset):
            billing_interval = UNSET
        else:
            billing_interval = check_billing_interval_enum(_billing_interval)




        quantity = d.pop("quantity", UNSET)

        subscription_create_request = cls(
            customer_id=customer_id,
            tier=tier,
            billing_interval=billing_interval,
            quantity=quantity,
        )


        subscription_create_request.additional_properties = d
        return subscription_create_request

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
