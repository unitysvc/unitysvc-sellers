from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="RoomAttention")


@_attrs_define
class RoomAttention:
    """Whether the room waits for the account (#2929)."""

    attention_pending: bool
    attention_since: datetime.datetime | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attention_pending = self.attention_pending

        attention_since: None | str
        if isinstance(self.attention_since, datetime.datetime):
            attention_since = self.attention_since.isoformat()
        else:
            attention_since = self.attention_since

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attention_pending": attention_pending,
                "attention_since": attention_since,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        attention_pending = d.pop("attention_pending")

        def _parse_attention_since(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                attention_since_type_0 = isoparse(data)

                return attention_since_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        attention_since = _parse_attention_since(d.pop("attention_since"))

        room_attention = cls(
            attention_pending=attention_pending,
            attention_since=attention_since,
        )

        room_attention.additional_properties = d
        return room_attention

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
