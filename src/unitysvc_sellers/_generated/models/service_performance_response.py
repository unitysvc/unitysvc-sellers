from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.aggregation_period import AggregationPeriod
from ..models.aggregation_period import check_aggregation_period
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.service_performance_data_point import ServicePerformanceDataPoint





T = TypeVar("T", bound="ServicePerformanceResponse")



@_attrs_define
class ServicePerformanceResponse:
    """ Response model for service performance queries.

     """

    service_id: UUID
    """ Service ID """
    period: AggregationPeriod
    """ Time aggregation granularity for dashboard queries. """
    start_date: datetime.date
    """ Query start date """
    end_date: datetime.date
    """ Query end date """
    total_requests: int
    """ Total requests across all data points """
    overall_success_rate: float
    """ Overall success rate percentage """
    overall_avg_response_time_ms: float
    """ Overall average response time """
    data: list[ServicePerformanceDataPoint] | Unset = UNSET
    """ Performance data points """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_performance_data_point import ServicePerformanceDataPoint
        service_id = str(self.service_id)

        period: str = self.period

        start_date = self.start_date.isoformat()

        end_date = self.end_date.isoformat()

        total_requests = self.total_requests

        overall_success_rate = self.overall_success_rate

        overall_avg_response_time_ms = self.overall_avg_response_time_ms

        data: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = []
            for data_item_data in self.data:
                data_item = data_item_data.to_dict()
                data.append(data_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "service_id": service_id,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "total_requests": total_requests,
            "overall_success_rate": overall_success_rate,
            "overall_avg_response_time_ms": overall_avg_response_time_ms,
        })
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_performance_data_point import ServicePerformanceDataPoint
        d = dict(src_dict)
        service_id = UUID(d.pop("service_id"))




        period = check_aggregation_period(d.pop("period"))




        start_date = isoparse(d.pop("start_date")).date()




        end_date = isoparse(d.pop("end_date")).date()




        total_requests = d.pop("total_requests")

        overall_success_rate = d.pop("overall_success_rate")

        overall_avg_response_time_ms = d.pop("overall_avg_response_time_ms")

        _data = d.pop("data", UNSET)
        data: list[ServicePerformanceDataPoint] | Unset = UNSET
        if _data is not UNSET:
            data = []
            for data_item_data in _data:
                data_item = ServicePerformanceDataPoint.from_dict(data_item_data)



                data.append(data_item)


        service_performance_response = cls(
            service_id=service_id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_requests=total_requests,
            overall_success_rate=overall_success_rate,
            overall_avg_response_time_ms=overall_avg_response_time_ms,
            data=data,
        )


        service_performance_response.additional_properties = d
        return service_performance_response

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
