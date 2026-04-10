from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.payment_method_info_details import PaymentMethodInfoDetails





T = TypeVar("T", bound="PaymentMethodInfo")



@_attrs_define
class PaymentMethodInfo:
    """ Payment method information from Stripe.

     """

    id: str
    """ Stripe payment method ID (pm_xxx) """
    type_: str
    """ Payment method type: card, us_bank_account, etc. """
    display_name: str
    """ Human-readable name for display """
    details: PaymentMethodInfoDetails
    """ Type-specific details (last4, brand, bank_name, etc.) """
    is_default: bool
    """ Whether this is the default payment method """
    customer_id: None | str | Unset = UNSET
    """ Customer ID this PM belongs to (when all_customers=True) """
    customer_name: None | str | Unset = UNSET
    """ Customer name for display (when all_customers=True) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.payment_method_info_details import PaymentMethodInfoDetails
        id = self.id

        type_ = self.type_

        display_name = self.display_name

        details = self.details.to_dict()

        is_default = self.is_default

        customer_id: None | str | Unset
        if isinstance(self.customer_id, Unset):
            customer_id = UNSET
        else:
            customer_id = self.customer_id

        customer_name: None | str | Unset
        if isinstance(self.customer_name, Unset):
            customer_name = UNSET
        else:
            customer_name = self.customer_name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "type": type_,
            "display_name": display_name,
            "details": details,
            "is_default": is_default,
        })
        if customer_id is not UNSET:
            field_dict["customer_id"] = customer_id
        if customer_name is not UNSET:
            field_dict["customer_name"] = customer_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.payment_method_info_details import PaymentMethodInfoDetails
        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        display_name = d.pop("display_name")

        details = PaymentMethodInfoDetails.from_dict(d.pop("details"))




        is_default = d.pop("is_default")

        def _parse_customer_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        customer_id = _parse_customer_id(d.pop("customer_id", UNSET))


        def _parse_customer_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        customer_name = _parse_customer_name(d.pop("customer_name", UNSET))


        payment_method_info = cls(
            id=id,
            type_=type_,
            display_name=display_name,
            details=details,
            is_default=is_default,
            customer_id=customer_id,
            customer_name=customer_name,
        )


        payment_method_info.additional_properties = d
        return payment_method_info

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
