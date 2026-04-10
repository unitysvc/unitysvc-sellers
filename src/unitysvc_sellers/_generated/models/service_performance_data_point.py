from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="ServicePerformanceDataPoint")



@_attrs_define
class ServicePerformanceDataPoint:
    """ A single data point for service performance dashboard.

     """

    period_start: datetime.datetime
    """ Start of the time period """
    request_count: int
    """ Total requests """
    success_count: int
    """ Successful requests """
    error_count: int
    """ Failed requests """
    avg_response_time_ms: float
    """ Average response time """
    p95_response_time_ms: float
    """ P95 response time """
    p99_response_time_ms: float
    """ P99 response time """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        period_start = self.period_start.isoformat()

        request_count = self.request_count

        success_count = self.success_count

        error_count = self.error_count

        avg_response_time_ms = self.avg_response_time_ms

        p95_response_time_ms = self.p95_response_time_ms

        p99_response_time_ms = self.p99_response_time_ms


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "period_start": period_start,
            "request_count": request_count,
            "success_count": success_count,
            "error_count": error_count,
            "avg_response_time_ms": avg_response_time_ms,
            "p95_response_time_ms": p95_response_time_ms,
            "p99_response_time_ms": p99_response_time_ms,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        period_start = isoparse(d.pop("period_start"))




        request_count = d.pop("request_count")

        success_count = d.pop("success_count")

        error_count = d.pop("error_count")

        avg_response_time_ms = d.pop("avg_response_time_ms")

        p95_response_time_ms = d.pop("p95_response_time_ms")

        p99_response_time_ms = d.pop("p99_response_time_ms")

        service_performance_data_point = cls(
            period_start=period_start,
            request_count=request_count,
            success_count=success_count,
            error_count=error_count,
            avg_response_time_ms=avg_response_time_ms,
            p95_response_time_ms=p95_response_time_ms,
            p99_response_time_ms=p99_response_time_ms,
        )


        service_performance_data_point.additional_properties = d
        return service_performance_data_point

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
