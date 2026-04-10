from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.action_code_status import ActionCodeStatus
from ..models.action_code_status import check_action_code_status
from ..models.action_code_type import ActionCodeType
from ..models.action_code_type import check_action_code_type
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.action_code_public_extra_data_type_0 import ActionCodePublicExtraDataType0





T = TypeVar("T", bound="ActionCodePublic")



@_attrs_define
class ActionCodePublic:
    """ Public action code information for API responses.

     """

    id: UUID
    code_type: ActionCodeType
    """ Type of action code - determines target entity and use action. """
    entity_id: UUID
    token: str
    status: ActionCodeStatus
    """ Status of an action code. """
    use_count: int
    created_by_id: UUID
    effective_at: datetime.datetime
    expires_at: datetime.datetime
    created_at: datetime.datetime
    max_uses: int | None | Unset = UNSET
    """ Maximum number of uses (None = unlimited) """
    note: None | str | Unset = UNSET
    """ Optional note about this code (e.g. 'For marketing team') """
    extra_data: ActionCodePublicExtraDataType0 | None | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.action_code_public_extra_data_type_0 import ActionCodePublicExtraDataType0
        id = str(self.id)

        code_type: str = self.code_type

        entity_id = str(self.entity_id)

        token = self.token

        status: str = self.status

        use_count = self.use_count

        created_by_id = str(self.created_by_id)

        effective_at = self.effective_at.isoformat()

        expires_at = self.expires_at.isoformat()

        created_at = self.created_at.isoformat()

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

        extra_data: dict[str, Any] | None | Unset
        if isinstance(self.extra_data, Unset):
            extra_data = UNSET
        elif isinstance(self.extra_data, ActionCodePublicExtraDataType0):
            extra_data = self.extra_data.to_dict()
        else:
            extra_data = self.extra_data


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "id": id,
            "code_type": code_type,
            "entity_id": entity_id,
            "token": token,
            "status": status,
            "use_count": use_count,
            "created_by_id": created_by_id,
            "effective_at": effective_at,
            "expires_at": expires_at,
            "created_at": created_at,
        })
        if max_uses is not UNSET:
            field_dict["max_uses"] = max_uses
        if note is not UNSET:
            field_dict["note"] = note
        if extra_data is not UNSET:
            field_dict["extra_data"] = extra_data

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.action_code_public_extra_data_type_0 import ActionCodePublicExtraDataType0
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        code_type = check_action_code_type(d.pop("code_type"))




        entity_id = UUID(d.pop("entity_id"))




        token = d.pop("token")

        status = check_action_code_status(d.pop("status"))




        use_count = d.pop("use_count")

        created_by_id = UUID(d.pop("created_by_id"))




        effective_at = isoparse(d.pop("effective_at"))




        expires_at = isoparse(d.pop("expires_at"))




        created_at = isoparse(d.pop("created_at"))




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


        def _parse_extra_data(data: object) -> ActionCodePublicExtraDataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_data_type_0 = ActionCodePublicExtraDataType0.from_dict(data)



                return extra_data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActionCodePublicExtraDataType0 | None | Unset, data)

        extra_data = _parse_extra_data(d.pop("extra_data", UNSET))


        action_code_public = cls(
            id=id,
            code_type=code_type,
            entity_id=entity_id,
            token=token,
            status=status,
            use_count=use_count,
            created_by_id=created_by_id,
            effective_at=effective_at,
            expires_at=expires_at,
            created_at=created_at,
            max_uses=max_uses,
            note=note,
            extra_data=extra_data,
        )

        return action_code_public

