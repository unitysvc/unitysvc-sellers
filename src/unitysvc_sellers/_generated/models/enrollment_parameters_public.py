from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.enrollment_parameters_public_current_parameters_type_0 import EnrollmentParametersPublicCurrentParametersType0
  from ..models.enrollment_parameters_public_parameters_schema_type_0 import EnrollmentParametersPublicParametersSchemaType0
  from ..models.enrollment_parameters_public_parameters_ui_schema_type_0 import EnrollmentParametersPublicParametersUiSchemaType0
  from ..models.enrollment_parameters_public_service_options_type_0 import EnrollmentParametersPublicServiceOptionsType0





T = TypeVar("T", bound="EnrollmentParametersPublic")



@_attrs_define
class EnrollmentParametersPublic:
    """ Response model for enrollment parameters configuration.

     """

    parameters_schema: EnrollmentParametersPublicParametersSchemaType0 | None | Unset = UNSET
    parameters_ui_schema: EnrollmentParametersPublicParametersUiSchemaType0 | None | Unset = UNSET
    current_parameters: EnrollmentParametersPublicCurrentParametersType0 | None | Unset = UNSET
    service_options: EnrollmentParametersPublicServiceOptionsType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.enrollment_parameters_public_current_parameters_type_0 import EnrollmentParametersPublicCurrentParametersType0
        from ..models.enrollment_parameters_public_parameters_schema_type_0 import EnrollmentParametersPublicParametersSchemaType0
        from ..models.enrollment_parameters_public_parameters_ui_schema_type_0 import EnrollmentParametersPublicParametersUiSchemaType0
        from ..models.enrollment_parameters_public_service_options_type_0 import EnrollmentParametersPublicServiceOptionsType0
        parameters_schema: dict[str, Any] | None | Unset
        if isinstance(self.parameters_schema, Unset):
            parameters_schema = UNSET
        elif isinstance(self.parameters_schema, EnrollmentParametersPublicParametersSchemaType0):
            parameters_schema = self.parameters_schema.to_dict()
        else:
            parameters_schema = self.parameters_schema

        parameters_ui_schema: dict[str, Any] | None | Unset
        if isinstance(self.parameters_ui_schema, Unset):
            parameters_ui_schema = UNSET
        elif isinstance(self.parameters_ui_schema, EnrollmentParametersPublicParametersUiSchemaType0):
            parameters_ui_schema = self.parameters_ui_schema.to_dict()
        else:
            parameters_ui_schema = self.parameters_ui_schema

        current_parameters: dict[str, Any] | None | Unset
        if isinstance(self.current_parameters, Unset):
            current_parameters = UNSET
        elif isinstance(self.current_parameters, EnrollmentParametersPublicCurrentParametersType0):
            current_parameters = self.current_parameters.to_dict()
        else:
            current_parameters = self.current_parameters

        service_options: dict[str, Any] | None | Unset
        if isinstance(self.service_options, Unset):
            service_options = UNSET
        elif isinstance(self.service_options, EnrollmentParametersPublicServiceOptionsType0):
            service_options = self.service_options.to_dict()
        else:
            service_options = self.service_options


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if parameters_schema is not UNSET:
            field_dict["parameters_schema"] = parameters_schema
        if parameters_ui_schema is not UNSET:
            field_dict["parameters_ui_schema"] = parameters_ui_schema
        if current_parameters is not UNSET:
            field_dict["current_parameters"] = current_parameters
        if service_options is not UNSET:
            field_dict["service_options"] = service_options

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.enrollment_parameters_public_current_parameters_type_0 import EnrollmentParametersPublicCurrentParametersType0
        from ..models.enrollment_parameters_public_parameters_schema_type_0 import EnrollmentParametersPublicParametersSchemaType0
        from ..models.enrollment_parameters_public_parameters_ui_schema_type_0 import EnrollmentParametersPublicParametersUiSchemaType0
        from ..models.enrollment_parameters_public_service_options_type_0 import EnrollmentParametersPublicServiceOptionsType0
        d = dict(src_dict)
        def _parse_parameters_schema(data: object) -> EnrollmentParametersPublicParametersSchemaType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_schema_type_0 = EnrollmentParametersPublicParametersSchemaType0.from_dict(data)



                return parameters_schema_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EnrollmentParametersPublicParametersSchemaType0 | None | Unset, data)

        parameters_schema = _parse_parameters_schema(d.pop("parameters_schema", UNSET))


        def _parse_parameters_ui_schema(data: object) -> EnrollmentParametersPublicParametersUiSchemaType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_ui_schema_type_0 = EnrollmentParametersPublicParametersUiSchemaType0.from_dict(data)



                return parameters_ui_schema_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EnrollmentParametersPublicParametersUiSchemaType0 | None | Unset, data)

        parameters_ui_schema = _parse_parameters_ui_schema(d.pop("parameters_ui_schema", UNSET))


        def _parse_current_parameters(data: object) -> EnrollmentParametersPublicCurrentParametersType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                current_parameters_type_0 = EnrollmentParametersPublicCurrentParametersType0.from_dict(data)



                return current_parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EnrollmentParametersPublicCurrentParametersType0 | None | Unset, data)

        current_parameters = _parse_current_parameters(d.pop("current_parameters", UNSET))


        def _parse_service_options(data: object) -> EnrollmentParametersPublicServiceOptionsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                service_options_type_0 = EnrollmentParametersPublicServiceOptionsType0.from_dict(data)



                return service_options_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EnrollmentParametersPublicServiceOptionsType0 | None | Unset, data)

        service_options = _parse_service_options(d.pop("service_options", UNSET))


        enrollment_parameters_public = cls(
            parameters_schema=parameters_schema,
            parameters_ui_schema=parameters_ui_schema,
            current_parameters=current_parameters,
            service_options=service_options,
        )


        enrollment_parameters_public.additional_properties = d
        return enrollment_parameters_public

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
