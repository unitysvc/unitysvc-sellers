from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceStatus")


@_attrs_define
class ServiceStatus:
    """Backend-assigned service **status / identity sidecar** (the ``service.json``
    file) — *not* the authored service data.

    A service's ``provider_data`` / ``offering_data`` / ``listing_data`` are the
    authored service data; this is the *other*, backend-owned half — the status
    record the backend materializes once a service exists. It is the
    **round-trip** sidecar: the ingest task returns it, the seller stores it in
    ``service.json`` beside the spec files, and replays it on the next
    upload/revision so the backend can match the upload to the existing service.

    Of these fields, ``service_id`` and ``template_instance_id`` are consumed on
    the way *in* (they declare which service / which template the publish
    targets); the rest are populated on the way *out* as informational status /
    provenance for the seller. ``extra="ignore"`` keeps unknown keys from
    breaking either direction.

    """

    service_id: None | Unset | UUID = UNSET
    """ Backend-assigned service id from a previous publish. When present on upload, the request targets the
    existing service (revise/replace) instead of creating a new one. """
    revision_of: None | Unset | UUID = UNSET
    """ Set when this record describes a revision: the canonical service id the revision derives from.
    ``service_id`` is then the revision's own id. """
    status: None | str | Unset = UNSET
    """ Service identity status as resolved by the last ingest. """
    name: None | str | Unset = UNSET
    """ Backend-derived service name (from listing/offering). """
    display_name: None | str | Unset = UNSET
    """ Backend-derived human-readable service name. """
    time_created: datetime.datetime | None | Unset = UNSET
    """ When the service was first created (informational provenance). """
    template_instance_id: None | Unset | UUID = UNSET
    """ Set when the service was published from a seller TemplateInstance (the seller-instances flow). Like
    ``service_id`` it is consumed on the way *in* to declare the operation — with no ``service_id`` it creates a
    service from the template (the backend pins the form's service_id); with one it updates an existing template-
    generated service — and echoed on the way *out* so ``service.json`` records the template association. Absent for
    plain (non-template) services. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

        revision_of: None | str | Unset
        if isinstance(self.revision_of, Unset):
            revision_of = UNSET
        elif isinstance(self.revision_of, UUID):
            revision_of = str(self.revision_of)
        else:
            revision_of = self.revision_of

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        time_created: None | str | Unset
        if isinstance(self.time_created, Unset):
            time_created = UNSET
        elif isinstance(self.time_created, datetime.datetime):
            time_created = self.time_created.isoformat()
        else:
            time_created = self.time_created

        template_instance_id: None | str | Unset
        if isinstance(self.template_instance_id, Unset):
            template_instance_id = UNSET
        elif isinstance(self.template_instance_id, UUID):
            template_instance_id = str(self.template_instance_id)
        else:
            template_instance_id = self.template_instance_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if revision_of is not UNSET:
            field_dict["revision_of"] = revision_of
        if status is not UNSET:
            field_dict["status"] = status
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if time_created is not UNSET:
            field_dict["time_created"] = time_created
        if template_instance_id is not UNSET:
            field_dict["template_instance_id"] = template_instance_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

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

        def _parse_revision_of(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                revision_of_type_0 = UUID(data)

                return revision_of_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        revision_of = _parse_revision_of(d.pop("revision_of", UNSET))

        def _parse_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_time_created(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                time_created_type_0 = isoparse(data)

                return time_created_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        time_created = _parse_time_created(d.pop("time_created", UNSET))

        def _parse_template_instance_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                template_instance_id_type_0 = UUID(data)

                return template_instance_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        template_instance_id = _parse_template_instance_id(d.pop("template_instance_id", UNSET))

        service_status = cls(
            service_id=service_id,
            revision_of=revision_of,
            status=status,
            name=name,
            display_name=display_name,
            time_created=time_created,
            template_instance_id=template_instance_id,
        )

        service_status.additional_properties = d
        return service_status

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
