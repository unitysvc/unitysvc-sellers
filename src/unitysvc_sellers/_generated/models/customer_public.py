from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.customer_status_enum import check_customer_status_enum
from ..models.customer_status_enum import CustomerStatusEnum
from ..models.customer_type_enum import check_customer_type_enum
from ..models.customer_type_enum import CustomerTypeEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="CustomerPublic")



@_attrs_define
class CustomerPublic:
    """ Public customer information for API responses

     """

    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    customer_type: CustomerTypeEnum | Unset = UNSET
    name: None | str | Unset = UNSET
    """ Company name for business/corporate customers """
    stripe_customer_id: None | str | Unset = UNSET
    """ Stripe customer ID for billing """
    default_pm_id: None | str | Unset = UNSET
    """ Default payment method ID (cached from Stripe) """
    default_pm_details: None | str | Unset = UNSET
    """ Default payment method details (e.g., 'Visa ending in 4242') """
    billing_email: None | str | Unset = UNSET
    """ Billing contact email (for team/business customers) """
    status: CustomerStatusEnum | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        customer_type: str | Unset = UNSET
        if not isinstance(self.customer_type, Unset):
            customer_type = self.customer_type


        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        stripe_customer_id: None | str | Unset
        if isinstance(self.stripe_customer_id, Unset):
            stripe_customer_id = UNSET
        else:
            stripe_customer_id = self.stripe_customer_id

        default_pm_id: None | str | Unset
        if isinstance(self.default_pm_id, Unset):
            default_pm_id = UNSET
        else:
            default_pm_id = self.default_pm_id

        default_pm_details: None | str | Unset
        if isinstance(self.default_pm_details, Unset):
            default_pm_details = UNSET
        else:
            default_pm_details = self.default_pm_details

        billing_email: None | str | Unset
        if isinstance(self.billing_email, Unset):
            billing_email = UNSET
        else:
            billing_email = self.billing_email

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status



        field_dict: dict[str, Any] = {}

        field_dict.update({
            "id": id,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if customer_type is not UNSET:
            field_dict["customer_type"] = customer_type
        if name is not UNSET:
            field_dict["name"] = name
        if stripe_customer_id is not UNSET:
            field_dict["stripe_customer_id"] = stripe_customer_id
        if default_pm_id is not UNSET:
            field_dict["default_pm_id"] = default_pm_id
        if default_pm_details is not UNSET:
            field_dict["default_pm_details"] = default_pm_details
        if billing_email is not UNSET:
            field_dict["billing_email"] = billing_email
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        _customer_type = d.pop("customer_type", UNSET)
        customer_type: CustomerTypeEnum | Unset
        if isinstance(_customer_type,  Unset):
            customer_type = UNSET
        else:
            customer_type = check_customer_type_enum(_customer_type)




        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))


        def _parse_stripe_customer_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        stripe_customer_id = _parse_stripe_customer_id(d.pop("stripe_customer_id", UNSET))


        def _parse_default_pm_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        default_pm_id = _parse_default_pm_id(d.pop("default_pm_id", UNSET))


        def _parse_default_pm_details(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        default_pm_details = _parse_default_pm_details(d.pop("default_pm_details", UNSET))


        def _parse_billing_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        billing_email = _parse_billing_email(d.pop("billing_email", UNSET))


        _status = d.pop("status", UNSET)
        status: CustomerStatusEnum | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_customer_status_enum(_status)




        customer_public = cls(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            customer_type=customer_type,
            name=name,
            stripe_customer_id=stripe_customer_id,
            default_pm_id=default_pm_id,
            default_pm_details=default_pm_details,
            billing_email=billing_email,
            status=status,
        )

        return customer_public

