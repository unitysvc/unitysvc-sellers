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
  from ..models.user_usage_data_point import UserUsageDataPoint





T = TypeVar("T", bound="UserDashboardResponse")



@_attrs_define
class UserDashboardResponse:
    """ Response model for user dashboard queries.

     """

    user_id: UUID
    """ User ID """
    customer_id: UUID
    """ Customer ID (organization) """
    period: AggregationPeriod
    """ Time aggregation granularity for dashboard queries. """
    start_date: datetime.date
    """ Query start date """
    end_date: datetime.date
    """ Query end date """
    total_charge: str
    """ Total charge across all data points """
    total_requests: int
    """ Total requests across all data points """
    aggregated: bool | Unset = False
    """ Whether data is aggregated across subscriptions/listings """
    data: list[UserUsageDataPoint] | Unset = UNSET
    """ Usage data points """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.user_usage_data_point import UserUsageDataPoint
        user_id = str(self.user_id)

        customer_id = str(self.customer_id)

        period: str = self.period

        start_date = self.start_date.isoformat()

        end_date = self.end_date.isoformat()

        total_charge = self.total_charge

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
            "user_id": user_id,
            "customer_id": customer_id,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "total_charge": total_charge,
            "total_requests": total_requests,
        })
        if aggregated is not UNSET:
            field_dict["aggregated"] = aggregated
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_usage_data_point import UserUsageDataPoint
        d = dict(src_dict)
        user_id = UUID(d.pop("user_id"))




        customer_id = UUID(d.pop("customer_id"))




        period = check_aggregation_period(d.pop("period"))




        start_date = isoparse(d.pop("start_date")).date()




        end_date = isoparse(d.pop("end_date")).date()




        total_charge = d.pop("total_charge")

        total_requests = d.pop("total_requests")

        aggregated = d.pop("aggregated", UNSET)

        _data = d.pop("data", UNSET)
        data: list[UserUsageDataPoint] | Unset = UNSET
        if _data is not UNSET:
            data = []
            for data_item_data in _data:
                data_item = UserUsageDataPoint.from_dict(data_item_data)



                data.append(data_item)


        user_dashboard_response = cls(
            user_id=user_id,
            customer_id=customer_id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_charge=total_charge,
            total_requests=total_requests,
            aggregated=aggregated,
            data=data,
        )


        user_dashboard_response.additional_properties = d
        return user_dashboard_response

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
