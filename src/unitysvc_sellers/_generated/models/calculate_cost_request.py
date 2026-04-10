from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.calculate_cost_request_usage_metrics import CalculateCostRequestUsageMetrics





T = TypeVar("T", bound="CalculateCostRequest")



@_attrs_define
class CalculateCostRequest:
    """ Request body for the calculate-cost endpoint.

     """

    bundle_id: UUID
    """ Pricing bundle UUID """
    usage_metrics: CalculateCostRequestUsageMetrics
    """ Usage metrics (e.g., input_tokens, output_tokens, duration_seconds) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.calculate_cost_request_usage_metrics import CalculateCostRequestUsageMetrics
        bundle_id = str(self.bundle_id)

        usage_metrics = self.usage_metrics.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "bundle_id": bundle_id,
            "usage_metrics": usage_metrics,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.calculate_cost_request_usage_metrics import CalculateCostRequestUsageMetrics
        d = dict(src_dict)
        bundle_id = UUID(d.pop("bundle_id"))




        usage_metrics = CalculateCostRequestUsageMetrics.from_dict(d.pop("usage_metrics"))




        calculate_cost_request = cls(
            bundle_id=bundle_id,
            usage_metrics=usage_metrics,
        )


        calculate_cost_request.additional_properties = d
        return calculate_cost_request

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
