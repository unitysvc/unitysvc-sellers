from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.plan_subscription_status_enum import check_plan_subscription_status_enum
from ..models.plan_subscription_status_enum import PlanSubscriptionStatusEnum
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.plan_info_public import PlanInfoPublic





T = TypeVar("T", bound="SubscriptionCreateResponse")



@_attrs_define
class SubscriptionCreateResponse:
    """ Response after subscription is created.

     """

    subscription_id: UUID
    """ Subscription ID """
    customer_id: UUID
    """ Customer ID """
    plan: PlanInfoPublic
    """ Minimal plan info for response. """
    status: PlanSubscriptionStatusEnum
    """ Platform subscription status (Stripe-compatible).

    Note: This is separate from SubscriptionStatusEnum which is for
    ServiceEnrollment (marketplace services). """
    amount: str
    """ Subscription amount """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.plan_info_public import PlanInfoPublic
        subscription_id = str(self.subscription_id)

        customer_id = str(self.customer_id)

        plan = self.plan.to_dict()

        status: str = self.status

        amount = self.amount


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "subscription_id": subscription_id,
            "customer_id": customer_id,
            "plan": plan,
            "status": status,
            "amount": amount,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plan_info_public import PlanInfoPublic
        d = dict(src_dict)
        subscription_id = UUID(d.pop("subscription_id"))




        customer_id = UUID(d.pop("customer_id"))




        plan = PlanInfoPublic.from_dict(d.pop("plan"))




        status = check_plan_subscription_status_enum(d.pop("status"))




        amount = d.pop("amount")

        subscription_create_response = cls(
            subscription_id=subscription_id,
            customer_id=customer_id,
            plan=plan,
            status=status,
            amount=amount,
        )


        subscription_create_response.additional_properties = d
        return subscription_create_response

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
