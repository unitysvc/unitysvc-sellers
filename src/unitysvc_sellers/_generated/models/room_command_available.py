from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomCommandAvailable")


@_attrs_define
class RoomCommandAvailable:
    """Whether this caller may send the command in one room right now, and
    why not: what the composer offers, greys out, and ``!help`` prints.

    """

    name: str
    syntax: str
    example: str
    summary: str
    sender: str
    effect: str
    pattern: str
    available: bool
    code: None | str | Unset = UNSET
    reason: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        syntax = self.syntax

        example = self.example

        summary = self.summary

        sender = self.sender

        effect = self.effect

        pattern = self.pattern

        available = self.available

        code: None | str | Unset
        if isinstance(self.code, Unset):
            code = UNSET
        else:
            code = self.code

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "syntax": syntax,
                "example": example,
                "summary": summary,
                "sender": sender,
                "effect": effect,
                "pattern": pattern,
                "available": available,
            }
        )
        if code is not UNSET:
            field_dict["code"] = code
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        syntax = d.pop("syntax")

        example = d.pop("example")

        summary = d.pop("summary")

        sender = d.pop("sender")

        effect = d.pop("effect")

        pattern = d.pop("pattern")

        available = d.pop("available")

        def _parse_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        code = _parse_code(d.pop("code", UNSET))

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        room_command_available = cls(
            name=name,
            syntax=syntax,
            example=example,
            summary=summary,
            sender=sender,
            effect=effect,
            pattern=pattern,
            available=available,
            code=code,
            reason=reason,
        )

        room_command_available.additional_properties = d
        return room_command_available

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
