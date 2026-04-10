from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.pricing_plan_tier_enum import check_pricing_plan_tier_enum
from ..models.pricing_plan_tier_enum import PricingPlanTierEnum
from typing import cast
from uuid import UUID






T = TypeVar("T", bound="PlanInfoPublic")



@_attrs_define
class PlanInfoPublic:
    """ Minimal plan info for response.

     """

    id: UUID
    name: str
    tier: PricingPlanTierEnum
    """ High-level usage plan tier categories. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        tier: str = self.tier


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "tier": tier,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        name = d.pop("name")

        tier = check_pricing_plan_tier_enum(d.pop("tier"))




        plan_info_public = cls(
            id=id,
            name=name,
            tier=tier,
        )


        plan_info_public.additional_properties = d
        return plan_info_public

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
