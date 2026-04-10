from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.seller_usage_data_point_usage_metrics import SellerUsageDataPointUsageMetrics





T = TypeVar("T", bound="SellerUsageDataPoint")



@_attrs_define
class SellerUsageDataPoint:
    """ A single data point for seller dashboard.

    When aggregate=true, service_id and customer_id may be None
    (data is aggregated across all listings/customers).

     """

    period_start: datetime.datetime
    """ Start of the time period """
    customer_charge: str
    """ Revenue from customer for this period """
    request_count: int
    """ Total requests """
    success_count: int
    """ Successful requests """
    error_count: int
    """ Failed requests """
    service_id: None | Unset | UUID = UNSET
    """ Service ID (None when aggregated across listings) """
    customer_id: None | Unset | UUID = UNSET
    """ Customer ID using the service (None when aggregated across customers) """
    usage_metrics: SellerUsageDataPointUsageMetrics | Unset = UNSET
    """ Aggregated usage metrics by key """
    avg_response_time_ms: float | None | Unset = UNSET
    """ Average response time """
    p95_response_time_ms: float | None | Unset = UNSET
    """ P95 response time """
    p99_response_time_ms: float | None | Unset = UNSET
    """ P99 response time """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.seller_usage_data_point_usage_metrics import SellerUsageDataPointUsageMetrics
        period_start = self.period_start.isoformat()

        customer_charge = self.customer_charge

        request_count = self.request_count

        success_count = self.success_count

        error_count = self.error_count

        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

        customer_id: None | str | Unset
        if isinstance(self.customer_id, Unset):
            customer_id = UNSET
        elif isinstance(self.customer_id, UUID):
            customer_id = str(self.customer_id)
        else:
            customer_id = self.customer_id

        usage_metrics: dict[str, Any] | Unset = UNSET
        if not isinstance(self.usage_metrics, Unset):
            usage_metrics = self.usage_metrics.to_dict()

        avg_response_time_ms: float | None | Unset
        if isinstance(self.avg_response_time_ms, Unset):
            avg_response_time_ms = UNSET
        else:
            avg_response_time_ms = self.avg_response_time_ms

        p95_response_time_ms: float | None | Unset
        if isinstance(self.p95_response_time_ms, Unset):
            p95_response_time_ms = UNSET
        else:
            p95_response_time_ms = self.p95_response_time_ms

        p99_response_time_ms: float | None | Unset
        if isinstance(self.p99_response_time_ms, Unset):
            p99_response_time_ms = UNSET
        else:
            p99_response_time_ms = self.p99_response_time_ms


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "period_start": period_start,
            "customer_charge": customer_charge,
            "request_count": request_count,
            "success_count": success_count,
            "error_count": error_count,
        })
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if customer_id is not UNSET:
            field_dict["customer_id"] = customer_id
        if usage_metrics is not UNSET:
            field_dict["usage_metrics"] = usage_metrics
        if avg_response_time_ms is not UNSET:
            field_dict["avg_response_time_ms"] = avg_response_time_ms
        if p95_response_time_ms is not UNSET:
            field_dict["p95_response_time_ms"] = p95_response_time_ms
        if p99_response_time_ms is not UNSET:
            field_dict["p99_response_time_ms"] = p99_response_time_ms

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.seller_usage_data_point_usage_metrics import SellerUsageDataPointUsageMetrics
        d = dict(src_dict)
        period_start = isoparse(d.pop("period_start"))




        customer_charge = d.pop("customer_charge")

        request_count = d.pop("request_count")

        success_count = d.pop("success_count")

        error_count = d.pop("error_count")

        def _parse_service_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_id_type_0 = UUID(data)



                return service_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        service_id = _parse_service_id(d.pop("service_id", UNSET))


        def _parse_customer_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                customer_id_type_0 = UUID(data)



                return customer_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        customer_id = _parse_customer_id(d.pop("customer_id", UNSET))


        _usage_metrics = d.pop("usage_metrics", UNSET)
        usage_metrics: SellerUsageDataPointUsageMetrics | Unset
        if isinstance(_usage_metrics,  Unset):
            usage_metrics = UNSET
        else:
            usage_metrics = SellerUsageDataPointUsageMetrics.from_dict(_usage_metrics)




        def _parse_avg_response_time_ms(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        avg_response_time_ms = _parse_avg_response_time_ms(d.pop("avg_response_time_ms", UNSET))


        def _parse_p95_response_time_ms(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        p95_response_time_ms = _parse_p95_response_time_ms(d.pop("p95_response_time_ms", UNSET))


        def _parse_p99_response_time_ms(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        p99_response_time_ms = _parse_p99_response_time_ms(d.pop("p99_response_time_ms", UNSET))


        seller_usage_data_point = cls(
            period_start=period_start,
            customer_charge=customer_charge,
            request_count=request_count,
            success_count=success_count,
            error_count=error_count,
            service_id=service_id,
            customer_id=customer_id,
            usage_metrics=usage_metrics,
            avg_response_time_ms=avg_response_time_ms,
            p95_response_time_ms=p95_response_time_ms,
            p99_response_time_ms=p99_response_time_ms,
        )


        seller_usage_data_point.additional_properties = d
        return seller_usage_data_point

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
