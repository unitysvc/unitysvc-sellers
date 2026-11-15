from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.live_state_enum import LiveStateEnum, check_live_state_enum
from ..types import UNSET, Unset

T = TypeVar("T", bound="LiveRequestLease")


@_attrs_define
class LiveRequestLease:
    target_member_id: UUID
    generation: str
    client_id: str
    first_requested_at: datetime.datetime
    available: bool
    """ Whether the target party has someone accepting requests now """
    state: LiveStateEnum
    """ A party's live help state (#2926), from its people's leases.

    - accepting: someone takes new live requests
    - draining: nobody takes new ones, but someone still serves the
      requests already waiting ("finishing queue")
    - off: neither """
    expires_in: int | Unset = 60
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        target_member_id = str(self.target_member_id)

        generation = self.generation

        client_id = self.client_id

        first_requested_at = self.first_requested_at.isoformat()

        available = self.available

        state: str = self.state

        expires_in = self.expires_in

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "target_member_id": target_member_id,
                "generation": generation,
                "client_id": client_id,
                "first_requested_at": first_requested_at,
                "available": available,
                "state": state,
            }
        )
        if expires_in is not UNSET:
            field_dict["expires_in"] = expires_in

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        target_member_id = UUID(d.pop("target_member_id"))

        generation = d.pop("generation")

        client_id = d.pop("client_id")

        first_requested_at = isoparse(d.pop("first_requested_at"))

        available = d.pop("available")

        state = check_live_state_enum(d.pop("state"))

        expires_in = d.pop("expires_in", UNSET)

        live_request_lease = cls(
            target_member_id=target_member_id,
            generation=generation,
            client_id=client_id,
            first_requested_at=first_requested_at,
            available=available,
            state=state,
            expires_in=expires_in,
        )

        live_request_lease.additional_properties = d
        return live_request_lease

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
