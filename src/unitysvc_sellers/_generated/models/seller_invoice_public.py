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
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.seller_invoice_line_item_public import SellerInvoiceLineItemPublic





T = TypeVar("T", bound="SellerInvoicePublic")



@_attrs_define
class SellerInvoicePublic:
    """ Public SellerInvoice for API responses.

     """

    seller_id: UUID
    """ Reference to the seller receiving payment """
    invoice_number: str
    """ Auto-generated: INV-{seller}-{YYYYMM}-{seq} """
    period_start: datetime.date
    """ Start of billing period """
    period_end: datetime.date
    """ End of billing period """
    seller_payout: str
    """ Total amount owed to seller (sum of line item payouts) """
    id: UUID
    dispute_deadline: datetime.datetime
    generated_at: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime
    opening_balance: str | Unset = '0'
    """ Unpaid balance carried forward from previous invoice """
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    payout_adjustment: str | Unset = '0'
    """ Adjustment amount (can be negative) """
    adjustment_reason: None | str | Unset = UNSET
    """ Reason for adjustment """
    list_charge: None | str | Unset = UNSET
    """ Total list price before any discounts (reference) """
    status: SellerInvoiceStatusEnum | Unset = UNSET
    """ Status of a seller invoice in its lifecycle.

    Flow:
    - pro_forma: Invoice created, within dispute window for seller review
    - disputed: Seller filed dispute, awaiting UnitySVC review
    - finalized: Dispute window closed (or dispute resolved), awaiting payout
    - funds_released: Payout processed, ledger entry created for seller balance
    - voided: Invoice voided due to fraud/abuse (terminal, preserves audit trail)

    Note: Seller balance is computed from SellerLedger entries.
    Actual payouts are handled separately via payout processing. """
    disputed_at: datetime.datetime | None | Unset = UNSET
    dispute_reason: None | str | Unset = UNSET
    reviewed_by_id: None | Unset | UUID = UNSET
    reviewed_at: datetime.datetime | None | Unset = UNSET
    review_notes: None | str | Unset = UNSET
    finalized_at: datetime.datetime | None | Unset = UNSET
    funds_released_at: datetime.datetime | None | Unset = UNSET
    voided_at: datetime.datetime | None | Unset = UNSET
    void_reason: None | str | Unset = UNSET
    line_items: list[SellerInvoiceLineItemPublic] | Unset = UNSET
    pdf_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.seller_invoice_line_item_public import SellerInvoiceLineItemPublic
        seller_id = str(self.seller_id)

        invoice_number = self.invoice_number

        period_start = self.period_start.isoformat()

        period_end = self.period_end.isoformat()

        seller_payout = self.seller_payout

        id = str(self.id)

        dispute_deadline = self.dispute_deadline.isoformat()

        generated_at = self.generated_at.isoformat()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        opening_balance = self.opening_balance

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency


        payout_adjustment = self.payout_adjustment

        adjustment_reason: None | str | Unset
        if isinstance(self.adjustment_reason, Unset):
            adjustment_reason = UNSET
        else:
            adjustment_reason = self.adjustment_reason

        list_charge: None | str | Unset
        if isinstance(self.list_charge, Unset):
            list_charge = UNSET
        else:
            list_charge = self.list_charge

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status


        disputed_at: None | str | Unset
        if isinstance(self.disputed_at, Unset):
            disputed_at = UNSET
        elif isinstance(self.disputed_at, datetime.datetime):
            disputed_at = self.disputed_at.isoformat()
        else:
            disputed_at = self.disputed_at

        dispute_reason: None | str | Unset
        if isinstance(self.dispute_reason, Unset):
            dispute_reason = UNSET
        else:
            dispute_reason = self.dispute_reason

        reviewed_by_id: None | str | Unset
        if isinstance(self.reviewed_by_id, Unset):
            reviewed_by_id = UNSET
        elif isinstance(self.reviewed_by_id, UUID):
            reviewed_by_id = str(self.reviewed_by_id)
        else:
            reviewed_by_id = self.reviewed_by_id

        reviewed_at: None | str | Unset
        if isinstance(self.reviewed_at, Unset):
            reviewed_at = UNSET
        elif isinstance(self.reviewed_at, datetime.datetime):
            reviewed_at = self.reviewed_at.isoformat()
        else:
            reviewed_at = self.reviewed_at

        review_notes: None | str | Unset
        if isinstance(self.review_notes, Unset):
            review_notes = UNSET
        else:
            review_notes = self.review_notes

        finalized_at: None | str | Unset
        if isinstance(self.finalized_at, Unset):
            finalized_at = UNSET
        elif isinstance(self.finalized_at, datetime.datetime):
            finalized_at = self.finalized_at.isoformat()
        else:
            finalized_at = self.finalized_at

        funds_released_at: None | str | Unset
        if isinstance(self.funds_released_at, Unset):
            funds_released_at = UNSET
        elif isinstance(self.funds_released_at, datetime.datetime):
            funds_released_at = self.funds_released_at.isoformat()
        else:
            funds_released_at = self.funds_released_at

        voided_at: None | str | Unset
        if isinstance(self.voided_at, Unset):
            voided_at = UNSET
        elif isinstance(self.voided_at, datetime.datetime):
            voided_at = self.voided_at.isoformat()
        else:
            voided_at = self.voided_at

        void_reason: None | str | Unset
        if isinstance(self.void_reason, Unset):
            void_reason = UNSET
        else:
            void_reason = self.void_reason

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
            "seller_id": seller_id,
            "invoice_number": invoice_number,
            "period_start": period_start,
            "period_end": period_end,
            "seller_payout": seller_payout,
            "id": id,
            "dispute_deadline": dispute_deadline,
            "generated_at": generated_at,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if opening_balance is not UNSET:
            field_dict["opening_balance"] = opening_balance
        if currency is not UNSET:
            field_dict["currency"] = currency
        if payout_adjustment is not UNSET:
            field_dict["payout_adjustment"] = payout_adjustment
        if adjustment_reason is not UNSET:
            field_dict["adjustment_reason"] = adjustment_reason
        if list_charge is not UNSET:
            field_dict["list_charge"] = list_charge
        if status is not UNSET:
            field_dict["status"] = status
        if disputed_at is not UNSET:
            field_dict["disputed_at"] = disputed_at
        if dispute_reason is not UNSET:
            field_dict["dispute_reason"] = dispute_reason
        if reviewed_by_id is not UNSET:
            field_dict["reviewed_by_id"] = reviewed_by_id
        if reviewed_at is not UNSET:
            field_dict["reviewed_at"] = reviewed_at
        if review_notes is not UNSET:
            field_dict["review_notes"] = review_notes
        if finalized_at is not UNSET:
            field_dict["finalized_at"] = finalized_at
        if funds_released_at is not UNSET:
            field_dict["funds_released_at"] = funds_released_at
        if voided_at is not UNSET:
            field_dict["voided_at"] = voided_at
        if void_reason is not UNSET:
            field_dict["void_reason"] = void_reason
        if line_items is not UNSET:
            field_dict["line_items"] = line_items
        if pdf_url is not UNSET:
            field_dict["pdf_url"] = pdf_url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.seller_invoice_line_item_public import SellerInvoiceLineItemPublic
        d = dict(src_dict)
        seller_id = UUID(d.pop("seller_id"))




        invoice_number = d.pop("invoice_number")

        period_start = isoparse(d.pop("period_start")).date()




        period_end = isoparse(d.pop("period_end")).date()




        seller_payout = d.pop("seller_payout")

        id = UUID(d.pop("id"))




        dispute_deadline = isoparse(d.pop("dispute_deadline"))




        generated_at = isoparse(d.pop("generated_at"))




        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        opening_balance = d.pop("opening_balance", UNSET)

        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        payout_adjustment = d.pop("payout_adjustment", UNSET)

        def _parse_adjustment_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        adjustment_reason = _parse_adjustment_reason(d.pop("adjustment_reason", UNSET))


        def _parse_list_charge(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        list_charge = _parse_list_charge(d.pop("list_charge", UNSET))


        _status = d.pop("status", UNSET)
        status: SellerInvoiceStatusEnum | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_seller_invoice_status_enum(_status)




        def _parse_disputed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                disputed_at_type_0 = isoparse(data)



                return disputed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        disputed_at = _parse_disputed_at(d.pop("disputed_at", UNSET))


        def _parse_dispute_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        dispute_reason = _parse_dispute_reason(d.pop("dispute_reason", UNSET))


        def _parse_reviewed_by_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reviewed_by_id_type_0 = UUID(data)



                return reviewed_by_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        reviewed_by_id = _parse_reviewed_by_id(d.pop("reviewed_by_id", UNSET))


        def _parse_reviewed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reviewed_at_type_0 = isoparse(data)



                return reviewed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        reviewed_at = _parse_reviewed_at(d.pop("reviewed_at", UNSET))


        def _parse_review_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        review_notes = _parse_review_notes(d.pop("review_notes", UNSET))


        def _parse_finalized_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                finalized_at_type_0 = isoparse(data)



                return finalized_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        finalized_at = _parse_finalized_at(d.pop("finalized_at", UNSET))


        def _parse_funds_released_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                funds_released_at_type_0 = isoparse(data)



                return funds_released_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        funds_released_at = _parse_funds_released_at(d.pop("funds_released_at", UNSET))


        def _parse_voided_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                voided_at_type_0 = isoparse(data)



                return voided_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        voided_at = _parse_voided_at(d.pop("voided_at", UNSET))


        def _parse_void_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        void_reason = _parse_void_reason(d.pop("void_reason", UNSET))


        _line_items = d.pop("line_items", UNSET)
        line_items: list[SellerInvoiceLineItemPublic] | Unset = UNSET
        if _line_items is not UNSET:
            line_items = []
            for line_items_item_data in _line_items:
                line_items_item = SellerInvoiceLineItemPublic.from_dict(line_items_item_data)



                line_items.append(line_items_item)


        def _parse_pdf_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pdf_url = _parse_pdf_url(d.pop("pdf_url", UNSET))


        seller_invoice_public = cls(
            seller_id=seller_id,
            invoice_number=invoice_number,
            period_start=period_start,
            period_end=period_end,
            seller_payout=seller_payout,
            id=id,
            dispute_deadline=dispute_deadline,
            generated_at=generated_at,
            created_at=created_at,
            updated_at=updated_at,
            opening_balance=opening_balance,
            currency=currency,
            payout_adjustment=payout_adjustment,
            adjustment_reason=adjustment_reason,
            list_charge=list_charge,
            status=status,
            disputed_at=disputed_at,
            dispute_reason=dispute_reason,
            reviewed_by_id=reviewed_by_id,
            reviewed_at=reviewed_at,
            review_notes=review_notes,
            finalized_at=finalized_at,
            funds_released_at=funds_released_at,
            voided_at=voided_at,
            void_reason=void_reason,
            line_items=line_items,
            pdf_url=pdf_url,
        )


        seller_invoice_public.additional_properties = d
        return seller_invoice_public

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
