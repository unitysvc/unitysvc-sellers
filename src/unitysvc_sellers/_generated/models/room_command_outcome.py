from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.room_command_outcome_status import RoomCommandOutcomeStatus, check_room_command_outcome_status
from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomCommandOutcome")


@_attrs_define
class RoomCommandOutcome:
    """What a ``!`` first line did (#2904). The line and its answer are
    private to the sender for every outcome, including malformed or unknown
    commands. A syntax error may include an AI suggestion to copy and run;
    suggestions are never executed automatically.

    """

    status: RoomCommandOutcomeStatus
    message: str
    name: None | str | Unset = UNSET
    code: None | str | Unset = UNSET
    answer_message_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status: str = self.status

        message = self.message

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        code: None | str | Unset
        if isinstance(self.code, Unset):
            code = UNSET
        else:
            code = self.code

        answer_message_id: None | str | Unset
        if isinstance(self.answer_message_id, Unset):
            answer_message_id = UNSET
        elif isinstance(self.answer_message_id, UUID):
            answer_message_id = str(self.answer_message_id)
        else:
            answer_message_id = self.answer_message_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "message": message,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if code is not UNSET:
            field_dict["code"] = code
        if answer_message_id is not UNSET:
            field_dict["answer_message_id"] = answer_message_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = check_room_command_outcome_status(d.pop("status"))

        message = d.pop("message")

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        code = _parse_code(d.pop("code", UNSET))

        def _parse_answer_message_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                answer_message_id_type_0 = UUID(data)

                return answer_message_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        answer_message_id = _parse_answer_message_id(d.pop("answer_message_id", UNSET))

        room_command_outcome = cls(
            status=status,
            message=message,
            name=name,
            code=code,
            answer_message_id=answer_message_id,
        )

        room_command_outcome.additional_properties = d
        return room_command_outcome

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
