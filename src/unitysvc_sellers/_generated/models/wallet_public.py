from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..models.wallet_status_enum import check_wallet_status_enum
from ..models.wallet_status_enum import WalletStatusEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="WalletPublic")



@_attrs_define
class WalletPublic:
    """ Public wallet information for API responses

    All monetary amounts as Decimal (no conversion needed for display)

     """

    id: UUID
    customer_id: UUID
    balance: str
    status: WalletStatusEnum
    """ Wallet status for access control.

    - active: Normal operation, requests are served
    - suspended: Auto-topoff failed, can be auto-reactivated on successful payment
    - blocked: Manual admin block, requires admin action to unblock """
    created_at: datetime.datetime
    updated_at: datetime.datetime
    credit_limit: str | Unset = '0.00'
    """ Maximum allowed negative balance (credit extended to customer) """
    auto_topoff: bool | Unset = True
    """ Enable/disable automatic top-off """
    topoff_amount: str | Unset = '20.00'
    """ Amount to add during auto-topoff """
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    spending_budget: None | str | Unset = '1000.00'
    """ Spending budget per billing cycle. Notifications sent when exceeded, but usage continues. """
    daily_spending_alert: None | str | Unset = UNSET
    """ Daily spending alert threshold. Notifications sent when exceeded. Disabled if None. """
    statement_day: int | Unset = 0
    current_period_start: datetime.date | None | Unset = UNSET
    current_period_end: datetime.date | None | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        customer_id = str(self.customer_id)

        balance = self.balance

        status: str = self.status

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        credit_limit = self.credit_limit

        auto_topoff = self.auto_topoff

        topoff_amount = self.topoff_amount

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency


        spending_budget: None | str | Unset
        if isinstance(self.spending_budget, Unset):
            spending_budget = UNSET
        else:
            spending_budget = self.spending_budget

        daily_spending_alert: None | str | Unset
        if isinstance(self.daily_spending_alert, Unset):
            daily_spending_alert = UNSET
        else:
            daily_spending_alert = self.daily_spending_alert

        statement_day = self.statement_day

        current_period_start: None | str | Unset
        if isinstance(self.current_period_start, Unset):
            current_period_start = UNSET
        elif isinstance(self.current_period_start, datetime.date):
            current_period_start = self.current_period_start.isoformat()
        else:
            current_period_start = self.current_period_start

        current_period_end: None | str | Unset
        if isinstance(self.current_period_end, Unset):
            current_period_end = UNSET
        elif isinstance(self.current_period_end, datetime.date):
            current_period_end = self.current_period_end.isoformat()
        else:
            current_period_end = self.current_period_end


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "id": id,
            "customer_id": customer_id,
            "balance": balance,
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at,
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
        if statement_day is not UNSET:
            field_dict["statement_day"] = statement_day
        if current_period_start is not UNSET:
            field_dict["current_period_start"] = current_period_start
        if current_period_end is not UNSET:
            field_dict["current_period_end"] = current_period_end

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        customer_id = UUID(d.pop("customer_id"))




        balance = d.pop("balance")

        status = check_wallet_status_enum(d.pop("status"))




        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        credit_limit = d.pop("credit_limit", UNSET)

        auto_topoff = d.pop("auto_topoff", UNSET)

        topoff_amount = d.pop("topoff_amount", UNSET)

        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        def _parse_spending_budget(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        spending_budget = _parse_spending_budget(d.pop("spending_budget", UNSET))


        def _parse_daily_spending_alert(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        daily_spending_alert = _parse_daily_spending_alert(d.pop("daily_spending_alert", UNSET))


        statement_day = d.pop("statement_day", UNSET)

        def _parse_current_period_start(data: object) -> datetime.date | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                current_period_start_type_0 = isoparse(data).date()



                return current_period_start_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None | Unset, data)

        current_period_start = _parse_current_period_start(d.pop("current_period_start", UNSET))


        def _parse_current_period_end(data: object) -> datetime.date | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                current_period_end_type_0 = isoparse(data).date()



                return current_period_end_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None | Unset, data)

        current_period_end = _parse_current_period_end(d.pop("current_period_end", UNSET))


        wallet_public = cls(
            id=id,
            customer_id=customer_id,
            balance=balance,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            credit_limit=credit_limit,
            auto_topoff=auto_topoff,
            topoff_amount=topoff_amount,
            currency=currency,
            spending_budget=spending_budget,
            daily_spending_alert=daily_spending_alert,
            statement_day=statement_day,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
        )

        return wallet_public

