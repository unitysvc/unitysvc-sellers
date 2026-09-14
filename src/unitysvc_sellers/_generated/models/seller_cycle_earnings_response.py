from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.seller_service_earning_public import SellerServiceEarningPublic


T = TypeVar("T", bound="SellerCycleEarningsResponse")


@_attrs_define
class SellerCycleEarningsResponse:
    """Cycle-to-date earnings for the authenticated seller.

    Mark-to-date: the same computation the monthly invoice worker runs,
    evaluated over days 1..today. On the final day of the cycle it is the
    invoice. See `provisional` for why it may still move.

    """

    cycle_start: datetime.date
    cycle_end: datetime.date
    as_of: datetime.datetime
    days_elapsed: int
    days_total: int
    currency: str
    request_count: int
    """ Total requests served this cycle """
    total_seller_charge: str
    total_payout: str
    """ Cycle-to-date earnings, mark-to-date """
    projected_total_payout: str
    """ Flat extrapolation to cycle end; a projection, not a quote """
    services: list[SellerServiceEarningPublic] | Unset = UNSET
    provisional: bool | Unset = False
    """ True when a contributing payout_price is volume-`tiered`, whose rate applies to ALL usage in the cycle.
    Earnings can then fall as traffic grows, because a later tier re-rates usage already served, so the figure is
    not settled until the cycle closes. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.seller_service_earning_public import SellerServiceEarningPublic

        cycle_start = self.cycle_start.isoformat()

        cycle_end = self.cycle_end.isoformat()

        as_of = self.as_of.isoformat()

        days_elapsed = self.days_elapsed

        days_total = self.days_total

        currency = self.currency

        request_count = self.request_count

        total_seller_charge = self.total_seller_charge

        total_payout = self.total_payout

        projected_total_payout = self.projected_total_payout

        services: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.services, Unset):
            services = []
            for services_item_data in self.services:
                services_item = services_item_data.to_dict()
                services.append(services_item)

        provisional = self.provisional

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cycle_start": cycle_start,
                "cycle_end": cycle_end,
                "as_of": as_of,
                "days_elapsed": days_elapsed,
                "days_total": days_total,
                "currency": currency,
                "request_count": request_count,
                "total_seller_charge": total_seller_charge,
                "total_payout": total_payout,
                "projected_total_payout": projected_total_payout,
            }
        )
        if services is not UNSET:
            field_dict["services"] = services
        if provisional is not UNSET:
            field_dict["provisional"] = provisional

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.seller_service_earning_public import SellerServiceEarningPublic

        d = dict(src_dict)
        cycle_start = isoparse(d.pop("cycle_start")).date()

        cycle_end = isoparse(d.pop("cycle_end")).date()

        as_of = isoparse(d.pop("as_of"))

        days_elapsed = d.pop("days_elapsed")

        days_total = d.pop("days_total")

        currency = d.pop("currency")

        request_count = d.pop("request_count")

        total_seller_charge = d.pop("total_seller_charge")

        total_payout = d.pop("total_payout")

        projected_total_payout = d.pop("projected_total_payout")

        _services = d.pop("services", UNSET)
        services: list[SellerServiceEarningPublic] | Unset = UNSET
        if _services is not UNSET:
            services = []
            for services_item_data in _services:
                services_item = SellerServiceEarningPublic.from_dict(services_item_data)

                services.append(services_item)

        provisional = d.pop("provisional", UNSET)

        seller_cycle_earnings_response = cls(
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            as_of=as_of,
            days_elapsed=days_elapsed,
            days_total=days_total,
            currency=currency,
            request_count=request_count,
            total_seller_charge=total_seller_charge,
            total_payout=total_payout,
            projected_total_payout=projected_total_payout,
            services=services,
            provisional=provisional,
        )

        seller_cycle_earnings_response.additional_properties = d
        return seller_cycle_earnings_response

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
