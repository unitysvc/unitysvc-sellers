from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="CustomerStatementSummary")



@_attrs_define
class CustomerStatementSummary:
    """ Summary of a CustomerStatement for list views.

     """

    id: UUID
    statement_number: str
    period_start: datetime.date
    period_end: datetime.date
    opening_balance: str
    closing_balance: str
    currency: CurrencyEnum
    """ Supported currency codes for pricing. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        statement_number = self.statement_number

        period_start = self.period_start.isoformat()

        period_end = self.period_end.isoformat()

        opening_balance = self.opening_balance

        closing_balance = self.closing_balance

        currency: str = self.currency


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "statement_number": statement_number,
            "period_start": period_start,
            "period_end": period_end,
            "opening_balance": opening_balance,
            "closing_balance": closing_balance,
            "currency": currency,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        statement_number = d.pop("statement_number")

        period_start = isoparse(d.pop("period_start")).date()




        period_end = isoparse(d.pop("period_end")).date()




        opening_balance = d.pop("opening_balance")

        closing_balance = d.pop("closing_balance")

        currency = check_currency_enum(d.pop("currency"))




        customer_statement_summary = cls(
            id=id,
            statement_number=statement_number,
            period_start=period_start,
            period_end=period_end,
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            currency=currency,
        )


        customer_statement_summary.additional_properties = d
        return customer_statement_summary

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
