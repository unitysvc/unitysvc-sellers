from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.payout_method_enum import check_payout_method_enum
from ..models.payout_method_enum import PayoutMethodEnum
from ..models.payout_schedule_enum import check_payout_schedule_enum
from ..models.payout_schedule_enum import PayoutScheduleEnum
from ..models.seller_status_enum import check_seller_status_enum
from ..models.seller_status_enum import SellerStatusEnum
from ..models.seller_tier_enum import check_seller_tier_enum
from ..models.seller_tier_enum import SellerTierEnum
from ..models.seller_type_enum import check_seller_type_enum
from ..models.seller_type_enum import SellerTypeEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="SellerPublic")



@_attrs_define
class SellerPublic:
    """ Public seller information for API responses.

    Note: Balance information is computed from SellerLedger, not stored on Seller.
    Use get_seller_balance() or get_seller_balances() from crud.seller_ledger.

     """

    name: str
    """ Unique seller identifier (URL-friendly, e.g., 'acme-corp', 'john-doe') """
    contact_email: str
    """ Primary contact email for the seller """
    id: UUID
    account_manager_id: UUID
    payout_window_months: int | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    display_name: None | str | Unset = UNSET
    """ Human-readable seller name (e.g., 'ACME Corporation', 'John Doe') """
    seller_type: SellerTypeEnum | Unset = UNSET
    secondary_contact_email: None | str | Unset = UNSET
    """ Secondary contact email """
    homepage: None | str | Unset = UNSET
    """ Seller's homepage URL """
    description: None | str | Unset = UNSET
    """ Brief description of the seller """
    business_registration: None | str | Unset = UNSET
    """ Business registration number (if organization) """
    tax_id: None | str | Unset = UNSET
    """ Tax identification number (EIN, VAT, etc.) """
    stripe_connect_id: None | str | Unset = UNSET
    """ Stripe Connect account ID for receiving payouts """
    stripe_payment_method_id: None | str | Unset = UNSET
    """ Stripe payment method ID for charging seller (used for seller-funded incentives) """
    status: SellerStatusEnum | Unset = UNSET
    """ Seller status enum (backend-only, not used in unitysvc-core). """
    is_verified: bool | Unset = False
    """ Whether the seller has been verified (KYC/business verification) """
    seller_tier: SellerTierEnum | Unset = UNSET
    """ Seller trust tier — controls service approval workflow.

    - standard: All submissions require admin review
    - trusted: Revisions to active services auto-approve; new services need review
    - partner: All submissions (new + revisions) auto-approve """
    preferred_payout_method: PayoutMethodEnum | Unset = UNSET
    """ Supported payout methods for sellers.

    - stripe_connect: Automatic payout via Stripe Connect (requires stripe_connect_id)
    - zelle: Zelle transfer (requires email or phone)
    - check: Physical check mailed to address """
    payout_schedule: PayoutScheduleEnum | Unset = UNSET
    """ Payout schedule options for sellers.

    - on_demand: Seller manually requests payouts
    - automatic: Payouts triggered automatically when threshold is met """
    payout_threshold: int | None | Unset = UNSET
    """ Minimum balance (in cents) to trigger automatic payout. Only used when payout_schedule is 'automatic'. """
    zelle_email: None | str | Unset = UNSET
    """ Email address for Zelle payouts """
    zelle_phone: None | str | Unset = UNSET
    """ Phone number for Zelle payouts """
    check_payee_name: None | str | Unset = UNSET
    """ Payee name for check payouts """
    check_address_line1: None | str | Unset = UNSET
    """ Street address line 1 for check mailing """
    check_address_line2: None | str | Unset = UNSET
    """ Street address line 2 for check mailing """
    check_city: None | str | Unset = UNSET
    """ City for check mailing """
    check_state: None | str | Unset = UNSET
    """ State/province for check mailing """
    check_postal_code: None | str | Unset = UNSET
    """ Postal/ZIP code for check mailing """
    check_country: None | str | Unset = UNSET
    """ Country code (ISO 3166-1 alpha-2) for check mailing """
    review_count: int | Unset = 0
    average_rating: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        contact_email = self.contact_email

        id = str(self.id)

        account_manager_id = str(self.account_manager_id)

        payout_window_months: int | None
        payout_window_months = self.payout_window_months

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        seller_type: str | Unset = UNSET
        if not isinstance(self.seller_type, Unset):
            seller_type = self.seller_type


        secondary_contact_email: None | str | Unset
        if isinstance(self.secondary_contact_email, Unset):
            secondary_contact_email = UNSET
        else:
            secondary_contact_email = self.secondary_contact_email

        homepage: None | str | Unset
        if isinstance(self.homepage, Unset):
            homepage = UNSET
        else:
            homepage = self.homepage

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        business_registration: None | str | Unset
        if isinstance(self.business_registration, Unset):
            business_registration = UNSET
        else:
            business_registration = self.business_registration

        tax_id: None | str | Unset
        if isinstance(self.tax_id, Unset):
            tax_id = UNSET
        else:
            tax_id = self.tax_id

        stripe_connect_id: None | str | Unset
        if isinstance(self.stripe_connect_id, Unset):
            stripe_connect_id = UNSET
        else:
            stripe_connect_id = self.stripe_connect_id

        stripe_payment_method_id: None | str | Unset
        if isinstance(self.stripe_payment_method_id, Unset):
            stripe_payment_method_id = UNSET
        else:
            stripe_payment_method_id = self.stripe_payment_method_id

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status


        is_verified = self.is_verified

        seller_tier: str | Unset = UNSET
        if not isinstance(self.seller_tier, Unset):
            seller_tier = self.seller_tier


        preferred_payout_method: str | Unset = UNSET
        if not isinstance(self.preferred_payout_method, Unset):
            preferred_payout_method = self.preferred_payout_method


        payout_schedule: str | Unset = UNSET
        if not isinstance(self.payout_schedule, Unset):
            payout_schedule = self.payout_schedule


        payout_threshold: int | None | Unset
        if isinstance(self.payout_threshold, Unset):
            payout_threshold = UNSET
        else:
            payout_threshold = self.payout_threshold

        zelle_email: None | str | Unset
        if isinstance(self.zelle_email, Unset):
            zelle_email = UNSET
        else:
            zelle_email = self.zelle_email

        zelle_phone: None | str | Unset
        if isinstance(self.zelle_phone, Unset):
            zelle_phone = UNSET
        else:
            zelle_phone = self.zelle_phone

        check_payee_name: None | str | Unset
        if isinstance(self.check_payee_name, Unset):
            check_payee_name = UNSET
        else:
            check_payee_name = self.check_payee_name

        check_address_line1: None | str | Unset
        if isinstance(self.check_address_line1, Unset):
            check_address_line1 = UNSET
        else:
            check_address_line1 = self.check_address_line1

        check_address_line2: None | str | Unset
        if isinstance(self.check_address_line2, Unset):
            check_address_line2 = UNSET
        else:
            check_address_line2 = self.check_address_line2

        check_city: None | str | Unset
        if isinstance(self.check_city, Unset):
            check_city = UNSET
        else:
            check_city = self.check_city

        check_state: None | str | Unset
        if isinstance(self.check_state, Unset):
            check_state = UNSET
        else:
            check_state = self.check_state

        check_postal_code: None | str | Unset
        if isinstance(self.check_postal_code, Unset):
            check_postal_code = UNSET
        else:
            check_postal_code = self.check_postal_code

        check_country: None | str | Unset
        if isinstance(self.check_country, Unset):
            check_country = UNSET
        else:
            check_country = self.check_country

        review_count = self.review_count

        average_rating: float | None | Unset
        if isinstance(self.average_rating, Unset):
            average_rating = UNSET
        else:
            average_rating = self.average_rating


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "contact_email": contact_email,
            "id": id,
            "account_manager_id": account_manager_id,
            "payout_window_months": payout_window_months,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if seller_type is not UNSET:
            field_dict["seller_type"] = seller_type
        if secondary_contact_email is not UNSET:
            field_dict["secondary_contact_email"] = secondary_contact_email
        if homepage is not UNSET:
            field_dict["homepage"] = homepage
        if description is not UNSET:
            field_dict["description"] = description
        if business_registration is not UNSET:
            field_dict["business_registration"] = business_registration
        if tax_id is not UNSET:
            field_dict["tax_id"] = tax_id
        if stripe_connect_id is not UNSET:
            field_dict["stripe_connect_id"] = stripe_connect_id
        if stripe_payment_method_id is not UNSET:
            field_dict["stripe_payment_method_id"] = stripe_payment_method_id
        if status is not UNSET:
            field_dict["status"] = status
        if is_verified is not UNSET:
            field_dict["is_verified"] = is_verified
        if seller_tier is not UNSET:
            field_dict["seller_tier"] = seller_tier
        if preferred_payout_method is not UNSET:
            field_dict["preferred_payout_method"] = preferred_payout_method
        if payout_schedule is not UNSET:
            field_dict["payout_schedule"] = payout_schedule
        if payout_threshold is not UNSET:
            field_dict["payout_threshold"] = payout_threshold
        if zelle_email is not UNSET:
            field_dict["zelle_email"] = zelle_email
        if zelle_phone is not UNSET:
            field_dict["zelle_phone"] = zelle_phone
        if check_payee_name is not UNSET:
            field_dict["check_payee_name"] = check_payee_name
        if check_address_line1 is not UNSET:
            field_dict["check_address_line1"] = check_address_line1
        if check_address_line2 is not UNSET:
            field_dict["check_address_line2"] = check_address_line2
        if check_city is not UNSET:
            field_dict["check_city"] = check_city
        if check_state is not UNSET:
            field_dict["check_state"] = check_state
        if check_postal_code is not UNSET:
            field_dict["check_postal_code"] = check_postal_code
        if check_country is not UNSET:
            field_dict["check_country"] = check_country
        if review_count is not UNSET:
            field_dict["review_count"] = review_count
        if average_rating is not UNSET:
            field_dict["average_rating"] = average_rating

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        contact_email = d.pop("contact_email")

        id = UUID(d.pop("id"))




        account_manager_id = UUID(d.pop("account_manager_id"))




        def _parse_payout_window_months(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        payout_window_months = _parse_payout_window_months(d.pop("payout_window_months"))


        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))


        _seller_type = d.pop("seller_type", UNSET)
        seller_type: SellerTypeEnum | Unset
        if isinstance(_seller_type,  Unset):
            seller_type = UNSET
        else:
            seller_type = check_seller_type_enum(_seller_type)




        def _parse_secondary_contact_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        secondary_contact_email = _parse_secondary_contact_email(d.pop("secondary_contact_email", UNSET))


        def _parse_homepage(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        homepage = _parse_homepage(d.pop("homepage", UNSET))


        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_business_registration(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        business_registration = _parse_business_registration(d.pop("business_registration", UNSET))


        def _parse_tax_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        tax_id = _parse_tax_id(d.pop("tax_id", UNSET))


        def _parse_stripe_connect_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        stripe_connect_id = _parse_stripe_connect_id(d.pop("stripe_connect_id", UNSET))


        def _parse_stripe_payment_method_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        stripe_payment_method_id = _parse_stripe_payment_method_id(d.pop("stripe_payment_method_id", UNSET))


        _status = d.pop("status", UNSET)
        status: SellerStatusEnum | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_seller_status_enum(_status)




        is_verified = d.pop("is_verified", UNSET)

        _seller_tier = d.pop("seller_tier", UNSET)
        seller_tier: SellerTierEnum | Unset
        if isinstance(_seller_tier,  Unset):
            seller_tier = UNSET
        else:
            seller_tier = check_seller_tier_enum(_seller_tier)




        _preferred_payout_method = d.pop("preferred_payout_method", UNSET)
        preferred_payout_method: PayoutMethodEnum | Unset
        if isinstance(_preferred_payout_method,  Unset):
            preferred_payout_method = UNSET
        else:
            preferred_payout_method = check_payout_method_enum(_preferred_payout_method)




        _payout_schedule = d.pop("payout_schedule", UNSET)
        payout_schedule: PayoutScheduleEnum | Unset
        if isinstance(_payout_schedule,  Unset):
            payout_schedule = UNSET
        else:
            payout_schedule = check_payout_schedule_enum(_payout_schedule)




        def _parse_payout_threshold(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        payout_threshold = _parse_payout_threshold(d.pop("payout_threshold", UNSET))


        def _parse_zelle_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        zelle_email = _parse_zelle_email(d.pop("zelle_email", UNSET))


        def _parse_zelle_phone(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        zelle_phone = _parse_zelle_phone(d.pop("zelle_phone", UNSET))


        def _parse_check_payee_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_payee_name = _parse_check_payee_name(d.pop("check_payee_name", UNSET))


        def _parse_check_address_line1(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_address_line1 = _parse_check_address_line1(d.pop("check_address_line1", UNSET))


        def _parse_check_address_line2(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_address_line2 = _parse_check_address_line2(d.pop("check_address_line2", UNSET))


        def _parse_check_city(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_city = _parse_check_city(d.pop("check_city", UNSET))


        def _parse_check_state(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_state = _parse_check_state(d.pop("check_state", UNSET))


        def _parse_check_postal_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_postal_code = _parse_check_postal_code(d.pop("check_postal_code", UNSET))


        def _parse_check_country(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_country = _parse_check_country(d.pop("check_country", UNSET))


        review_count = d.pop("review_count", UNSET)

        def _parse_average_rating(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        average_rating = _parse_average_rating(d.pop("average_rating", UNSET))


        seller_public = cls(
            name=name,
            contact_email=contact_email,
            id=id,
            account_manager_id=account_manager_id,
            payout_window_months=payout_window_months,
            created_at=created_at,
            updated_at=updated_at,
            display_name=display_name,
            seller_type=seller_type,
            secondary_contact_email=secondary_contact_email,
            homepage=homepage,
            description=description,
            business_registration=business_registration,
            tax_id=tax_id,
            stripe_connect_id=stripe_connect_id,
            stripe_payment_method_id=stripe_payment_method_id,
            status=status,
            is_verified=is_verified,
            seller_tier=seller_tier,
            preferred_payout_method=preferred_payout_method,
            payout_schedule=payout_schedule,
            payout_threshold=payout_threshold,
            zelle_email=zelle_email,
            zelle_phone=zelle_phone,
            check_payee_name=check_payee_name,
            check_address_line1=check_address_line1,
            check_address_line2=check_address_line2,
            check_city=check_city,
            check_state=check_state,
            check_postal_code=check_postal_code,
            check_country=check_country,
            review_count=review_count,
            average_rating=average_rating,
        )


        seller_public.additional_properties = d
        return seller_public

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
