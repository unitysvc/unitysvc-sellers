from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.live_state_enum import LiveStateEnum, check_live_state_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.live_request_view import LiveRequestView


T = TypeVar("T", bound="LivePartyStatus")


@_attrs_define
class LivePartyStatus:
    """One other member of the room: whether its party is accepting requests,
    and the room's live request to it. Never who is accepting.

    """

    member_id: UUID
    account_type: str
    available: bool
    """ Whether ``state`` is ``accepting`` """
    state: LiveStateEnum
    """ A party's live help state (#2926), from its people's leases.

    - accepting: someone takes new live requests
    - draining: nobody takes new ones, but someone still serves the
      requests already waiting ("finishing queue")
    - off: neither """
    name: None | str | Unset = UNSET
    request: LiveRequestView | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.live_request_view import LiveRequestView

        member_id = str(self.member_id)

        account_type = self.account_type

        available = self.available

        state: str = self.state

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        request: dict[str, Any] | None | Unset
        if isinstance(self.request, Unset):
            request = UNSET
        elif isinstance(self.request, LiveRequestView):
            request = self.request.to_dict()
        else:
            request = self.request

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "member_id": member_id,
                "account_type": account_type,
                "available": available,
                "state": state,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if request is not UNSET:
            field_dict["request"] = request

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.live_request_view import LiveRequestView

        d = dict(src_dict)
        member_id = UUID(d.pop("member_id"))

        account_type = d.pop("account_type")

        available = d.pop("available")

        state = check_live_state_enum(d.pop("state"))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_request(data: object) -> LiveRequestView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                request_type_0 = LiveRequestView.from_dict(data)

                return request_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(LiveRequestView | None | Unset, data)

        request = _parse_request(d.pop("request", UNSET))

        live_party_status = cls(
            member_id=member_id,
            account_type=account_type,
            available=available,
            state=state,
            name=name,
            request=request,
        )

        live_party_status.additional_properties = d
        return live_party_status

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
