from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.service_type_enum import ServiceTypeEnum, check_service_type_enum
from ..models.template_status_enum import TemplateStatusEnum, check_template_status_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_template_create_parameter_ui_schema_type_0 import ServiceTemplateCreateParameterUiSchemaType0
    from ..models.service_template_create_service_template_create_constants import (
        ServiceTemplateCreateServiceTemplateCreateConstants,
    )
    from ..models.service_template_create_service_template_create_parameter_schema import (
        ServiceTemplateCreateServiceTemplateCreateParameterSchema,
    )


T = TypeVar("T", bound="ServiceTemplateCreate")


@_attrs_define
class ServiceTemplateCreate:
    """Schema for creating/updating a ServiceTemplate (admin upload).

    ``status`` defaults to ``draft``; the renderer bodies and schemas are
    required so the stored row is self-contained.

    ``id`` is honored on CREATE only (the ``template_id.json`` sidecar
    replayed across environments, so a template keeps ONE id on staging and
    production — the same convention service ids follow). The upsert key
    stays ``(name, version)``: on update the id is ignored.

    """

    name: str
    """ URL-friendly slug identifying the template family (e.g. 'openai-compatible-llm'). Sellers bind to the active
    version of a name; admin-data directory names and the CLI key off it. Unique per (name, version). """
    version: str
    """ Template version label (e.g. 'v1'). The .j2 bodies and parameter_schema are frozen per version; a change is
    a new version. UNIQUE(name, version). """
    display_name: str
    """ Human-readable template name shown in the seller picker. """
    service_type: ServiceTypeEnum
    """ Broad service category — defines the access pattern and protocol.

    AI modalities (vision, tools, rerank, etc.) are tracked via the
    `capabilities` list on ServiceOffering, not service_type. """
    offering_template: str
    listing_template: str
    provider_template: str
    description: None | str | Unset = UNSET
    """ What kind of service this template produces. """
    id: None | Unset | UUID = UNSET
    status: TemplateStatusEnum | Unset = UNSET
    """ Lifecycle status of an admin-owned ServiceTemplate.

    Invariant: at most one ``active`` version per template ``name`` — the one
    sellers bind new forms to. Publishing a new ``active`` version
    auto-deprecates the prior active one. Deprecated templates can no longer
    generate net-new services, but services already built from them can still
    be revised against their pinned version. """
    parameter_schema: ServiceTemplateCreateServiceTemplateCreateParameterSchema | Unset = UNSET
    parameter_ui_schema: None | ServiceTemplateCreateParameterUiSchemaType0 | Unset = UNSET
    constants: ServiceTemplateCreateServiceTemplateCreateConstants | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_template_create_parameter_ui_schema_type_0 import (
            ServiceTemplateCreateParameterUiSchemaType0,
        )
        from ..models.service_template_create_service_template_create_constants import (
            ServiceTemplateCreateServiceTemplateCreateConstants,
        )
        from ..models.service_template_create_service_template_create_parameter_schema import (
            ServiceTemplateCreateServiceTemplateCreateParameterSchema,
        )

        name = self.name

        version = self.version

        display_name = self.display_name

        service_type: str = self.service_type

        offering_template = self.offering_template

        listing_template = self.listing_template

        provider_template = self.provider_template

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        elif isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        parameter_schema: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameter_schema, Unset):
            parameter_schema = self.parameter_schema.to_dict()

        parameter_ui_schema: dict[str, Any] | None | Unset
        if isinstance(self.parameter_ui_schema, Unset):
            parameter_ui_schema = UNSET
        elif isinstance(self.parameter_ui_schema, ServiceTemplateCreateParameterUiSchemaType0):
            parameter_ui_schema = self.parameter_ui_schema.to_dict()
        else:
            parameter_ui_schema = self.parameter_ui_schema

        constants: dict[str, Any] | Unset = UNSET
        if not isinstance(self.constants, Unset):
            constants = self.constants.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "version": version,
                "display_name": display_name,
                "service_type": service_type,
                "offering_template": offering_template,
                "listing_template": listing_template,
                "provider_template": provider_template,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if id is not UNSET:
            field_dict["id"] = id
        if status is not UNSET:
            field_dict["status"] = status
        if parameter_schema is not UNSET:
            field_dict["parameter_schema"] = parameter_schema
        if parameter_ui_schema is not UNSET:
            field_dict["parameter_ui_schema"] = parameter_ui_schema
        if constants is not UNSET:
            field_dict["constants"] = constants

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_template_create_parameter_ui_schema_type_0 import (
            ServiceTemplateCreateParameterUiSchemaType0,
        )
        from ..models.service_template_create_service_template_create_constants import (
            ServiceTemplateCreateServiceTemplateCreateConstants,
        )
        from ..models.service_template_create_service_template_create_parameter_schema import (
            ServiceTemplateCreateServiceTemplateCreateParameterSchema,
        )

        d = dict(src_dict)
        name = d.pop("name")

        version = d.pop("version")

        display_name = d.pop("display_name")

        service_type = check_service_type_enum(d.pop("service_type"))

        offering_template = d.pop("offering_template")

        listing_template = d.pop("listing_template")

        provider_template = d.pop("provider_template")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                id_type_0 = UUID(data)

                return id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        id = _parse_id(d.pop("id", UNSET))

        _status = d.pop("status", UNSET)
        status: TemplateStatusEnum | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_template_status_enum(_status)

        _parameter_schema = d.pop("parameter_schema", UNSET)
        parameter_schema: ServiceTemplateCreateServiceTemplateCreateParameterSchema | Unset
        if isinstance(_parameter_schema, Unset):
            parameter_schema = UNSET
        else:
            parameter_schema = ServiceTemplateCreateServiceTemplateCreateParameterSchema.from_dict(_parameter_schema)

        def _parse_parameter_ui_schema(data: object) -> None | ServiceTemplateCreateParameterUiSchemaType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameter_ui_schema_type_0 = ServiceTemplateCreateParameterUiSchemaType0.from_dict(data)

                return parameter_ui_schema_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceTemplateCreateParameterUiSchemaType0 | Unset, data)

        parameter_ui_schema = _parse_parameter_ui_schema(d.pop("parameter_ui_schema", UNSET))

        _constants = d.pop("constants", UNSET)
        constants: ServiceTemplateCreateServiceTemplateCreateConstants | Unset
        if isinstance(_constants, Unset):
            constants = UNSET
        else:
            constants = ServiceTemplateCreateServiceTemplateCreateConstants.from_dict(_constants)

        service_template_create = cls(
            name=name,
            version=version,
            display_name=display_name,
            service_type=service_type,
            offering_template=offering_template,
            listing_template=listing_template,
            provider_template=provider_template,
            description=description,
            id=id,
            status=status,
            parameter_schema=parameter_schema,
            parameter_ui_schema=parameter_ui_schema,
            constants=constants,
        )

        service_template_create.additional_properties = d
        return service_template_create

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
