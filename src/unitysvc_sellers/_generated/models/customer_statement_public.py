from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.customer_statement_line_item_public import CustomerStatementLineItemPublic





T = TypeVar("T", bound="CustomerStatementPublic")



@_attrs_define
class CustomerStatementPublic:
    """ Public CustomerStatement for API responses.

     """

    customer_id: UUID
    """ Reference to the customer """
    statement_number: str
    """ Auto-generated: STMT-{customer}-{YYYYMM}-{seq} """
    period_start: datetime.date
    """ Start of statement period """
    period_end: datetime.date
    """ End of statement period """
    opening_balance: str
    """ Wallet balance at period start """
    closing_balance: str
    """ Wallet balance at period end """
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    notes: None | str | Unset = UNSET
    line_items: list[CustomerStatementLineItemPublic] | Unset = UNSET
    pdf_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_statement_line_item_public import CustomerStatementLineItemPublic
        customer_id = str(self.customer_id)

        statement_number = self.statement_number

        period_start = self.period_start.isoformat()

        period_end = self.period_end.isoformat()

        opening_balance = self.opening_balance

        closing_balance = self.closing_balance

        id = str(self.id)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency


        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        line_items: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.line_items, Unset):
            line_items = []
            for line_items_item_data in self.line_items:
                line_items_item = line_items_item_data.to_dict()
                line_items.append(line_items_item)



        pdf_url: None | str | Unset
        if isinstance(self.pdf_url, Unset):
            pdf_url = UNSET
        else:
            pdf_url = self.pdf_url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "customer_id": customer_id,
            "statement_number": statement_number,
            "period_start": period_start,
            "period_end": period_end,
            "opening_balance": opening_balance,
            "closing_balance": closing_balance,
            "id": id,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if currency is not UNSET:
            field_dict["currency"] = currency
        if notes is not UNSET:
            field_dict["notes"] = notes
        if line_items is not UNSET:
            field_dict["line_items"] = line_items
        if pdf_url is not UNSET:
            field_dict["pdf_url"] = pdf_url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_statement_line_item_public import CustomerStatementLineItemPublic
        d = dict(src_dict)
        customer_id = UUID(d.pop("customer_id"))




        statement_number = d.pop("statement_number")

        period_start = isoparse(d.pop("period_start")).date()




        period_end = isoparse(d.pop("period_end")).date()




        opening_balance = d.pop("opening_balance")

        closing_balance = d.pop("closing_balance")

        id = UUID(d.pop("id"))




        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))


        _line_items = d.pop("line_items", UNSET)
        line_items: list[CustomerStatementLineItemPublic] | Unset = UNSET
        if _line_items is not UNSET:
            line_items = []
            for line_items_item_data in _line_items:
                line_items_item = CustomerStatementLineItemPublic.from_dict(line_items_item_data)



                line_items.append(line_items_item)


        def _parse_pdf_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pdf_url = _parse_pdf_url(d.pop("pdf_url", UNSET))


        customer_statement_public = cls(
            customer_id=customer_id,
            statement_number=statement_number,
            period_start=period_start,
            period_end=period_end,
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            currency=currency,
            notes=notes,
            line_items=line_items,
            pdf_url=pdf_url,
        )


        customer_statement_public.additional_properties = d
        return customer_statement_public

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
