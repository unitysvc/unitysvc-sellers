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
import datetime

if TYPE_CHECKING:
  from ..models.pricing_plan_data_extra_metadata_type_0 import PricingPlanDataExtraMetadataType0
  from ..models.pricing_plan_data_plan_pricing_type_0 import PricingPlanDataPlanPricingType0
  from ..models.pricing_plan_data_terms import PricingPlanDataTerms





T = TypeVar("T", bound="PricingPlanData")



@_attrs_define
class PricingPlanData:
    """ Schema for publishing a usage plan from unitysvc_admin CLI.

    This data type contains user-facing complete data for the usage plan,
    but lacks database-related IDs that are assigned by the system. It represents
    the full data payload from the CLI or API input before database persistence.

    Key characteristics:
    - Used for publishing plans via unitysvc_admin publish pricing_plan
    - Uses slug as the unique identifier (resolved by publish layer)
    - Does not include system-generated fields (id, created_at, updated_at)
    - Does not include Stripe IDs (assigned later when syncing to Stripe)
    - Does not include created_by_id (handled by publish layer)
    - Contains all plan definition data provided by admin

     """

    slug: str
    """ Unique plan identifier (e.g., 'pro-2025-v1', 'enterprise-acme') """
    name: str
    """ Plan name (e.g., 'Pro', 'Team', 'Enterprise') """
    tier: PricingPlanTierEnum
    """ High-level usage plan tier categories. """
    display_name: str
    """ Human-readable display name """
    base_amount: float | str
    """ Base price per billing interval """
    terms: PricingPlanDataTerms
    """ Plan terms (features, limits, SLA) """
    description: None | str | Unset = UNSET
    """ Plan description """
    status: PricingPlanStatusEnum | Unset = UNSET
    """ Usage plan lifecycle and visibility status.

    - incomplete: Plan is being drafted/configured, can be updated
    - active: Plan is live and shown on public pricing page, immutable
    - private: Plan is live but hidden (custom/enterprise plans), immutable
    - expired: Plan is archived, no longer available for new subscriptions """
    valid_from: datetime.datetime | None | Unset = UNSET
    """ Plan availability start date (defaults to now) """
    valid_until: datetime.datetime | None | Unset = UNSET
    """ Plan availability end date (None = no end) """
    annual_discount_percent: int | Unset = 0
    """ Discount percentage for annual billing (0-100) """
    currency: str | Unset = 'USD'
    """ Currency code """
    included_seats: int | None | Unset = UNSET
    """ Number of seats included in base_amount. None = flat pricing, 0 = simple per-seat, N = tiered. """
    additional_seat_price: float | None | str | Unset = UNSET
    """ Price per seat beyond included_seats """
    plan_pricing: None | PricingPlanDataPlanPricingType0 | Unset = UNSET
    """ Plan-level pricing that replaces per-request charges at statement time """
    extra_metadata: None | PricingPlanDataExtraMetadataType0 | Unset = UNSET
    """ Additional metadata (templates, taglines, etc.) """
    allowed_domains: list[str] | None | Unset = UNSET
    """ Email domains that auto-enroll users to this plan (enterprise plans) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.pricing_plan_data_extra_metadata_type_0 import PricingPlanDataExtraMetadataType0
        from ..models.pricing_plan_data_plan_pricing_type_0 import PricingPlanDataPlanPricingType0
        from ..models.pricing_plan_data_terms import PricingPlanDataTerms
        slug = self.slug

        name = self.name

        tier: str = self.tier

        display_name = self.display_name

        base_amount: float | str
        base_amount = self.base_amount

        terms = self.terms.to_dict()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status


        valid_from: None | str | Unset
        if isinstance(self.valid_from, Unset):
            valid_from = UNSET
        elif isinstance(self.valid_from, datetime.datetime):
            valid_from = self.valid_from.isoformat()
        else:
            valid_from = self.valid_from

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

        additional_seat_price: float | None | str | Unset
        if isinstance(self.additional_seat_price, Unset):
            additional_seat_price = UNSET
        else:
            additional_seat_price = self.additional_seat_price

        plan_pricing: dict[str, Any] | None | Unset
        if isinstance(self.plan_pricing, Unset):
            plan_pricing = UNSET
        elif isinstance(self.plan_pricing, PricingPlanDataPlanPricingType0):
            plan_pricing = self.plan_pricing.to_dict()
        else:
            plan_pricing = self.plan_pricing

        extra_metadata: dict[str, Any] | None | Unset
        if isinstance(self.extra_metadata, Unset):
            extra_metadata = UNSET
        elif isinstance(self.extra_metadata, PricingPlanDataExtraMetadataType0):
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


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "slug": slug,
            "name": name,
            "tier": tier,
            "display_name": display_name,
            "base_amount": base_amount,
            "terms": terms,
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
        if plan_pricing is not UNSET:
            field_dict["plan_pricing"] = plan_pricing
        if extra_metadata is not UNSET:
            field_dict["extra_metadata"] = extra_metadata
        if allowed_domains is not UNSET:
            field_dict["allowed_domains"] = allowed_domains

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pricing_plan_data_extra_metadata_type_0 import PricingPlanDataExtraMetadataType0
        from ..models.pricing_plan_data_plan_pricing_type_0 import PricingPlanDataPlanPricingType0
        from ..models.pricing_plan_data_terms import PricingPlanDataTerms
        d = dict(src_dict)
        slug = d.pop("slug")

        name = d.pop("name")

        tier = check_pricing_plan_tier_enum(d.pop("tier"))




        display_name = d.pop("display_name")

        def _parse_base_amount(data: object) -> float | str:
            return cast(float | str, data)

        base_amount = _parse_base_amount(d.pop("base_amount"))


        terms = PricingPlanDataTerms.from_dict(d.pop("terms"))




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




        def _parse_valid_from(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                valid_from_type_0 = isoparse(data)



                return valid_from_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        valid_from = _parse_valid_from(d.pop("valid_from", UNSET))


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


        def _parse_additional_seat_price(data: object) -> float | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | str | Unset, data)

        additional_seat_price = _parse_additional_seat_price(d.pop("additional_seat_price", UNSET))


        def _parse_plan_pricing(data: object) -> None | PricingPlanDataPlanPricingType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                plan_pricing_type_0 = PricingPlanDataPlanPricingType0.from_dict(data)



                return plan_pricing_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PricingPlanDataPlanPricingType0 | Unset, data)

        plan_pricing = _parse_plan_pricing(d.pop("plan_pricing", UNSET))


        def _parse_extra_metadata(data: object) -> None | PricingPlanDataExtraMetadataType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_metadata_type_0 = PricingPlanDataExtraMetadataType0.from_dict(data)



                return extra_metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PricingPlanDataExtraMetadataType0 | Unset, data)

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


        pricing_plan_data = cls(
            slug=slug,
            name=name,
            tier=tier,
            display_name=display_name,
            base_amount=base_amount,
            terms=terms,
            description=description,
            status=status,
            valid_from=valid_from,
            valid_until=valid_until,
            annual_discount_percent=annual_discount_percent,
            currency=currency,
            included_seats=included_seats,
            additional_seat_price=additional_seat_price,
            plan_pricing=plan_pricing,
            extra_metadata=extra_metadata,
            allowed_domains=allowed_domains,
        )


        pricing_plan_data.additional_properties = d
        return pricing_plan_data

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
