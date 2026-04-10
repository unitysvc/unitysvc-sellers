from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.action_code_type import ActionCodeType
from ..models.action_code_type import check_action_code_type
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.action_code_create_extra_data_type_0 import ActionCodeCreateExtraDataType0





T = TypeVar("T", bound="ActionCodeCreate")



@_attrs_define
class ActionCodeCreate:
    """ Schema for creating a new action code.

    Note: code_type and entity_id have defaults to allow partial creation
    (e.g., when the team wrapper fills in team-specific values).
    The generic create_action_code CRUD requires both to be set.

     """

    max_uses: int | None | Unset = UNSET
    """ Maximum number of uses (None = unlimited) """
    note: None | str | Unset = UNSET
    """ Optional note about this code (e.g. 'For marketing team') """
    code_type: ActionCodeType | None | Unset = UNSET
    """ Type of action code (determines target entity and use action) """
    entity_id: None | Unset | UUID = UNSET
    """ ID of the target entity (e.g., customer_id for team invitations) """
    effective_at: datetime.datetime | None | Unset = UNSET
    """ When the code becomes active (None = immediately) """
    expires_in_days: int | None | Unset = 7
    """ Days until expiry (default 7, max 365) """
    extra_data: ActionCodeCreateExtraDataType0 | None | Unset = UNSET
    """ Type-specific metadata (e.g., discount %, trial days) """
    token_length: int | None | Unset = UNSET
    """ Length of generated token (default 6, min 4, max 16) """





    def to_dict(self) -> dict[str, Any]:
        from ..models.action_code_create_extra_data_type_0 import ActionCodeCreateExtraDataType0
        max_uses: int | None | Unset
        if isinstance(self.max_uses, Unset):
            max_uses = UNSET
        else:
            max_uses = self.max_uses

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        code_type: None | str | Unset
        if isinstance(self.code_type, Unset):
            code_type = UNSET
        elif isinstance(self.code_type, str):
            code_type = self.code_type
        else:
            code_type = self.code_type

        entity_id: None | str | Unset
        if isinstance(self.entity_id, Unset):
            entity_id = UNSET
        elif isinstance(self.entity_id, UUID):
            entity_id = str(self.entity_id)
        else:
            entity_id = self.entity_id

        effective_at: None | str | Unset
        if isinstance(self.effective_at, Unset):
            effective_at = UNSET
        elif isinstance(self.effective_at, datetime.datetime):
            effective_at = self.effective_at.isoformat()
        else:
            effective_at = self.effective_at

        expires_in_days: int | None | Unset
        if isinstance(self.expires_in_days, Unset):
            expires_in_days = UNSET
        else:
            expires_in_days = self.expires_in_days

        extra_data: dict[str, Any] | None | Unset
        if isinstance(self.extra_data, Unset):
            extra_data = UNSET
        elif isinstance(self.extra_data, ActionCodeCreateExtraDataType0):
            extra_data = self.extra_data.to_dict()
        else:
            extra_data = self.extra_data

        token_length: int | None | Unset
        if isinstance(self.token_length, Unset):
            token_length = UNSET
        else:
            token_length = self.token_length


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if max_uses is not UNSET:
            field_dict["max_uses"] = max_uses
        if note is not UNSET:
            field_dict["note"] = note
        if code_type is not UNSET:
            field_dict["code_type"] = code_type
        if entity_id is not UNSET:
            field_dict["entity_id"] = entity_id
        if effective_at is not UNSET:
            field_dict["effective_at"] = effective_at
        if expires_in_days is not UNSET:
            field_dict["expires_in_days"] = expires_in_days
        if extra_data is not UNSET:
            field_dict["extra_data"] = extra_data
        if token_length is not UNSET:
            field_dict["token_length"] = token_length

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.action_code_create_extra_data_type_0 import ActionCodeCreateExtraDataType0
        d = dict(src_dict)
        def _parse_max_uses(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_uses = _parse_max_uses(d.pop("max_uses", UNSET))


        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))


        def _parse_code_type(data: object) -> ActionCodeType | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                code_type_type_0 = check_action_code_type(data)



                return code_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActionCodeType | None | Unset, data)

        code_type = _parse_code_type(d.pop("code_type", UNSET))


        def _parse_entity_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                entity_id_type_0 = UUID(data)



                return entity_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        entity_id = _parse_entity_id(d.pop("entity_id", UNSET))


        def _parse_effective_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                effective_at_type_0 = isoparse(data)



                return effective_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        effective_at = _parse_effective_at(d.pop("effective_at", UNSET))


        def _parse_expires_in_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expires_in_days = _parse_expires_in_days(d.pop("expires_in_days", UNSET))


        def _parse_extra_data(data: object) -> ActionCodeCreateExtraDataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_data_type_0 = ActionCodeCreateExtraDataType0.from_dict(data)



                return extra_data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActionCodeCreateExtraDataType0 | None | Unset, data)

        extra_data = _parse_extra_data(d.pop("extra_data", UNSET))


        def _parse_token_length(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        token_length = _parse_token_length(d.pop("token_length", UNSET))


        action_code_create = cls(
            max_uses=max_uses,
            note=note,
            code_type=code_type,
            entity_id=entity_id,
            effective_at=effective_at,
            expires_in_days=expires_in_days,
            extra_data=extra_data,
            token_length=token_length,
        )

        return action_code_create

