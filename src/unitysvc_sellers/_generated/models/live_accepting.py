from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.live_accepting_mode import LiveAcceptingMode, check_live_accepting_mode
from ..types import UNSET, Unset

T = TypeVar("T", bound="LiveAccepting")


@_attrs_define
class LiveAccepting:
    client_id: None | str | Unset = UNSET
    """ Renew this client's lease; omit to start one """
    mode: LiveAcceptingMode | Unset = "accepting"
    """ ``accepting`` takes new live requests; ``draining`` (finishing the queue) takes none but keeps serving the
    ones waiting. Renewing in the other mode switches this client's lease. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_id: None | str | Unset
        if isinstance(self.client_id, Unset):
            client_id = UNSET
        else:
            client_id = self.client_id

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if mode is not UNSET:
            field_dict["mode"] = mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_client_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        client_id = _parse_client_id(d.pop("client_id", UNSET))

        _mode = d.pop("mode", UNSET)
        mode: LiveAcceptingMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = check_live_accepting_mode(_mode)

        live_accepting = cls(
            client_id=client_id,
            mode=mode,
        )

        live_accepting.additional_properties = d
        return live_accepting

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
