from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.recurrent_request_status_enum import check_recurrent_request_status_enum
from ..models.recurrent_request_status_enum import RecurrentRequestStatusEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.recurrent_request_public_body_template_type_0 import RecurrentRequestPublicBodyTemplateType0
  from ..models.recurrent_request_public_schedule_type_0 import RecurrentRequestPublicScheduleType0
  from ..models.recurrent_request_public_state_type_0 import RecurrentRequestPublicStateType0





T = TypeVar("T", bound="RecurrentRequestPublic")



@_attrs_define
class RecurrentRequestPublic:
    """ Public RecurrentRequest for API responses.

     """

    id: UUID
    status: RecurrentRequestStatusEnum
    """ Status of a recurrent request.

    Lifecycle: draft → active → paused → cancelled """
    customer_id: UUID
    request_path: str
    http_method: str
    created_at: str
    service_id: None | Unset | UUID = UNSET
    enrollment_id: None | Unset | UUID = UNSET
    body_template: None | RecurrentRequestPublicBodyTemplateType0 | Unset = UNSET
    schedule: None | RecurrentRequestPublicScheduleType0 | Unset = UNSET
    state: None | RecurrentRequestPublicStateType0 | Unset = UNSET
    name: None | str | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.recurrent_request_public_body_template_type_0 import RecurrentRequestPublicBodyTemplateType0
        from ..models.recurrent_request_public_schedule_type_0 import RecurrentRequestPublicScheduleType0
        from ..models.recurrent_request_public_state_type_0 import RecurrentRequestPublicStateType0
        id = str(self.id)

        status: str = self.status

        customer_id = str(self.customer_id)

        request_path = self.request_path

        http_method = self.http_method

        created_at = self.created_at

        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

        enrollment_id: None | str | Unset
        if isinstance(self.enrollment_id, Unset):
            enrollment_id = UNSET
        elif isinstance(self.enrollment_id, UUID):
            enrollment_id = str(self.enrollment_id)
        else:
            enrollment_id = self.enrollment_id

        body_template: dict[str, Any] | None | Unset
        if isinstance(self.body_template, Unset):
            body_template = UNSET
        elif isinstance(self.body_template, RecurrentRequestPublicBodyTemplateType0):
            body_template = self.body_template.to_dict()
        else:
            body_template = self.body_template

        schedule: dict[str, Any] | None | Unset
        if isinstance(self.schedule, Unset):
            schedule = UNSET
        elif isinstance(self.schedule, RecurrentRequestPublicScheduleType0):
            schedule = self.schedule.to_dict()
        else:
            schedule = self.schedule

        state: dict[str, Any] | None | Unset
        if isinstance(self.state, Unset):
            state = UNSET
        elif isinstance(self.state, RecurrentRequestPublicStateType0):
            state = self.state.to_dict()
        else:
            state = self.state

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "status": status,
            "customer_id": customer_id,
            "request_path": request_path,
            "http_method": http_method,
            "created_at": created_at,
        })
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if enrollment_id is not UNSET:
            field_dict["enrollment_id"] = enrollment_id
        if body_template is not UNSET:
            field_dict["body_template"] = body_template
        if schedule is not UNSET:
            field_dict["schedule"] = schedule
        if state is not UNSET:
            field_dict["state"] = state
        if name is not UNSET:
            field_dict["name"] = name
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recurrent_request_public_body_template_type_0 import RecurrentRequestPublicBodyTemplateType0
        from ..models.recurrent_request_public_schedule_type_0 import RecurrentRequestPublicScheduleType0
        from ..models.recurrent_request_public_state_type_0 import RecurrentRequestPublicStateType0
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        status = check_recurrent_request_status_enum(d.pop("status"))




        customer_id = UUID(d.pop("customer_id"))




        request_path = d.pop("request_path")

        http_method = d.pop("http_method")

        created_at = d.pop("created_at")

        def _parse_service_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_id_type_0 = UUID(data)



                return service_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        service_id = _parse_service_id(d.pop("service_id", UNSET))


        def _parse_enrollment_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                enrollment_id_type_0 = UUID(data)



                return enrollment_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        enrollment_id = _parse_enrollment_id(d.pop("enrollment_id", UNSET))


        def _parse_body_template(data: object) -> None | RecurrentRequestPublicBodyTemplateType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                body_template_type_0 = RecurrentRequestPublicBodyTemplateType0.from_dict(data)



                return body_template_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RecurrentRequestPublicBodyTemplateType0 | Unset, data)

        body_template = _parse_body_template(d.pop("body_template", UNSET))


        def _parse_schedule(data: object) -> None | RecurrentRequestPublicScheduleType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                schedule_type_0 = RecurrentRequestPublicScheduleType0.from_dict(data)



                return schedule_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RecurrentRequestPublicScheduleType0 | Unset, data)

        schedule = _parse_schedule(d.pop("schedule", UNSET))


        def _parse_state(data: object) -> None | RecurrentRequestPublicStateType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                state_type_0 = RecurrentRequestPublicStateType0.from_dict(data)



                return state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RecurrentRequestPublicStateType0 | Unset, data)

        state = _parse_state(d.pop("state", UNSET))


        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))


        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))


        recurrent_request_public = cls(
            id=id,
            status=status,
            customer_id=customer_id,
            request_path=request_path,
            http_method=http_method,
            created_at=created_at,
            service_id=service_id,
            enrollment_id=enrollment_id,
            body_template=body_template,
            schedule=schedule,
            state=state,
            name=name,
            updated_at=updated_at,
        )


        recurrent_request_public.additional_properties = d
        return recurrent_request_public

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
