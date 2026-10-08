from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_data_input import ServiceDataInput
    from ..models.service_status import ServiceStatus
    from ..models.service_template_create import ServiceTemplateCreate


T = TypeVar("T", bound="PlatformServiceUpload")


@_attrs_define
class PlatformServiceUpload:
    """A platform service and its member template, published together (#2569).

    A platform service is a seller's product: it buys capacity from member
    sellers and resells it at a ``/p`` address its listing declares. The member
    template is what other sellers instantiate to join it, so it travels in the
    same upload and is owned through the platform service.

    """

    service_data: ServiceDataInput
    """ Authored service content for publishing (provider + offering + listing).

    Fields are typed against the shared ``unitysvc_core`` models so the
    OpenAPI spec carries the full provider/offering/listing schemas, and
    generated clients expose typed upload methods instead of ``dict[str, Any]``.
    The status sidecar (``ServiceStatus``) is a separate ``service_status``
    parameter, not a field here. """
    member_template: ServiceTemplateCreate
    """ Schema for creating/updating a ServiceTemplate (admin upload).

    ``status`` defaults to ``draft``; the renderer bodies and schemas are
    required so the stored row is self-contained.

    ``id`` is honored on CREATE only (the ``template_id.json`` sidecar
    replayed across environments, so a template keeps ONE id on staging and
    production — the same convention service ids follow). The upsert key
    stays ``(name, version)``: on update the id is ignored. """
    service_status: None | ServiceStatus | Unset = UNSET
    """ The platform service's service.json sidecar; its service_id is the platform service's identity (it survives
    a rename) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_data_input import ServiceDataInput
        from ..models.service_status import ServiceStatus
        from ..models.service_template_create import ServiceTemplateCreate

        service_data = self.service_data.to_dict()

        member_template = self.member_template.to_dict()

        service_status: dict[str, Any] | None | Unset
        if isinstance(self.service_status, Unset):
            service_status = UNSET
        elif isinstance(self.service_status, ServiceStatus):
            service_status = self.service_status.to_dict()
        else:
            service_status = self.service_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service_data": service_data,
                "member_template": member_template,
            }
        )
        if service_status is not UNSET:
            field_dict["service_status"] = service_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_data_input import ServiceDataInput
        from ..models.service_status import ServiceStatus
        from ..models.service_template_create import ServiceTemplateCreate

        d = dict(src_dict)
        service_data = ServiceDataInput.from_dict(d.pop("service_data"))

        member_template = ServiceTemplateCreate.from_dict(d.pop("member_template"))

        def _parse_service_status(data: object) -> None | ServiceStatus | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                service_status_type_0 = ServiceStatus.from_dict(data)

                return service_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceStatus | Unset, data)

        service_status = _parse_service_status(d.pop("service_status", UNSET))

        platform_service_upload = cls(
            service_data=service_data,
            member_template=member_template,
            service_status=service_status,
        )

        platform_service_upload.additional_properties = d
        return platform_service_upload

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
