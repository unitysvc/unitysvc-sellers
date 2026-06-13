from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.parameters import Parameters


T = TypeVar("T", bound="ServiceFormCreate")


@_attrs_define
class ServiceFormCreate:
    """Create a form bound to the active version of a template."""

    template_id: UUID
    name: None | str | Unset = UNSET
    """ Optional label; defaults to the template display name. """
    parameters: Parameters | Unset = UNSET
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

        service_form_create = cls(
            template_id=template_id,
            name=name,
            parameters=parameters,
        )

        service_form_create.additional_properties = d
        return service_form_create

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
