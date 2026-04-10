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
from typing import cast
from uuid import UUID






T = TypeVar("T", bound="PlanPricingResponse")



@_attrs_define
class PlanPricingResponse:
    """ Response with plan pricing information.

     """

    plan_id: UUID
    """ Plan ID """
    plan_name: str
    """ Plan name """
    tier: PricingPlanTierEnum
    """ High-level usage plan tier categories. """
    base_amount: str
    """ Base price """
    quantity: int
    """ Number of seats """
    total_amount: str
    """ Total calculated price """
    currency: str
    """ Currency code (e.g., USD) """
    billing_interval: BillingIntervalEnum
    """ Billing cycle interval. """
    included_seats: int | None
    """ Seats included in base price (None=flat, 0=per-seat, N=tiered) """
    additional_seat_price: None | str
    """ Price per seat beyond included_seats """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        plan_id = str(self.plan_id)

        plan_name = self.plan_name

        tier: str = self.tier

        base_amount = self.base_amount

        quantity = self.quantity

        total_amount = self.total_amount

        currency = self.currency

        billing_interval: str = self.billing_interval

        included_seats: int | None
        included_seats = self.included_seats

        additional_seat_price: None | str
        additional_seat_price = self.additional_seat_price


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "plan_id": plan_id,
            "plan_name": plan_name,
            "tier": tier,
            "base_amount": base_amount,
            "quantity": quantity,
            "total_amount": total_amount,
            "currency": currency,
            "billing_interval": billing_interval,
            "included_seats": included_seats,
            "additional_seat_price": additional_seat_price,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        plan_id = UUID(d.pop("plan_id"))




        plan_name = d.pop("plan_name")

        tier = check_pricing_plan_tier_enum(d.pop("tier"))




        base_amount = d.pop("base_amount")

        quantity = d.pop("quantity")

        total_amount = d.pop("total_amount")

        currency = d.pop("currency")

        billing_interval = check_billing_interval_enum(d.pop("billing_interval"))




        def _parse_included_seats(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        included_seats = _parse_included_seats(d.pop("included_seats"))


        def _parse_additional_seat_price(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        additional_seat_price = _parse_additional_seat_price(d.pop("additional_seat_price"))


        plan_pricing_response = cls(
            plan_id=plan_id,
            plan_name=plan_name,
            tier=tier,
            base_amount=base_amount,
            quantity=quantity,
            total_amount=total_amount,
            currency=currency,
            billing_interval=billing_interval,
            included_seats=included_seats,
            additional_seat_price=additional_seat_price,
        )


        plan_pricing_response.additional_properties = d
        return plan_pricing_response

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
