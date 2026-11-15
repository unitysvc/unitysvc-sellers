from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="LiveRequestView")


@_attrs_define
class LiveRequestView:
    generation: str
    first_requested_at: datetime.datetime
    requesters: int
    """ How many people are waiting in it """
    mine: bool
    """ Whether the caller is one of them """
    position: int | None | Unset = UNSET
    """ Your request's place in the supporting party's waiting line, 1 for next; only on your own request (``mine``)
    """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        generation = self.generation

        first_requested_at = self.first_requested_at.isoformat()

        requesters = self.requesters

        mine = self.mine

        position: int | None | Unset
        if isinstance(self.position, Unset):
            position = UNSET
        else:
            position = self.position

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "generation": generation,
                "first_requested_at": first_requested_at,
                "requesters": requesters,
                "mine": mine,
            }
        )
        if position is not UNSET:
            field_dict["position"] = position

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        generation = d.pop("generation")

        first_requested_at = isoparse(d.pop("first_requested_at"))

        requesters = d.pop("requesters")

        mine = d.pop("mine")

        def _parse_position(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        position = _parse_position(d.pop("position", UNSET))

        live_request_view = cls(
            generation=generation,
            first_requested_at=first_requested_at,
            requesters=requesters,
            mine=mine,
            position=position,
        )

        live_request_view.additional_properties = d
        return live_request_view

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
