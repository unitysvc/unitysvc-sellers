from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.recurrent_request_create_body_template_type_0 import RecurrentRequestCreateBodyTemplateType0
  from ..models.recurrent_request_create_request_headers_type_0 import RecurrentRequestCreateRequestHeadersType0





T = TypeVar("T", bound="RecurrentRequestCreate")



@_attrs_define
class RecurrentRequestCreate:
    """ Schema for creating a RecurrentRequest (draft).

     """

    request_path: str
    """ Gateway path (e.g., /u/group/service) """
    service_id: None | Unset | UUID = UNSET
    enrollment_id: None | Unset | UUID = UNSET
    http_method: str | Unset = 'POST'
    body_template: None | RecurrentRequestCreateBodyTemplateType0 | Unset = UNSET
    request_headers: None | RecurrentRequestCreateRequestHeadersType0 | Unset = UNSET
    name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.recurrent_request_create_body_template_type_0 import RecurrentRequestCreateBodyTemplateType0
        from ..models.recurrent_request_create_request_headers_type_0 import RecurrentRequestCreateRequestHeadersType0
        request_path = self.request_path

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

        http_method = self.http_method

        body_template: dict[str, Any] | None | Unset
        if isinstance(self.body_template, Unset):
            body_template = UNSET
        elif isinstance(self.body_template, RecurrentRequestCreateBodyTemplateType0):
            body_template = self.body_template.to_dict()
        else:
            body_template = self.body_template

        request_headers: dict[str, Any] | None | Unset
        if isinstance(self.request_headers, Unset):
            request_headers = UNSET
        elif isinstance(self.request_headers, RecurrentRequestCreateRequestHeadersType0):
            request_headers = self.request_headers.to_dict()
        else:
            request_headers = self.request_headers

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "request_path": request_path,
        })
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if enrollment_id is not UNSET:
            field_dict["enrollment_id"] = enrollment_id
        if http_method is not UNSET:
            field_dict["http_method"] = http_method
        if body_template is not UNSET:
            field_dict["body_template"] = body_template
        if request_headers is not UNSET:
            field_dict["request_headers"] = request_headers
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recurrent_request_create_body_template_type_0 import RecurrentRequestCreateBodyTemplateType0
        from ..models.recurrent_request_create_request_headers_type_0 import RecurrentRequestCreateRequestHeadersType0
        d = dict(src_dict)
        request_path = d.pop("request_path")

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


        http_method = d.pop("http_method", UNSET)

        def _parse_body_template(data: object) -> None | RecurrentRequestCreateBodyTemplateType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                body_template_type_0 = RecurrentRequestCreateBodyTemplateType0.from_dict(data)



                return body_template_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RecurrentRequestCreateBodyTemplateType0 | Unset, data)

        body_template = _parse_body_template(d.pop("body_template", UNSET))


        def _parse_request_headers(data: object) -> None | RecurrentRequestCreateRequestHeadersType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                request_headers_type_0 = RecurrentRequestCreateRequestHeadersType0.from_dict(data)



                return request_headers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RecurrentRequestCreateRequestHeadersType0 | Unset, data)

        request_headers = _parse_request_headers(d.pop("request_headers", UNSET))


        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))


        recurrent_request_create = cls(
            request_path=request_path,
            service_id=service_id,
            enrollment_id=enrollment_id,
            http_method=http_method,
            body_template=body_template,
            request_headers=request_headers,
            name=name,
        )


        recurrent_request_create.additional_properties = d
        return recurrent_request_create

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
