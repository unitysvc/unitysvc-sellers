from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NextTierPublic")


@_attrs_define
class NextTierPublic:
    """The next volume threshold that will re-rate a tiered payout cycle.

    Present only for a service on a top-level `tiered` payout_price that has
    not yet reached its final tier. Lets the UI warn before the headline
    moves, instead of leaving a correct drop looking like a bug.

    """

    based_on: str
    """ request_count | customer_charge | usage field """
    current: str
    """ Cycle-to-date value of that metric """
    threshold: str
    """ Value at which the rate changes for the whole cycle """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        based_on = self.based_on

        current = self.current

        threshold = self.threshold

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "based_on": based_on,
                "current": current,
                "threshold": threshold,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        based_on = d.pop("based_on")

        current = d.pop("current")

        threshold = d.pop("threshold")

        next_tier_public = cls(
            based_on=based_on,
            current=current,
            threshold=threshold,
        )

        next_tier_public.additional_properties = d
        return next_tier_public

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
