from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_data_input import ServiceDataInput
    from ..models.service_status import ServiceStatus


T = TypeVar("T", bound="BodyServicesUpload")


@_attrs_define
class BodyServicesUpload:
    data: ServiceDataInput
    """ Authored service content for publishing (provider + offering + listing).

    Fields are typed against the shared ``unitysvc_core`` models so the
    OpenAPI spec carries the full provider/offering/listing schemas, and
    generated clients expose typed upload methods instead of ``dict[str, Any]``.
    The status sidecar (``ServiceStatus``) is a separate ``service_status``
    parameter, not a field here. """
    service_status: None | ServiceStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_data_input import ServiceDataInput
        from ..models.service_status import ServiceStatus

        data = self.data.to_dict()

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
                "data": data,
            }
        )
        if service_status is not UNSET:
            field_dict["service_status"] = service_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_data_input import ServiceDataInput
        from ..models.service_status import ServiceStatus

        d = dict(src_dict)
        data = ServiceDataInput.from_dict(d.pop("data"))

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

        body_services_upload = cls(
            data=data,
            service_status=service_status,
        )

        body_services_upload.additional_properties = d
        return body_services_upload

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
