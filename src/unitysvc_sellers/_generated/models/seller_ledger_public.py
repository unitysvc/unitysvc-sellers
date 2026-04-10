from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..models.seller_ledger_type_enum import check_seller_ledger_type_enum
from ..models.seller_ledger_type_enum import SellerLedgerTypeEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="SellerLedgerPublic")



@_attrs_define
class SellerLedgerPublic:
    """ Public SellerLedger entry for API responses.

     """

    entry_type: SellerLedgerTypeEnum
    """ Types of seller ledger entries.

    All entries are immutable. Balance = SUM(amount) per seller per currency.
    Positive amounts are credits, negative amounts are debits. """
    amount: str
    """ Transaction amount (positive=credit, negative=debit) """
    id: UUID
    seller_id: UUID
    created_at: datetime.datetime
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    description: None | str | Unset = UNSET
    """ Optional description of the transaction """
    invoice_id: None | Unset | UUID = UNSET
    external_payout_id: None | str | Unset = UNSET
    created_by_id: None | Unset | UUID = UNSET





    def to_dict(self) -> dict[str, Any]:
        entry_type: str = self.entry_type

        amount = self.amount

        id = str(self.id)

        seller_id = str(self.seller_id)

        created_at = self.created_at.isoformat()

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency


        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        invoice_id: None | str | Unset
        if isinstance(self.invoice_id, Unset):
            invoice_id = UNSET
        elif isinstance(self.invoice_id, UUID):
            invoice_id = str(self.invoice_id)
        else:
            invoice_id = self.invoice_id

        external_payout_id: None | str | Unset
        if isinstance(self.external_payout_id, Unset):
            external_payout_id = UNSET
        else:
            external_payout_id = self.external_payout_id

        created_by_id: None | str | Unset
        if isinstance(self.created_by_id, Unset):
            created_by_id = UNSET
        elif isinstance(self.created_by_id, UUID):
            created_by_id = str(self.created_by_id)
        else:
            created_by_id = self.created_by_id


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "entry_type": entry_type,
            "amount": amount,
            "id": id,
            "seller_id": seller_id,
            "created_at": created_at,
        })
        if currency is not UNSET:
            field_dict["currency"] = currency
        if description is not UNSET:
            field_dict["description"] = description
        if invoice_id is not UNSET:
            field_dict["invoice_id"] = invoice_id
        if external_payout_id is not UNSET:
            field_dict["external_payout_id"] = external_payout_id
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        entry_type = check_seller_ledger_type_enum(d.pop("entry_type"))




        amount = d.pop("amount")

        id = UUID(d.pop("id"))




        seller_id = UUID(d.pop("seller_id"))




        created_at = isoparse(d.pop("created_at"))




        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_invoice_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                invoice_id_type_0 = UUID(data)



                return invoice_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        invoice_id = _parse_invoice_id(d.pop("invoice_id", UNSET))


        def _parse_external_payout_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_payout_id = _parse_external_payout_id(d.pop("external_payout_id", UNSET))


        def _parse_created_by_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_by_id_type_0 = UUID(data)



                return created_by_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        created_by_id = _parse_created_by_id(d.pop("created_by_id", UNSET))


        seller_ledger_public = cls(
            entry_type=entry_type,
            amount=amount,
            id=id,
            seller_id=seller_id,
            created_at=created_at,
            currency=currency,
            description=description,
            invoice_id=invoice_id,
            external_payout_id=external_payout_id,
            created_by_id=created_by_id,
        )

        return seller_ledger_public

