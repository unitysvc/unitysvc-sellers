from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="WalletUpdate")



@_attrs_define
class WalletUpdate:
    """ Schema for updating Wallet, all fields optional

    All monetary amounts as Decimal

     """

    credit_limit: float | None | str | Unset = UNSET
    auto_topoff: bool | None | Unset = UNSET
    topoff_amount: float | None | str | Unset = UNSET
    spending_budget: float | None | str | Unset = UNSET
    daily_spending_alert: float | None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        credit_limit: float | None | str | Unset
        if isinstance(self.credit_limit, Unset):
            credit_limit = UNSET
        else:
            credit_limit = self.credit_limit

        auto_topoff: bool | None | Unset
        if isinstance(self.auto_topoff, Unset):
            auto_topoff = UNSET
        else:
            auto_topoff = self.auto_topoff

        topoff_amount: float | None | str | Unset
        if isinstance(self.topoff_amount, Unset):
            topoff_amount = UNSET
        else:
            topoff_amount = self.topoff_amount

        spending_budget: float | None | str | Unset
        if isinstance(self.spending_budget, Unset):
            spending_budget = UNSET
        else:
            spending_budget = self.spending_budget

        daily_spending_alert: float | None | str | Unset
        if isinstance(self.daily_spending_alert, Unset):
            daily_spending_alert = UNSET
        else:
            daily_spending_alert = self.daily_spending_alert


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if credit_limit is not UNSET:
            field_dict["credit_limit"] = credit_limit
        if auto_topoff is not UNSET:
            field_dict["auto_topoff"] = auto_topoff
        if topoff_amount is not UNSET:
            field_dict["topoff_amount"] = topoff_amount
        if spending_budget is not UNSET:
            field_dict["spending_budget"] = spending_budget
        if daily_spending_alert is not UNSET:
            field_dict["daily_spending_alert"] = daily_spending_alert

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_credit_limit(data: object) -> float | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | str | Unset, data)

        credit_limit = _parse_credit_limit(d.pop("credit_limit", UNSET))


        def _parse_auto_topoff(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        auto_topoff = _parse_auto_topoff(d.pop("auto_topoff", UNSET))


        def _parse_topoff_amount(data: object) -> float | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | str | Unset, data)

        topoff_amount = _parse_topoff_amount(d.pop("topoff_amount", UNSET))


        def _parse_spending_budget(data: object) -> float | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | str | Unset, data)

        spending_budget = _parse_spending_budget(d.pop("spending_budget", UNSET))


        def _parse_daily_spending_alert(data: object) -> float | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | str | Unset, data)

        daily_spending_alert = _parse_daily_spending_alert(d.pop("daily_spending_alert", UNSET))


        wallet_update = cls(
            credit_limit=credit_limit,
            auto_topoff=auto_topoff,
            topoff_amount=topoff_amount,
            spending_budget=spending_budget,
            daily_spending_alert=daily_spending_alert,
        )


        wallet_update.additional_properties = d
        return wallet_update

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
