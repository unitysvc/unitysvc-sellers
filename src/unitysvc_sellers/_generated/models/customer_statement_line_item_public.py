from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..models.customer_statement_line_item_type_enum import check_customer_statement_line_item_type_enum
from ..models.customer_statement_line_item_type_enum import CustomerStatementLineItemTypeEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.customer_statement_line_item_public_reference_data import CustomerStatementLineItemPublicReferenceData





T = TypeVar("T", bound="CustomerStatementLineItemPublic")



@_attrs_define
class CustomerStatementLineItemPublic:
    """ Public CustomerStatementLineItem for API responses.

     """

    customer_id: UUID
    """ Reference to the customer """
    transaction_date: datetime.date
    """ Date of the transaction """
    item_type: CustomerStatementLineItemTypeEnum
    """ Types of line items that appear on customer statements.

    These represent actual financial transactions on a statement.
    Statements are wallet-based; subscription payments are handled by Stripe. """
    description: str
    """ Human-readable description of the line item """
    amount: str
    """ Amount (positive=credit, negative=debit) """
    id: UUID
    statement_id: None | UUID
    reference_data: CustomerStatementLineItemPublicReferenceData | Unset = UNSET
    """ Reference data: {type, id, details} e.g., {type: 'wallet_transaction', id: '...'} """
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_statement_line_item_public_reference_data import CustomerStatementLineItemPublicReferenceData
        customer_id = str(self.customer_id)

        transaction_date = self.transaction_date.isoformat()

        item_type: str = self.item_type

        description = self.description

        amount = self.amount

        id = str(self.id)

        statement_id: None | str
        if isinstance(self.statement_id, UUID):
            statement_id = str(self.statement_id)
        else:
            statement_id = self.statement_id

        reference_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.reference_data, Unset):
            reference_data = self.reference_data.to_dict()

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "customer_id": customer_id,
            "transaction_date": transaction_date,
            "item_type": item_type,
            "description": description,
            "amount": amount,
            "id": id,
            "statement_id": statement_id,
        })
        if reference_data is not UNSET:
            field_dict["reference_data"] = reference_data
        if currency is not UNSET:
            field_dict["currency"] = currency

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_statement_line_item_public_reference_data import CustomerStatementLineItemPublicReferenceData
        d = dict(src_dict)
        customer_id = UUID(d.pop("customer_id"))




        transaction_date = isoparse(d.pop("transaction_date")).date()




        item_type = check_customer_statement_line_item_type_enum(d.pop("item_type"))




        description = d.pop("description")

        amount = d.pop("amount")

        id = UUID(d.pop("id"))




        def _parse_statement_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                statement_id_type_0 = UUID(data)



                return statement_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        statement_id = _parse_statement_id(d.pop("statement_id"))


        _reference_data = d.pop("reference_data", UNSET)
        reference_data: CustomerStatementLineItemPublicReferenceData | Unset
        if isinstance(_reference_data,  Unset):
            reference_data = UNSET
        else:
            reference_data = CustomerStatementLineItemPublicReferenceData.from_dict(_reference_data)




        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        customer_statement_line_item_public = cls(
            customer_id=customer_id,
            transaction_date=transaction_date,
            item_type=item_type,
            description=description,
            amount=amount,
            id=id,
            statement_id=statement_id,
            reference_data=reference_data,
            currency=currency,
        )


        customer_statement_line_item_public.additional_properties = d
        return customer_statement_line_item_public

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
