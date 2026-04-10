from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.service_enrollment_status_enum import check_service_enrollment_status_enum
from ..models.service_enrollment_status_enum import ServiceEnrollmentStatusEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.service_enrollment_create_parameters_type_0 import ServiceEnrollmentCreateParametersType0
  from ..models.service_enrollment_create_recurrence_schedule_type_0 import ServiceEnrollmentCreateRecurrenceScheduleType0





T = TypeVar("T", bound="ServiceEnrollmentCreate")



@_attrs_define
class ServiceEnrollmentCreate:
    """ Model for creating new Enrollments.

    customer_id is derived from the X-Role-Id header at the route level.
    service_id references the Service identity layer (not listing_id).

     """

    service_id: UUID
    status: None | ServiceEnrollmentStatusEnum | Unset = UNSET
    parameters: None | ServiceEnrollmentCreateParametersType0 | Unset = UNSET
    recurrence_schedule: None | ServiceEnrollmentCreateRecurrenceScheduleType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_enrollment_create_parameters_type_0 import ServiceEnrollmentCreateParametersType0
        from ..models.service_enrollment_create_recurrence_schedule_type_0 import ServiceEnrollmentCreateRecurrenceScheduleType0
        service_id = str(self.service_id)

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, str):
            status = self.status
        else:
            status = self.status

        parameters: dict[str, Any] | None | Unset
        if isinstance(self.parameters, Unset):
            parameters = UNSET
        elif isinstance(self.parameters, ServiceEnrollmentCreateParametersType0):
            parameters = self.parameters.to_dict()
        else:
            parameters = self.parameters

        recurrence_schedule: dict[str, Any] | None | Unset
        if isinstance(self.recurrence_schedule, Unset):
            recurrence_schedule = UNSET
        elif isinstance(self.recurrence_schedule, ServiceEnrollmentCreateRecurrenceScheduleType0):
            recurrence_schedule = self.recurrence_schedule.to_dict()
        else:
            recurrence_schedule = self.recurrence_schedule


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "service_id": service_id,
        })
        if status is not UNSET:
            field_dict["status"] = status
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if recurrence_schedule is not UNSET:
            field_dict["recurrence_schedule"] = recurrence_schedule

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_enrollment_create_parameters_type_0 import ServiceEnrollmentCreateParametersType0
        from ..models.service_enrollment_create_recurrence_schedule_type_0 import ServiceEnrollmentCreateRecurrenceScheduleType0
        d = dict(src_dict)
        service_id = UUID(d.pop("service_id"))




        def _parse_status(data: object) -> None | ServiceEnrollmentStatusEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = check_service_enrollment_status_enum(data)



                return status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceEnrollmentStatusEnum | Unset, data)

        status = _parse_status(d.pop("status", UNSET))


        def _parse_parameters(data: object) -> None | ServiceEnrollmentCreateParametersType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_type_0 = ServiceEnrollmentCreateParametersType0.from_dict(data)



                return parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceEnrollmentCreateParametersType0 | Unset, data)

        parameters = _parse_parameters(d.pop("parameters", UNSET))


        def _parse_recurrence_schedule(data: object) -> None | ServiceEnrollmentCreateRecurrenceScheduleType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                recurrence_schedule_type_0 = ServiceEnrollmentCreateRecurrenceScheduleType0.from_dict(data)



                return recurrence_schedule_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceEnrollmentCreateRecurrenceScheduleType0 | Unset, data)

        recurrence_schedule = _parse_recurrence_schedule(d.pop("recurrence_schedule", UNSET))


        service_enrollment_create = cls(
            service_id=service_id,
            status=status,
            parameters=parameters,
            recurrence_schedule=recurrence_schedule,
        )


        service_enrollment_create.additional_properties = d
        return service_enrollment_create

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
