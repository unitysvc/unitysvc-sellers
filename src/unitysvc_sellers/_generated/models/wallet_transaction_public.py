from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..models.wallet_transaction_type_enum import check_wallet_transaction_type_enum
from ..models.wallet_transaction_type_enum import WalletTransactionTypeEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="WalletTransactionPublic")



@_attrs_define
class WalletTransactionPublic:
    """ Public transaction information for API responses

    All monetary amounts as Decimal (no conversion needed for display)

     """

    amount: str
    """ Transaction amount (positive for credits, negative for debits) """
    transaction_type: WalletTransactionTypeEnum
    """ Wallet transaction types. """
    balance_before: str
    """ Wallet balance before this transaction (double-entry bookkeeping) """
    balance_after: str
    """ Wallet balance after this transaction (double-entry bookkeeping) """
    id: UUID
    wallet_id: UUID
    created_at: datetime.datetime
    description: None | str | Unset = UNSET
    """ Optional description of the transaction """
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """





    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        transaction_type: str = self.transaction_type

        balance_before = self.balance_before

        balance_after = self.balance_after

        id = str(self.id)

        wallet_id = str(self.wallet_id)

        created_at = self.created_at.isoformat()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency



        field_dict: dict[str, Any] = {}

        field_dict.update({
            "amount": amount,
            "transaction_type": transaction_type,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "id": id,
            "wallet_id": wallet_id,
            "created_at": created_at,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if currency is not UNSET:
            field_dict["currency"] = currency

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        amount = d.pop("amount")

        transaction_type = check_wallet_transaction_type_enum(d.pop("transaction_type"))




        balance_before = d.pop("balance_before")

        balance_after = d.pop("balance_after")

        id = UUID(d.pop("id"))




        wallet_id = UUID(d.pop("wallet_id"))




        created_at = isoparse(d.pop("created_at"))




        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        wallet_transaction_public = cls(
            amount=amount,
            transaction_type=transaction_type,
            balance_before=balance_before,
            balance_after=balance_after,
            id=id,
            wallet_id=wallet_id,
            created_at=created_at,
            description=description,
            currency=currency,
        )

        return wallet_transaction_public

