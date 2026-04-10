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
  from ..models.seller_usage_data_point import SellerUsageDataPoint





T = TypeVar("T", bound="SellerDashboardResponse")



@_attrs_define
class SellerDashboardResponse:
    """ Response model for seller dashboard queries.

     """

    seller_id: UUID
    """ Seller ID """
    period: AggregationPeriod
    """ Time aggregation granularity for dashboard queries. """
    start_date: datetime.date
    """ Query start date """
    end_date: datetime.date
    """ Query end date """
    total_revenue: str
    """ Total revenue across all data points """
    total_requests: int
    """ Total requests across all data points """
    aggregated: bool | Unset = False
    """ Whether data is aggregated across listings/customers """
    data: list[SellerUsageDataPoint] | Unset = UNSET
    """ Usage data points """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.seller_usage_data_point import SellerUsageDataPoint
        seller_id = str(self.seller_id)

        period: str = self.period

        start_date = self.start_date.isoformat()

        end_date = self.end_date.isoformat()

        total_revenue = self.total_revenue

        total_requests = self.total_requests

        aggregated = self.aggregated

        data: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = []
            for data_item_data in self.data:
                data_item = data_item_data.to_dict()
                data.append(data_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "seller_id": seller_id,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "total_revenue": total_revenue,
            "total_requests": total_requests,
        })
        if aggregated is not UNSET:
            field_dict["aggregated"] = aggregated
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.seller_usage_data_point import SellerUsageDataPoint
        d = dict(src_dict)
        seller_id = UUID(d.pop("seller_id"))




        period = check_aggregation_period(d.pop("period"))




        start_date = isoparse(d.pop("start_date")).date()




        end_date = isoparse(d.pop("end_date")).date()




        total_revenue = d.pop("total_revenue")

        total_requests = d.pop("total_requests")

        aggregated = d.pop("aggregated", UNSET)

        _data = d.pop("data", UNSET)
        data: list[SellerUsageDataPoint] | Unset = UNSET
        if _data is not UNSET:
            data = []
            for data_item_data in _data:
                data_item = SellerUsageDataPoint.from_dict(data_item_data)



                data.append(data_item)


        seller_dashboard_response = cls(
            seller_id=seller_id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_revenue=total_revenue,
            total_requests=total_requests,
            aggregated=aggregated,
            data=data,
        )


        seller_dashboard_response.additional_properties = d
        return seller_dashboard_response

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
