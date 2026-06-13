from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.service_type_enum import ServiceTypeEnum, check_service_type_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_template_summary_parameter_schema import ServiceTemplateSummaryParameterSchema
    from ..models.service_template_summary_parameter_ui_schema_type_0 import (
        ServiceTemplateSummaryParameterUiSchemaType0,
    )


T = TypeVar("T", bound="ServiceTemplateSummary")


@_attrs_define
class ServiceTemplateSummary:
    """Seller-facing read model — the bounded input surface only.

    Excludes the Jinja2 bodies and platform ``constants`` (the seller never
    sees the rendered offering/listing schema or the platform-fixed context).

    """

    id: UUID
    name: str
    version: str
    display_name: str
    service_type: ServiceTypeEnum
    """ Broad service category — defines the access pattern and protocol.

    AI modalities (vision, tools, rerank, etc.) are tracked via the
    `capabilities` list on ServiceOffering, not service_type. """
    parameter_schema: ServiceTemplateSummaryParameterSchema
    description: None | str | Unset = UNSET
    pool_name: None | str | Unset = UNSET
    parameter_ui_schema: None | ServiceTemplateSummaryParameterUiSchemaType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_template_summary_parameter_schema import ServiceTemplateSummaryParameterSchema
        from ..models.service_template_summary_parameter_ui_schema_type_0 import (
            ServiceTemplateSummaryParameterUiSchemaType0,
        )

        id = str(self.id)

        name = self.name

        version = self.version

        display_name = self.display_name

        service_type: str = self.service_type

        parameter_schema = self.parameter_schema.to_dict()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        pool_name: None | str | Unset
        if isinstance(self.pool_name, Unset):
            pool_name = UNSET
        else:
            pool_name = self.pool_name

        parameter_ui_schema: dict[str, Any] | None | Unset
        if isinstance(self.parameter_ui_schema, Unset):
            parameter_ui_schema = UNSET
        elif isinstance(self.parameter_ui_schema, ServiceTemplateSummaryParameterUiSchemaType0):
            parameter_ui_schema = self.parameter_ui_schema.to_dict()
        else:
            parameter_ui_schema = self.parameter_ui_schema

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "version": version,
                "display_name": display_name,
                "service_type": service_type,
                "parameter_schema": parameter_schema,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if pool_name is not UNSET:
            field_dict["pool_name"] = pool_name
        if parameter_ui_schema is not UNSET:
            field_dict["parameter_ui_schema"] = parameter_ui_schema

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_template_summary_parameter_schema import ServiceTemplateSummaryParameterSchema
        from ..models.service_template_summary_parameter_ui_schema_type_0 import (
            ServiceTemplateSummaryParameterUiSchemaType0,
        )

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        version = d.pop("version")

        display_name = d.pop("display_name")

        service_type = check_service_type_enum(d.pop("service_type"))

        parameter_schema = ServiceTemplateSummaryParameterSchema.from_dict(d.pop("parameter_schema"))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_pool_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pool_name = _parse_pool_name(d.pop("pool_name", UNSET))

        def _parse_parameter_ui_schema(data: object) -> None | ServiceTemplateSummaryParameterUiSchemaType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameter_ui_schema_type_0 = ServiceTemplateSummaryParameterUiSchemaType0.from_dict(data)

                return parameter_ui_schema_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceTemplateSummaryParameterUiSchemaType0 | Unset, data)

        parameter_ui_schema = _parse_parameter_ui_schema(d.pop("parameter_ui_schema", UNSET))

        service_template_summary = cls(
            id=id,
            name=name,
            version=version,
            display_name=display_name,
            service_type=service_type,
            parameter_schema=parameter_schema,
            description=description,
            pool_name=pool_name,
            parameter_ui_schema=parameter_ui_schema,
        )

        service_template_summary.additional_properties = d
        return service_template_summary

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
