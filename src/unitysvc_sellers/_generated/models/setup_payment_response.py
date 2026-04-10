from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.setup_payment_response_payment_method_details import SetupPaymentResponsePaymentMethodDetails





T = TypeVar("T", bound="SetupPaymentResponse")



@_attrs_define
class SetupPaymentResponse:
    """ Response from setup-payment endpoint.

     """

    customer_id: str
    """ New customer ID """
    stripe_customer_id: str
    """ Stripe customer ID """
    payment_method_id: str
    """ Attached payment method ID """
    payment_method_details: SetupPaymentResponsePaymentMethodDetails
    """ Payment method display info """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.setup_payment_response_payment_method_details import SetupPaymentResponsePaymentMethodDetails
        customer_id = self.customer_id

        stripe_customer_id = self.stripe_customer_id

        payment_method_id = self.payment_method_id

        payment_method_details = self.payment_method_details.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "customer_id": customer_id,
            "stripe_customer_id": stripe_customer_id,
            "payment_method_id": payment_method_id,
            "payment_method_details": payment_method_details,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.setup_payment_response_payment_method_details import SetupPaymentResponsePaymentMethodDetails
        d = dict(src_dict)
        customer_id = d.pop("customer_id")

        stripe_customer_id = d.pop("stripe_customer_id")

        payment_method_id = d.pop("payment_method_id")

        payment_method_details = SetupPaymentResponsePaymentMethodDetails.from_dict(d.pop("payment_method_details"))




        setup_payment_response = cls(
            customer_id=customer_id,
            stripe_customer_id=stripe_customer_id,
            payment_method_id=payment_method_id,
            payment_method_details=payment_method_details,
        )


        setup_payment_response.additional_properties = d
        return setup_payment_response

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
