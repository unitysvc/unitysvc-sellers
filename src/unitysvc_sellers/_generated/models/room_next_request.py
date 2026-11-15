from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.room_work_ref import RoomWorkRef


T = TypeVar("T", bound="RoomNextRequest")


@_attrs_define
class RoomNextRequest:
    current: None | RoomWorkRef | Unset = UNSET
    """ Complete this room first, if the caller still holds its claim """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.room_work_ref import RoomWorkRef

        current: dict[str, Any] | None | Unset
        if isinstance(self.current, Unset):
            current = UNSET
        elif isinstance(self.current, RoomWorkRef):
            current = self.current.to_dict()
        else:
            current = self.current

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if current is not UNSET:
            field_dict["current"] = current

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.room_work_ref import RoomWorkRef

        d = dict(src_dict)

        def _parse_current(data: object) -> None | RoomWorkRef | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                current_type_0 = RoomWorkRef.from_dict(data)

                return current_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RoomWorkRef | Unset, data)

        current = _parse_current(d.pop("current", UNSET))

        room_next_request = cls(
            current=current,
        )

        room_next_request.additional_properties = d
        return room_next_request

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
