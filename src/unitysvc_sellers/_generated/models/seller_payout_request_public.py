from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..models.payout_method_enum import check_payout_method_enum
from ..models.payout_method_enum import PayoutMethodEnum
from ..models.payout_request_status_enum import check_payout_request_status_enum
from ..models.payout_request_status_enum import PayoutRequestStatusEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="SellerPayoutRequestPublic")



@_attrs_define
class SellerPayoutRequestPublic:
    """ Public SellerPayoutRequest for API responses.

     """

    amount: str
    """ Requested payout amount (must be positive) """
    payment_method: PayoutMethodEnum
    """ Supported payout methods for sellers.

    - stripe_connect: Automatic payout via Stripe Connect (requires stripe_connect_id)
    - zelle: Zelle transfer (requires email or phone)
    - check: Physical check mailed to address """
    id: UUID
    seller_id: UUID
    request_number: str
    status: PayoutRequestStatusEnum
    """ Status of a seller payout request.

    - pending: Request submitted, awaiting processing
    - processing: Payment being processed
    - completed: Payout successfully completed
    - failed: Payout failed (with failure_reason)
    - cancelled: Request cancelled before processing """
    platform_fee: str
    net_amount: str
    requested_at: datetime.datetime
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    payment_reference: None | str | Unset = UNSET
    failure_reason: None | str | Unset = UNSET
    processed_at: datetime.datetime | None | Unset = UNSET
    completed_at: datetime.datetime | None | Unset = UNSET
    requested_by_id: None | Unset | UUID = UNSET
    processed_by_id: None | Unset | UUID = UNSET





    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        payment_method: str = self.payment_method

        id = str(self.id)

        seller_id = str(self.seller_id)

        request_number = self.request_number

        status: str = self.status

        platform_fee = self.platform_fee

        net_amount = self.net_amount

        requested_at = self.requested_at.isoformat()

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency


        payment_reference: None | str | Unset
        if isinstance(self.payment_reference, Unset):
            payment_reference = UNSET
        else:
            payment_reference = self.payment_reference

        failure_reason: None | str | Unset
        if isinstance(self.failure_reason, Unset):
            failure_reason = UNSET
        else:
            failure_reason = self.failure_reason

        processed_at: None | str | Unset
        if isinstance(self.processed_at, Unset):
            processed_at = UNSET
        elif isinstance(self.processed_at, datetime.datetime):
            processed_at = self.processed_at.isoformat()
        else:
            processed_at = self.processed_at

        completed_at: None | str | Unset
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        requested_by_id: None | str | Unset
        if isinstance(self.requested_by_id, Unset):
            requested_by_id = UNSET
        elif isinstance(self.requested_by_id, UUID):
            requested_by_id = str(self.requested_by_id)
        else:
            requested_by_id = self.requested_by_id

        processed_by_id: None | str | Unset
        if isinstance(self.processed_by_id, Unset):
            processed_by_id = UNSET
        elif isinstance(self.processed_by_id, UUID):
            processed_by_id = str(self.processed_by_id)
        else:
            processed_by_id = self.processed_by_id


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "amount": amount,
            "payment_method": payment_method,
            "id": id,
            "seller_id": seller_id,
            "request_number": request_number,
            "status": status,
            "platform_fee": platform_fee,
            "net_amount": net_amount,
            "requested_at": requested_at,
        })
        if currency is not UNSET:
            field_dict["currency"] = currency
        if payment_reference is not UNSET:
            field_dict["payment_reference"] = payment_reference
        if failure_reason is not UNSET:
            field_dict["failure_reason"] = failure_reason
        if processed_at is not UNSET:
            field_dict["processed_at"] = processed_at
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if requested_by_id is not UNSET:
            field_dict["requested_by_id"] = requested_by_id
        if processed_by_id is not UNSET:
            field_dict["processed_by_id"] = processed_by_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        amount = d.pop("amount")

        payment_method = check_payout_method_enum(d.pop("payment_method"))




        id = UUID(d.pop("id"))




        seller_id = UUID(d.pop("seller_id"))




        request_number = d.pop("request_number")

        status = check_payout_request_status_enum(d.pop("status"))




        platform_fee = d.pop("platform_fee")

        net_amount = d.pop("net_amount")

        requested_at = isoparse(d.pop("requested_at"))




        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        def _parse_payment_reference(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        payment_reference = _parse_payment_reference(d.pop("payment_reference", UNSET))


        def _parse_failure_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        failure_reason = _parse_failure_reason(d.pop("failure_reason", UNSET))


        def _parse_processed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                processed_at_type_0 = isoparse(data)



                return processed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        processed_at = _parse_processed_at(d.pop("processed_at", UNSET))


        def _parse_completed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = isoparse(data)



                return completed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        completed_at = _parse_completed_at(d.pop("completed_at", UNSET))


        def _parse_requested_by_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                requested_by_id_type_0 = UUID(data)



                return requested_by_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        requested_by_id = _parse_requested_by_id(d.pop("requested_by_id", UNSET))


        def _parse_processed_by_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                processed_by_id_type_0 = UUID(data)



                return processed_by_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        processed_by_id = _parse_processed_by_id(d.pop("processed_by_id", UNSET))


        seller_payout_request_public = cls(
            amount=amount,
            payment_method=payment_method,
            id=id,
            seller_id=seller_id,
            request_number=request_number,
            status=status,
            platform_fee=platform_fee,
            net_amount=net_amount,
            requested_at=requested_at,
            currency=currency,
            payment_reference=payment_reference,
            failure_reason=failure_reason,
            processed_at=processed_at,
            completed_at=completed_at,
            requested_by_id=requested_by_id,
            processed_by_id=processed_by_id,
        )

        return seller_payout_request_public

