from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..models.seller_invoice_status_enum import check_seller_invoice_status_enum
from ..models.seller_invoice_status_enum import SellerInvoiceStatusEnum
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="SellerInvoiceSummary")



@_attrs_define
class SellerInvoiceSummary:
    """ Summary of a SellerInvoice for list views.

     """

    id: UUID
    seller_id: UUID
    invoice_number: str
    period_start: datetime.date
    period_end: datetime.date
    seller_payout: str
    payout_adjustment: str
    list_charge: None | str
    currency: CurrencyEnum
    """ Supported currency codes for pricing. """
    status: SellerInvoiceStatusEnum
    """ Status of a seller invoice in its lifecycle.

    Flow:
    - pro_forma: Invoice created, within dispute window for seller review
    - disputed: Seller filed dispute, awaiting UnitySVC review
    - finalized: Dispute window closed (or dispute resolved), awaiting payout
    - funds_released: Payout processed, ledger entry created for seller balance
    - voided: Invoice voided due to fraud/abuse (terminal, preserves audit trail)

    Note: Seller balance is computed from SellerLedger entries.
    Actual payouts are handled separately via payout processing. """
    dispute_deadline: datetime.datetime
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        seller_id = str(self.seller_id)

        invoice_number = self.invoice_number

        period_start = self.period_start.isoformat()

        period_end = self.period_end.isoformat()

        seller_payout = self.seller_payout

        payout_adjustment = self.payout_adjustment

        list_charge: None | str
        list_charge = self.list_charge

        currency: str = self.currency

        status: str = self.status

        dispute_deadline = self.dispute_deadline.isoformat()

        created_at = self.created_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "seller_id": seller_id,
            "invoice_number": invoice_number,
            "period_start": period_start,
            "period_end": period_end,
            "seller_payout": seller_payout,
            "payout_adjustment": payout_adjustment,
            "list_charge": list_charge,
            "currency": currency,
            "status": status,
            "dispute_deadline": dispute_deadline,
            "created_at": created_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        seller_id = UUID(d.pop("seller_id"))




        invoice_number = d.pop("invoice_number")

        period_start = isoparse(d.pop("period_start")).date()




        period_end = isoparse(d.pop("period_end")).date()




        seller_payout = d.pop("seller_payout")

        payout_adjustment = d.pop("payout_adjustment")

        def _parse_list_charge(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        list_charge = _parse_list_charge(d.pop("list_charge"))


        currency = check_currency_enum(d.pop("currency"))




        status = check_seller_invoice_status_enum(d.pop("status"))




        dispute_deadline = isoparse(d.pop("dispute_deadline"))




        created_at = isoparse(d.pop("created_at"))




        seller_invoice_summary = cls(
            id=id,
            seller_id=seller_id,
            invoice_number=invoice_number,
            period_start=period_start,
            period_end=period_end,
            seller_payout=seller_payout,
            payout_adjustment=payout_adjustment,
            list_charge=list_charge,
            currency=currency,
            status=status,
            dispute_deadline=dispute_deadline,
            created_at=created_at,
        )


        seller_invoice_summary.additional_properties = d
        return seller_invoice_summary

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
