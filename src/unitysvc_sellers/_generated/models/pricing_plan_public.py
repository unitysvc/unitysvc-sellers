from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.pricing_plan_status_enum import check_pricing_plan_status_enum
from ..models.pricing_plan_status_enum import PricingPlanStatusEnum
from ..models.pricing_plan_tier_enum import check_pricing_plan_tier_enum
from ..models.pricing_plan_tier_enum import PricingPlanTierEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.pricing_plan_public_extra_metadata_type_0 import PricingPlanPublicExtraMetadataType0
  from ..models.pricing_plan_public_plan_pricing_type_0 import PricingPlanPublicPlanPricingType0
  from ..models.pricing_plan_public_terms import PricingPlanPublicTerms





T = TypeVar("T", bound="PricingPlanPublic")



@_attrs_define
class PricingPlanPublic:
    """ Public plan information for API responses.

     """

    name: str
    """ Plan name (e.g., 'Pro', 'Team', 'Enterprise - Acme') """
    slug: str
    """ Unique plan identifier (e.g., 'pro-2025-v1', 'enterprise-acme') """
    tier: PricingPlanTierEnum
    """ High-level usage plan tier categories. """
    display_name: str
    """ Human-readable display name """
    base_amount: str
    """ Base monthly price """
    terms: PricingPlanPublicTerms
    """ Plan terms (features, limits, SLA) """
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: None | str | Unset = UNSET
    """ Plan description """
    status: PricingPlanStatusEnum | Unset = UNSET
    """ Usage plan lifecycle and visibility status.

    - incomplete: Plan is being drafted/configured, can be updated
    - active: Plan is live and shown on public pricing page, immutable
    - private: Plan is live but hidden (custom/enterprise plans), immutable
    - expired: Plan is archived, no longer available for new subscriptions """
    valid_from: datetime.datetime | Unset = UNSET
    """ Plan availability start date """
    valid_until: datetime.datetime | None | Unset = UNSET
    """ Plan availability end date (None = no end) """
    annual_discount_percent: int | Unset = 0
    """ Discount percentage for annual billing (0-100) """
    currency: str | Unset = 'USD'
    """ Currency code """
    included_seats: int | None | Unset = UNSET
    """ Number of seats included in base_amount. None = flat pricing (quantity ignored). 0 = simple per-seat
    (base_amount ignored, additional_seat_price * quantity). N = tiered (base_amount covers N seats,
    additional_seat_price per extra). """
    additional_seat_price: None | str | Unset = UNSET
    """ Price per seat beyond included_seats. Required when included_seats is set. """
    stripe_product_id: None | str | Unset = UNSET
    """ Stripe product ID """
    stripe_price_id_monthly: None | str | Unset = UNSET
    """ Stripe price ID for monthly billing """
    stripe_price_id_annual: None | str | Unset = UNSET
    """ Stripe price ID for annual billing """
    plan_pricing: None | PricingPlanPublicPlanPricingType0 | Unset = UNSET
    """ Plan-level pricing that replaces per-request charges at statement time. Supports graduated/tiered pricing
    based on total_customer_charge or request_count. """
    extra_metadata: None | PricingPlanPublicExtraMetadataType0 | Unset = UNSET
    """ Additional metadata """
    allowed_domains: list[str] | None | Unset = UNSET
    """ Email domains that qualify for this plan (e.g., ['acme.com', 'acme.co.uk']). Used for enterprise plans to
    auto-enroll users based on email domain. """
    auto_enroll: bool | Unset = False
    """ If true, users with matching email domains are automatically enrolled. If false, users need an invite code
    to join (like team plans). """





    def to_dict(self) -> dict[str, Any]:
        from ..models.pricing_plan_public_extra_metadata_type_0 import PricingPlanPublicExtraMetadataType0
        from ..models.pricing_plan_public_plan_pricing_type_0 import PricingPlanPublicPlanPricingType0
        from ..models.pricing_plan_public_terms import PricingPlanPublicTerms
        name = self.name

        slug = self.slug

        tier: str = self.tier

        display_name = self.display_name

        base_amount = self.base_amount

        terms = self.terms.to_dict()

        id = str(self.id)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status


        valid_from: str | Unset = UNSET
        if not isinstance(self.valid_from, Unset):
            valid_from = self.valid_from.isoformat()

        valid_until: None | str | Unset
        if isinstance(self.valid_until, Unset):
            valid_until = UNSET
        elif isinstance(self.valid_until, datetime.datetime):
            valid_until = self.valid_until.isoformat()
        else:
            valid_until = self.valid_until

        annual_discount_percent = self.annual_discount_percent

        currency = self.currency

        included_seats: int | None | Unset
        if isinstance(self.included_seats, Unset):
            included_seats = UNSET
        else:
            included_seats = self.included_seats

        additional_seat_price: None | str | Unset
        if isinstance(self.additional_seat_price, Unset):
            additional_seat_price = UNSET
        else:
            additional_seat_price = self.additional_seat_price

        stripe_product_id: None | str | Unset
        if isinstance(self.stripe_product_id, Unset):
            stripe_product_id = UNSET
        else:
            stripe_product_id = self.stripe_product_id

        stripe_price_id_monthly: None | str | Unset
        if isinstance(self.stripe_price_id_monthly, Unset):
            stripe_price_id_monthly = UNSET
        else:
            stripe_price_id_monthly = self.stripe_price_id_monthly

        stripe_price_id_annual: None | str | Unset
        if isinstance(self.stripe_price_id_annual, Unset):
            stripe_price_id_annual = UNSET
        else:
            stripe_price_id_annual = self.stripe_price_id_annual

        plan_pricing: dict[str, Any] | None | Unset
        if isinstance(self.plan_pricing, Unset):
            plan_pricing = UNSET
        elif isinstance(self.plan_pricing, PricingPlanPublicPlanPricingType0):
            plan_pricing = self.plan_pricing.to_dict()
        else:
            plan_pricing = self.plan_pricing

        extra_metadata: dict[str, Any] | None | Unset
        if isinstance(self.extra_metadata, Unset):
            extra_metadata = UNSET
        elif isinstance(self.extra_metadata, PricingPlanPublicExtraMetadataType0):
            extra_metadata = self.extra_metadata.to_dict()
        else:
            extra_metadata = self.extra_metadata

        allowed_domains: list[str] | None | Unset
        if isinstance(self.allowed_domains, Unset):
            allowed_domains = UNSET
        elif isinstance(self.allowed_domains, list):
            allowed_domains = self.allowed_domains


        else:
            allowed_domains = self.allowed_domains

        auto_enroll = self.auto_enroll


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "name": name,
            "slug": slug,
            "tier": tier,
            "display_name": display_name,
            "base_amount": base_amount,
            "terms": terms,
            "id": id,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if status is not UNSET:
            field_dict["status"] = status
        if valid_from is not UNSET:
            field_dict["valid_from"] = valid_from
        if valid_until is not UNSET:
            field_dict["valid_until"] = valid_until
        if annual_discount_percent is not UNSET:
            field_dict["annual_discount_percent"] = annual_discount_percent
        if currency is not UNSET:
            field_dict["currency"] = currency
        if included_seats is not UNSET:
            field_dict["included_seats"] = included_seats
        if additional_seat_price is not UNSET:
            field_dict["additional_seat_price"] = additional_seat_price
        if stripe_product_id is not UNSET:
            field_dict["stripe_product_id"] = stripe_product_id
        if stripe_price_id_monthly is not UNSET:
            field_dict["stripe_price_id_monthly"] = stripe_price_id_monthly
        if stripe_price_id_annual is not UNSET:
            field_dict["stripe_price_id_annual"] = stripe_price_id_annual
        if plan_pricing is not UNSET:
            field_dict["plan_pricing"] = plan_pricing
        if extra_metadata is not UNSET:
            field_dict["extra_metadata"] = extra_metadata
        if allowed_domains is not UNSET:
            field_dict["allowed_domains"] = allowed_domains
        if auto_enroll is not UNSET:
            field_dict["auto_enroll"] = auto_enroll

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pricing_plan_public_extra_metadata_type_0 import PricingPlanPublicExtraMetadataType0
        from ..models.pricing_plan_public_plan_pricing_type_0 import PricingPlanPublicPlanPricingType0
        from ..models.pricing_plan_public_terms import PricingPlanPublicTerms
        d = dict(src_dict)
        name = d.pop("name")

        slug = d.pop("slug")

        tier = check_pricing_plan_tier_enum(d.pop("tier"))




        display_name = d.pop("display_name")

        base_amount = d.pop("base_amount")

        terms = PricingPlanPublicTerms.from_dict(d.pop("terms"))




        id = UUID(d.pop("id"))




        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        _status = d.pop("status", UNSET)
        status: PricingPlanStatusEnum | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_pricing_plan_status_enum(_status)




        _valid_from = d.pop("valid_from", UNSET)
        valid_from: datetime.datetime | Unset
        if isinstance(_valid_from,  Unset):
            valid_from = UNSET
        else:
            valid_from = isoparse(_valid_from)




        def _parse_valid_until(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                valid_until_type_0 = isoparse(data)



                return valid_until_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        valid_until = _parse_valid_until(d.pop("valid_until", UNSET))


        annual_discount_percent = d.pop("annual_discount_percent", UNSET)

        currency = d.pop("currency", UNSET)

        def _parse_included_seats(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        included_seats = _parse_included_seats(d.pop("included_seats", UNSET))


        def _parse_additional_seat_price(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        additional_seat_price = _parse_additional_seat_price(d.pop("additional_seat_price", UNSET))


        def _parse_stripe_product_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        stripe_product_id = _parse_stripe_product_id(d.pop("stripe_product_id", UNSET))


        def _parse_stripe_price_id_monthly(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        stripe_price_id_monthly = _parse_stripe_price_id_monthly(d.pop("stripe_price_id_monthly", UNSET))


        def _parse_stripe_price_id_annual(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        stripe_price_id_annual = _parse_stripe_price_id_annual(d.pop("stripe_price_id_annual", UNSET))


        def _parse_plan_pricing(data: object) -> None | PricingPlanPublicPlanPricingType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                plan_pricing_type_0 = PricingPlanPublicPlanPricingType0.from_dict(data)



                return plan_pricing_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PricingPlanPublicPlanPricingType0 | Unset, data)

        plan_pricing = _parse_plan_pricing(d.pop("plan_pricing", UNSET))


        def _parse_extra_metadata(data: object) -> None | PricingPlanPublicExtraMetadataType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_metadata_type_0 = PricingPlanPublicExtraMetadataType0.from_dict(data)



                return extra_metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PricingPlanPublicExtraMetadataType0 | Unset, data)

        extra_metadata = _parse_extra_metadata(d.pop("extra_metadata", UNSET))


        def _parse_allowed_domains(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                allowed_domains_type_0 = cast(list[str], data)

                return allowed_domains_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        allowed_domains = _parse_allowed_domains(d.pop("allowed_domains", UNSET))


        auto_enroll = d.pop("auto_enroll", UNSET)

        pricing_plan_public = cls(
            name=name,
            slug=slug,
            tier=tier,
            display_name=display_name,
            base_amount=base_amount,
            terms=terms,
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            status=status,
            valid_from=valid_from,
            valid_until=valid_until,
            annual_discount_percent=annual_discount_percent,
            currency=currency,
            included_seats=included_seats,
            additional_seat_price=additional_seat_price,
            stripe_product_id=stripe_product_id,
            stripe_price_id_monthly=stripe_price_id_monthly,
            stripe_price_id_annual=stripe_price_id_annual,
            plan_pricing=plan_pricing,
            extra_metadata=extra_metadata,
            allowed_domains=allowed_domains,
            auto_enroll=auto_enroll,
        )

        return pricing_plan_public

