from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..models.seller_invoice_line_item_type_enum import check_seller_invoice_line_item_type_enum
from ..models.seller_invoice_line_item_type_enum import SellerInvoiceLineItemTypeEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.seller_invoice_line_item_public_reference_data import SellerInvoiceLineItemPublicReferenceData





T = TypeVar("T", bound="SellerInvoiceLineItemPublic")



@_attrs_define
class SellerInvoiceLineItemPublic:
    """ Public SellerInvoiceLineItem for API responses.

     """

    seller_id: UUID
    """ Reference to the seller """
    transaction_date: datetime.date
    """ Date of the transaction """
    item_type: SellerInvoiceLineItemTypeEnum
    """ Types of line items that appear on seller invoices.

    Invoice line items come from two sources:
    1. ClickHouse usage data (earnings for the period)
    2. Ledger entries (cash movements during the period)

    Positive amounts are credits, negative amounts are debits. """
    description: str
    """ Human-readable description of the line item """
    amount: str
    """ Amount (positive=credit to seller, negative=debit from seller) """
    id: UUID
    invoice_id: None | UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    reference_data: SellerInvoiceLineItemPublicReferenceData | Unset = UNSET
    """ Reference data: {type, id, details} e.g., {type: 'dashboard_line_item', id: '...'} """
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.seller_invoice_line_item_public_reference_data import SellerInvoiceLineItemPublicReferenceData
        seller_id = str(self.seller_id)

        transaction_date = self.transaction_date.isoformat()

        item_type: str = self.item_type

        description = self.description

        amount = self.amount

        id = str(self.id)

        invoice_id: None | str
        if isinstance(self.invoice_id, UUID):
            invoice_id = str(self.invoice_id)
        else:
            invoice_id = self.invoice_id

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        reference_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.reference_data, Unset):
            reference_data = self.reference_data.to_dict()

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "seller_id": seller_id,
            "transaction_date": transaction_date,
            "item_type": item_type,
            "description": description,
            "amount": amount,
            "id": id,
            "invoice_id": invoice_id,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if reference_data is not UNSET:
            field_dict["reference_data"] = reference_data
        if currency is not UNSET:
            field_dict["currency"] = currency

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.seller_invoice_line_item_public_reference_data import SellerInvoiceLineItemPublicReferenceData
        d = dict(src_dict)
        seller_id = UUID(d.pop("seller_id"))




        transaction_date = isoparse(d.pop("transaction_date")).date()




        item_type = check_seller_invoice_line_item_type_enum(d.pop("item_type"))




        description = d.pop("description")

        amount = d.pop("amount")

        id = UUID(d.pop("id"))




        def _parse_invoice_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                invoice_id_type_0 = UUID(data)



                return invoice_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        invoice_id = _parse_invoice_id(d.pop("invoice_id"))


        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        _reference_data = d.pop("reference_data", UNSET)
        reference_data: SellerInvoiceLineItemPublicReferenceData | Unset
        if isinstance(_reference_data,  Unset):
            reference_data = UNSET
        else:
            reference_data = SellerInvoiceLineItemPublicReferenceData.from_dict(_reference_data)




        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        seller_invoice_line_item_public = cls(
            seller_id=seller_id,
            transaction_date=transaction_date,
            item_type=item_type,
            description=description,
            amount=amount,
            id=id,
            invoice_id=invoice_id,
            created_at=created_at,
            updated_at=updated_at,
            reference_data=reference_data,
            currency=currency,
        )


        seller_invoice_line_item_public.additional_properties = d
        return seller_invoice_line_item_public

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
