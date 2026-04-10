from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.rating_summary_distribution import RatingSummaryDistribution





T = TypeVar("T", bound="RatingSummary")



@_attrs_define
class RatingSummary:
    """ Rating summary for a target entity.

     """

    average: float | None | Unset = UNSET
    count: int | Unset = 0
    distribution: RatingSummaryDistribution | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.rating_summary_distribution import RatingSummaryDistribution
        average: float | None | Unset
        if isinstance(self.average, Unset):
            average = UNSET
        else:
            average = self.average

        count = self.count

        distribution: dict[str, Any] | Unset = UNSET
        if not isinstance(self.distribution, Unset):
            distribution = self.distribution.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if average is not UNSET:
            field_dict["average"] = average
        if count is not UNSET:
            field_dict["count"] = count
        if distribution is not UNSET:
            field_dict["distribution"] = distribution

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rating_summary_distribution import RatingSummaryDistribution
        d = dict(src_dict)
        def _parse_average(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        average = _parse_average(d.pop("average", UNSET))


        count = d.pop("count", UNSET)

        _distribution = d.pop("distribution", UNSET)
        distribution: RatingSummaryDistribution | Unset
        if isinstance(_distribution,  Unset):
            distribution = UNSET
        else:
            distribution = RatingSummaryDistribution.from_dict(_distribution)




        rating_summary = cls(
            average=average,
            count=count,
            distribution=distribution,
        )


        rating_summary.additional_properties = d
        return rating_summary

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
