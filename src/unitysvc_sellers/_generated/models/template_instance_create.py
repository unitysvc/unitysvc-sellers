from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.parameters import Parameters


T = TypeVar("T", bound="TemplateInstanceCreate")


@_attrs_define
class TemplateInstanceCreate:
    """Create a template instance and render it into a service.

    Always produces a ``TemplateInstance`` + a **draft** ``Service``. Set
    ``auto_submit=True`` to also submit that draft for review in the same call
    (the one-click "create & submit" path); leave it ``False`` to create a
    reviewable draft and submit later via ``PATCH /seller/services`` (the batch
    path). Request-only — not stored on the instance.

    """

    template_id: UUID
    name: None | str | Unset = UNSET
    """ Optional label; defaults to the template display name. """
    parameters: Parameters | Unset = UNSET
    auto_submit: bool | Unset = False
    """ If true, submit the rendered draft service for review immediately. """
    service_id: None | Unset | UUID = UNSET
    """ Existing canonical service id to update (the seller's durable sidecar handle). When set, re-renders the
    template with the new parameters and applies it to that service — in place for draft/pending, as a revision for
    active — instead of creating a new service. Omit to create a new service. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.parameters import Parameters

        template_id = str(self.template_id)

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        auto_submit = self.auto_submit

        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "template_id": template_id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if auto_submit is not UNSET:
            field_dict["auto_submit"] = auto_submit
        if service_id is not UNSET:
            field_dict["service_id"] = service_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.parameters import Parameters

        d = dict(src_dict)
        template_id = UUID(d.pop("template_id"))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        _parameters = d.pop("parameters", UNSET)
        parameters: Parameters | Unset
        if isinstance(_parameters, Unset):
            parameters = UNSET
        else:
            parameters = Parameters.from_dict(_parameters)

        auto_submit = d.pop("auto_submit", UNSET)

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

        template_instance_create = cls(
            template_id=template_id,
            name=name,
            parameters=parameters,
            auto_submit=auto_submit,
            service_id=service_id,
        )

        template_instance_create.additional_properties = d
        return template_instance_create

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
