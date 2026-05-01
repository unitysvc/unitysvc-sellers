from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.response_tasks_get_task_status_additional_property import ResponseTasksGetTaskStatusAdditionalProperty


T = TypeVar("T", bound="ResponseTasksGetTaskStatus")


@_attrs_define
class ResponseTasksGetTaskStatus:
    additional_properties: dict[str, ResponseTasksGetTaskStatusAdditionalProperty] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.response_tasks_get_task_status_additional_property import (
            ResponseTasksGetTaskStatusAdditionalProperty,
        )

        d = dict(src_dict)
        response_tasks_get_task_status = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = ResponseTasksGetTaskStatusAdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        response_tasks_get_task_status.additional_properties = additional_properties
        return response_tasks_get_task_status

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> ResponseTasksGetTaskStatusAdditionalProperty:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: ResponseTasksGetTaskStatusAdditionalProperty) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
