from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.seller_balance_public import SellerBalancePublic





T = TypeVar("T", bound="SellerBalancesPublic")



@_attrs_define
class SellerBalancesPublic:
    """ List of seller balances across currencies.

     """

    seller_id: UUID
    balances: list[SellerBalancePublic]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.seller_balance_public import SellerBalancePublic
        seller_id = str(self.seller_id)

        balances = []
        for balances_item_data in self.balances:
            balances_item = balances_item_data.to_dict()
            balances.append(balances_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "seller_id": seller_id,
            "balances": balances,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.seller_balance_public import SellerBalancePublic
        d = dict(src_dict)
        seller_id = UUID(d.pop("seller_id"))




        balances = []
        _balances = d.pop("balances")
        for balances_item_data in (_balances):
            balances_item = SellerBalancePublic.from_dict(balances_item_data)



            balances.append(balances_item)


        seller_balances_public = cls(
            seller_id=seller_id,
            balances=balances,
        )


        seller_balances_public.additional_properties = d
        return seller_balances_public

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
