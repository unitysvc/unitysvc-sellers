from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.template_instance_public_parameters import TemplateInstancePublicParameters


T = TypeVar("T", bound="TemplateInstancePublic")


@_attrs_define
class TemplateInstancePublic:
    """Seller-facing read model with derived service state."""

    id: UUID
    name: str
    template_id: UUID
    parameters: TemplateInstancePublicParameters
    created_at: datetime.datetime
    template_name: None | str | Unset = UNSET
    template_version: None | str | Unset = UNSET
    template_status: None | str | Unset = UNSET
    service_id: None | Unset | UUID = UNSET
    service_status: None | str | Unset = UNSET
    pending_revision_id: None | Unset | UUID = UNSET
    last_submitted_at: datetime.datetime | None | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.template_instance_public_parameters import TemplateInstancePublicParameters

        id = str(self.id)

        name = self.name

        template_id = str(self.template_id)

        parameters = self.parameters.to_dict()

        created_at = self.created_at.isoformat()

        template_name: None | str | Unset
        if isinstance(self.template_name, Unset):
            template_name = UNSET
        else:
            template_name = self.template_name

        template_version: None | str | Unset
        if isinstance(self.template_version, Unset):
            template_version = UNSET
        else:
            template_version = self.template_version

        template_status: None | str | Unset
        if isinstance(self.template_status, Unset):
            template_status = UNSET
        else:
            template_status = self.template_status

        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

        service_status: None | str | Unset
        if isinstance(self.service_status, Unset):
            service_status = UNSET
        else:
            service_status = self.service_status

        pending_revision_id: None | str | Unset
        if isinstance(self.pending_revision_id, Unset):
            pending_revision_id = UNSET
        elif isinstance(self.pending_revision_id, UUID):
            pending_revision_id = str(self.pending_revision_id)
        else:
            pending_revision_id = self.pending_revision_id

        last_submitted_at: None | str | Unset
        if isinstance(self.last_submitted_at, Unset):
            last_submitted_at = UNSET
        elif isinstance(self.last_submitted_at, datetime.datetime):
            last_submitted_at = self.last_submitted_at.isoformat()
        else:
            last_submitted_at = self.last_submitted_at

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "template_id": template_id,
                "parameters": parameters,
                "created_at": created_at,
            }
        )
        if template_name is not UNSET:
            field_dict["template_name"] = template_name
        if template_version is not UNSET:
            field_dict["template_version"] = template_version
        if template_status is not UNSET:
            field_dict["template_status"] = template_status
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if service_status is not UNSET:
            field_dict["service_status"] = service_status
        if pending_revision_id is not UNSET:
            field_dict["pending_revision_id"] = pending_revision_id
        if last_submitted_at is not UNSET:
            field_dict["last_submitted_at"] = last_submitted_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.template_instance_public_parameters import TemplateInstancePublicParameters

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        template_id = UUID(d.pop("template_id"))

        parameters = TemplateInstancePublicParameters.from_dict(d.pop("parameters"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_template_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        template_name = _parse_template_name(d.pop("template_name", UNSET))

        def _parse_template_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        template_version = _parse_template_version(d.pop("template_version", UNSET))

        def _parse_template_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        template_status = _parse_template_status(d.pop("template_status", UNSET))

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

        def _parse_service_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        service_status = _parse_service_status(d.pop("service_status", UNSET))

        def _parse_pending_revision_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                pending_revision_id_type_0 = UUID(data)

                return pending_revision_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        pending_revision_id = _parse_pending_revision_id(d.pop("pending_revision_id", UNSET))

        def _parse_last_submitted_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_submitted_at_type_0 = isoparse(data)

                return last_submitted_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_submitted_at = _parse_last_submitted_at(d.pop("last_submitted_at", UNSET))

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        template_instance_public = cls(
            id=id,
            name=name,
            template_id=template_id,
            parameters=parameters,
            created_at=created_at,
            template_name=template_name,
            template_version=template_version,
            template_status=template_status,
            service_id=service_id,
            service_status=service_status,
            pending_revision_id=pending_revision_id,
            last_submitted_at=last_submitted_at,
            updated_at=updated_at,
        )

        template_instance_public.additional_properties = d
        return template_instance_public

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
