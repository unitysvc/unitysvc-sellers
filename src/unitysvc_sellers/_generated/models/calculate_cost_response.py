from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.calculate_cost_response_adjustments import CalculateCostResponseAdjustments





T = TypeVar("T", bound="CalculateCostResponse")



@_attrs_define
class CalculateCostResponse:
    """ Response from the calculate-cost endpoint.

     """

    list_charge: str
    """ Charge from list_price before any rules """
    seller_charge: str
    """ Charge after seller-funded rules """
    customer_charge: str
    """ Final charge after all rules """
    adjustments: CalculateCostResponseAdjustments
    """ Per-rule adjustments (rule_id -> adjustment amount) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.calculate_cost_response_adjustments import CalculateCostResponseAdjustments
        list_charge = self.list_charge

        seller_charge = self.seller_charge

        customer_charge = self.customer_charge

        adjustments = self.adjustments.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "list_charge": list_charge,
            "seller_charge": seller_charge,
            "customer_charge": customer_charge,
            "adjustments": adjustments,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.calculate_cost_response_adjustments import CalculateCostResponseAdjustments
        d = dict(src_dict)
        list_charge = d.pop("list_charge")

        seller_charge = d.pop("seller_charge")

        customer_charge = d.pop("customer_charge")

        adjustments = CalculateCostResponseAdjustments.from_dict(d.pop("adjustments"))




        calculate_cost_response = cls(
            list_charge=list_charge,
            seller_charge=seller_charge,
            customer_charge=customer_charge,
            adjustments=adjustments,
        )


        calculate_cost_response.additional_properties = d
        return calculate_cost_response

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
