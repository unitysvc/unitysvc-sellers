from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceFormInstantiateResponse")


@_attrs_define
class ServiceFormInstantiateResponse:
    """202 response for a one-shot instantiate (form created + submitted)."""

    form_id: UUID
    task_id: str
    status: str
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        form_id = str(self.form_id)

        task_id = self.task_id

        status = self.status

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "form_id": form_id,
                "task_id": task_id,
                "status": status,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        form_id = UUID(d.pop("form_id"))

        task_id = d.pop("task_id")

        status = d.pop("status")

        message = d.pop("message")

        service_form_instantiate_response = cls(
            form_id=form_id,
            task_id=task_id,
            status=status,
            message=message,
        )

        service_form_instantiate_response.additional_properties = d
        return service_form_instantiate_response

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
