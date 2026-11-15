from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RoomCommandInfo")


@_attrs_define
class RoomCommandInfo:
    """One registry command (#2904 §7), with its pattern as a string so a
    client validates a line with the server's own regular expression.

    """

    name: str
    syntax: str
    example: str
    summary: str
    sender: str
    effect: str
    pattern: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        syntax = self.syntax

        example = self.example

        summary = self.summary

        sender = self.sender

        effect = self.effect

        pattern = self.pattern

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
            }
        )

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

        room_command_info = cls(
            name=name,
            syntax=syntax,
            example=example,
            summary=summary,
            sender=sender,
            effect=effect,
            pattern=pattern,
        )

        room_command_info.additional_properties = d
        return room_command_info

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
