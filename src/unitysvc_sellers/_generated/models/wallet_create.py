from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="WalletCreate")



@_attrs_define
class WalletCreate:
    """ Schema for creating a new Wallet.

    customer_id is derived from the X-Role-Id header at the route level.

     """

    credit_limit: float | str | Unset = 0.0
    """ Maximum allowed negative balance (credit extended to customer) """
    auto_topoff: bool | Unset = True
    """ Enable/disable automatic top-off """
    topoff_amount: float | str | Unset = 20.0
    """ Amount to add during auto-topoff """
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    spending_budget: float | None | str | Unset = 1000.0
    """ Spending budget per billing cycle. Notifications sent when exceeded, but usage continues. """
    daily_spending_alert: float | None | str | Unset = UNSET
    """ Daily spending alert threshold. Notifications sent when exceeded. Disabled if None. """





    def to_dict(self) -> dict[str, Any]:
        credit_limit: float | str | Unset
        if isinstance(self.credit_limit, Unset):
            credit_limit = UNSET
        else:
            credit_limit = self.credit_limit

        auto_topoff = self.auto_topoff

        topoff_amount: float | str | Unset
        if isinstance(self.topoff_amount, Unset):
            topoff_amount = UNSET
        else:
            topoff_amount = self.topoff_amount

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency


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

        field_dict.update({
        })
        if credit_limit is not UNSET:
            field_dict["credit_limit"] = credit_limit
        if auto_topoff is not UNSET:
            field_dict["auto_topoff"] = auto_topoff
        if topoff_amount is not UNSET:
            field_dict["topoff_amount"] = topoff_amount
        if currency is not UNSET:
            field_dict["currency"] = currency
        if spending_budget is not UNSET:
            field_dict["spending_budget"] = spending_budget
        if daily_spending_alert is not UNSET:
            field_dict["daily_spending_alert"] = daily_spending_alert

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_credit_limit(data: object) -> float | str | Unset:
            if isinstance(data, Unset):
                return data
            return cast(float | str | Unset, data)

        credit_limit = _parse_credit_limit(d.pop("credit_limit", UNSET))


        auto_topoff = d.pop("auto_topoff", UNSET)

        def _parse_topoff_amount(data: object) -> float | str | Unset:
            if isinstance(data, Unset):
                return data
            return cast(float | str | Unset, data)

        topoff_amount = _parse_topoff_amount(d.pop("topoff_amount", UNSET))


        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




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


        wallet_create = cls(
            credit_limit=credit_limit,
            auto_topoff=auto_topoff,
            topoff_amount=topoff_amount,
            currency=currency,
            spending_budget=spending_budget,
            daily_spending_alert=daily_spending_alert,
        )

        return wallet_create

