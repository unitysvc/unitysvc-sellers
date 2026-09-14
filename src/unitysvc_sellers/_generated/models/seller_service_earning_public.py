from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.next_tier_public import NextTierPublic
    from ..models.seller_service_earning_public_usage_metrics import SellerServiceEarningPublicUsageMetrics


T = TypeVar("T", bound="SellerServiceEarningPublic")


@_attrs_define
class SellerServiceEarningPublic:
    """One service's usage and earnings for the seller's billing cycle."""

    service_id: UUID
    service_name: str
    """ Service name, blank if since deleted """
    request_count: int
    success_count: int
    error_count: int
    seller_charge: str
    """ Charge attributable to the seller before payout_price """
    payout: str
    """ What the seller earns: seller_charge with payout_price applied """
    channel: str | Unset = ""
    """ Upstream access channel used """
    usage_metrics: SellerServiceEarningPublicUsageMetrics | Unset = UNSET
    currency: str | Unset = "USD"
    """ Currency of the pricing bundle """
    next_tier: NextTierPublic | None | Unset = UNSET
    """ Next volume threshold that re-rates this cycle, for a tiered payout that has not reached its final tier.
    Null otherwise. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.next_tier_public import NextTierPublic
        from ..models.seller_service_earning_public_usage_metrics import SellerServiceEarningPublicUsageMetrics

        service_id = str(self.service_id)

        service_name = self.service_name

        request_count = self.request_count

        success_count = self.success_count

        error_count = self.error_count

        seller_charge = self.seller_charge

        payout = self.payout

        channel = self.channel

        usage_metrics: dict[str, Any] | Unset = UNSET
        if not isinstance(self.usage_metrics, Unset):
            usage_metrics = self.usage_metrics.to_dict()

        currency = self.currency

        next_tier: dict[str, Any] | None | Unset
        if isinstance(self.next_tier, Unset):
            next_tier = UNSET
        elif isinstance(self.next_tier, NextTierPublic):
            next_tier = self.next_tier.to_dict()
        else:
            next_tier = self.next_tier

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service_id": service_id,
                "service_name": service_name,
                "request_count": request_count,
                "success_count": success_count,
                "error_count": error_count,
                "seller_charge": seller_charge,
                "payout": payout,
            }
        )
        if channel is not UNSET:
            field_dict["channel"] = channel
        if usage_metrics is not UNSET:
            field_dict["usage_metrics"] = usage_metrics
        if currency is not UNSET:
            field_dict["currency"] = currency
        if next_tier is not UNSET:
            field_dict["next_tier"] = next_tier

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.next_tier_public import NextTierPublic
        from ..models.seller_service_earning_public_usage_metrics import SellerServiceEarningPublicUsageMetrics

        d = dict(src_dict)
        service_id = UUID(d.pop("service_id"))

        service_name = d.pop("service_name")

        request_count = d.pop("request_count")

        success_count = d.pop("success_count")

        error_count = d.pop("error_count")

        seller_charge = d.pop("seller_charge")

        payout = d.pop("payout")

        channel = d.pop("channel", UNSET)

        _usage_metrics = d.pop("usage_metrics", UNSET)
        usage_metrics: SellerServiceEarningPublicUsageMetrics | Unset
        if isinstance(_usage_metrics, Unset):
            usage_metrics = UNSET
        else:
            usage_metrics = SellerServiceEarningPublicUsageMetrics.from_dict(_usage_metrics)

        currency = d.pop("currency", UNSET)

        def _parse_next_tier(data: object) -> NextTierPublic | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                next_tier_type_0 = NextTierPublic.from_dict(data)

                return next_tier_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(NextTierPublic | None | Unset, data)

        next_tier = _parse_next_tier(d.pop("next_tier", UNSET))

        seller_service_earning_public = cls(
            service_id=service_id,
            service_name=service_name,
            request_count=request_count,
            success_count=success_count,
            error_count=error_count,
            seller_charge=seller_charge,
            payout=payout,
            channel=channel,
            usage_metrics=usage_metrics,
            currency=currency,
            next_tier=next_tier,
        )

        seller_service_earning_public.additional_properties = d
        return seller_service_earning_public

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
