from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tasks_get_task_status_response_tasks_get_task_status_additional_property import (
        TasksGetTaskStatusResponseTasksGetTaskStatusAdditionalProperty,
    )


T = TypeVar("T", bound="TasksGetTaskStatusResponseTasksGetTaskStatus")


@_attrs_define
class TasksGetTaskStatusResponseTasksGetTaskStatus:
    additional_properties: dict[str, TasksGetTaskStatusResponseTasksGetTaskStatusAdditionalProperty] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        from ..models.tasks_get_task_status_response_tasks_get_task_status_additional_property import (
            TasksGetTaskStatusResponseTasksGetTaskStatusAdditionalProperty,
        )

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tasks_get_task_status_response_tasks_get_task_status_additional_property import (
            TasksGetTaskStatusResponseTasksGetTaskStatusAdditionalProperty,
        )

        d = dict(src_dict)
        tasks_get_task_status_response_tasks_get_task_status = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = TasksGetTaskStatusResponseTasksGetTaskStatusAdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        tasks_get_task_status_response_tasks_get_task_status.additional_properties = additional_properties
        return tasks_get_task_status_response_tasks_get_task_status

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> TasksGetTaskStatusResponseTasksGetTaskStatusAdditionalProperty:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: TasksGetTaskStatusResponseTasksGetTaskStatusAdditionalProperty) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
