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

if TYPE_CHECKING:
  from ..models.recurrent_request_update_body_template_type_0 import RecurrentRequestUpdateBodyTemplateType0
  from ..models.recurrent_request_update_request_headers_type_0 import RecurrentRequestUpdateRequestHeadersType0
  from ..models.recurrent_request_update_schedule_type_0 import RecurrentRequestUpdateScheduleType0





T = TypeVar("T", bound="RecurrentRequestUpdate")



@_attrs_define
class RecurrentRequestUpdate:
    """ Schema for updating a RecurrentRequest.

     """

    request_path: None | str | Unset = UNSET
    body_template: None | RecurrentRequestUpdateBodyTemplateType0 | Unset = UNSET
    request_headers: None | RecurrentRequestUpdateRequestHeadersType0 | Unset = UNSET
    schedule: None | RecurrentRequestUpdateScheduleType0 | Unset = UNSET
    name: None | str | Unset = UNSET
    status: None | RecurrentRequestStatusEnum | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.recurrent_request_update_body_template_type_0 import RecurrentRequestUpdateBodyTemplateType0
        from ..models.recurrent_request_update_request_headers_type_0 import RecurrentRequestUpdateRequestHeadersType0
        from ..models.recurrent_request_update_schedule_type_0 import RecurrentRequestUpdateScheduleType0
        request_path: None | str | Unset
        if isinstance(self.request_path, Unset):
            request_path = UNSET
        else:
            request_path = self.request_path

        body_template: dict[str, Any] | None | Unset
        if isinstance(self.body_template, Unset):
            body_template = UNSET
        elif isinstance(self.body_template, RecurrentRequestUpdateBodyTemplateType0):
            body_template = self.body_template.to_dict()
        else:
            body_template = self.body_template

        request_headers: dict[str, Any] | None | Unset
        if isinstance(self.request_headers, Unset):
            request_headers = UNSET
        elif isinstance(self.request_headers, RecurrentRequestUpdateRequestHeadersType0):
            request_headers = self.request_headers.to_dict()
        else:
            request_headers = self.request_headers

        schedule: dict[str, Any] | None | Unset
        if isinstance(self.schedule, Unset):
            schedule = UNSET
        elif isinstance(self.schedule, RecurrentRequestUpdateScheduleType0):
            schedule = self.schedule.to_dict()
        else:
            schedule = self.schedule

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, str):
            status = self.status
        else:
            status = self.status


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if request_path is not UNSET:
            field_dict["request_path"] = request_path
        if body_template is not UNSET:
            field_dict["body_template"] = body_template
        if request_headers is not UNSET:
            field_dict["request_headers"] = request_headers
        if schedule is not UNSET:
            field_dict["schedule"] = schedule
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recurrent_request_update_body_template_type_0 import RecurrentRequestUpdateBodyTemplateType0
        from ..models.recurrent_request_update_request_headers_type_0 import RecurrentRequestUpdateRequestHeadersType0
        from ..models.recurrent_request_update_schedule_type_0 import RecurrentRequestUpdateScheduleType0
        d = dict(src_dict)
        def _parse_request_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        request_path = _parse_request_path(d.pop("request_path", UNSET))


        def _parse_body_template(data: object) -> None | RecurrentRequestUpdateBodyTemplateType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                body_template_type_0 = RecurrentRequestUpdateBodyTemplateType0.from_dict(data)



                return body_template_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RecurrentRequestUpdateBodyTemplateType0 | Unset, data)

        body_template = _parse_body_template(d.pop("body_template", UNSET))


        def _parse_request_headers(data: object) -> None | RecurrentRequestUpdateRequestHeadersType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                request_headers_type_0 = RecurrentRequestUpdateRequestHeadersType0.from_dict(data)



                return request_headers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RecurrentRequestUpdateRequestHeadersType0 | Unset, data)

        request_headers = _parse_request_headers(d.pop("request_headers", UNSET))


        def _parse_schedule(data: object) -> None | RecurrentRequestUpdateScheduleType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                schedule_type_0 = RecurrentRequestUpdateScheduleType0.from_dict(data)



                return schedule_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RecurrentRequestUpdateScheduleType0 | Unset, data)

        schedule = _parse_schedule(d.pop("schedule", UNSET))


        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))


        def _parse_status(data: object) -> None | RecurrentRequestStatusEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = check_recurrent_request_status_enum(data)



                return status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RecurrentRequestStatusEnum | Unset, data)

        status = _parse_status(d.pop("status", UNSET))


        recurrent_request_update = cls(
            request_path=request_path,
            body_template=body_template,
            request_headers=request_headers,
            schedule=schedule,
            name=name,
            status=status,
        )


        recurrent_request_update.additional_properties = d
        return recurrent_request_update

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
