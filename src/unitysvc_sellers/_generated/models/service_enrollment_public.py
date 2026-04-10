from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.service_enrollment_status_enum import check_service_enrollment_status_enum
from ..models.service_enrollment_status_enum import ServiceEnrollmentStatusEnum
from ..models.service_type_enum import check_service_type_enum
from ..models.service_type_enum import ServiceTypeEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.service_enrollment_public_parameters_type_0 import ServiceEnrollmentPublicParametersType0
  from ..models.service_enrollment_public_recurrence_schedule_type_0 import ServiceEnrollmentPublicRecurrenceScheduleType0
  from ..models.service_enrollment_public_recurrence_state_type_0 import ServiceEnrollmentPublicRecurrenceStateType0





T = TypeVar("T", bound="ServiceEnrollmentPublic")



@_attrs_define
class ServiceEnrollmentPublic:
    """ Public response model for Enrollments.

     """

    enrollment_id: UUID
    service_id: None | Unset | UUID = UNSET
    customer_id: None | Unset | UUID = UNSET
    customer_name: None | str | Unset = UNSET
    status: None | ServiceEnrollmentStatusEnum | Unset = UNSET
    parameters: None | ServiceEnrollmentPublicParametersType0 | Unset = UNSET
    recurrence_schedule: None | ServiceEnrollmentPublicRecurrenceScheduleType0 | Unset = UNSET
    recurrence_state: None | ServiceEnrollmentPublicRecurrenceStateType0 | Unset = UNSET
    was_created: bool | None | Unset = False
    service_name: None | str | Unset = UNSET
    service_type: None | ServiceTypeEnum | Unset = UNSET
    listing_type: None | str | Unset = UNSET
    provider_name: None | str | Unset = UNSET
    seller_name: None | str | Unset = UNSET
    expires_at: None | str | Unset = UNSET
    created_at: None | str | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_enrollment_public_parameters_type_0 import ServiceEnrollmentPublicParametersType0
        from ..models.service_enrollment_public_recurrence_schedule_type_0 import ServiceEnrollmentPublicRecurrenceScheduleType0
        from ..models.service_enrollment_public_recurrence_state_type_0 import ServiceEnrollmentPublicRecurrenceStateType0
        enrollment_id = str(self.enrollment_id)

        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

        customer_id: None | str | Unset
        if isinstance(self.customer_id, Unset):
            customer_id = UNSET
        elif isinstance(self.customer_id, UUID):
            customer_id = str(self.customer_id)
        else:
            customer_id = self.customer_id

        customer_name: None | str | Unset
        if isinstance(self.customer_name, Unset):
            customer_name = UNSET
        else:
            customer_name = self.customer_name

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
        elif isinstance(self.parameters, ServiceEnrollmentPublicParametersType0):
            parameters = self.parameters.to_dict()
        else:
            parameters = self.parameters

        recurrence_schedule: dict[str, Any] | None | Unset
        if isinstance(self.recurrence_schedule, Unset):
            recurrence_schedule = UNSET
        elif isinstance(self.recurrence_schedule, ServiceEnrollmentPublicRecurrenceScheduleType0):
            recurrence_schedule = self.recurrence_schedule.to_dict()
        else:
            recurrence_schedule = self.recurrence_schedule

        recurrence_state: dict[str, Any] | None | Unset
        if isinstance(self.recurrence_state, Unset):
            recurrence_state = UNSET
        elif isinstance(self.recurrence_state, ServiceEnrollmentPublicRecurrenceStateType0):
            recurrence_state = self.recurrence_state.to_dict()
        else:
            recurrence_state = self.recurrence_state

        was_created: bool | None | Unset
        if isinstance(self.was_created, Unset):
            was_created = UNSET
        else:
            was_created = self.was_created

        service_name: None | str | Unset
        if isinstance(self.service_name, Unset):
            service_name = UNSET
        else:
            service_name = self.service_name

        service_type: None | str | Unset
        if isinstance(self.service_type, Unset):
            service_type = UNSET
        elif isinstance(self.service_type, str):
            service_type = self.service_type
        else:
            service_type = self.service_type

        listing_type: None | str | Unset
        if isinstance(self.listing_type, Unset):
            listing_type = UNSET
        else:
            listing_type = self.listing_type

        provider_name: None | str | Unset
        if isinstance(self.provider_name, Unset):
            provider_name = UNSET
        else:
            provider_name = self.provider_name

        seller_name: None | str | Unset
        if isinstance(self.seller_name, Unset):
            seller_name = UNSET
        else:
            seller_name = self.seller_name

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        else:
            expires_at = self.expires_at

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "enrollment_id": enrollment_id,
        })
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if customer_id is not UNSET:
            field_dict["customer_id"] = customer_id
        if customer_name is not UNSET:
            field_dict["customer_name"] = customer_name
        if status is not UNSET:
            field_dict["status"] = status
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if recurrence_schedule is not UNSET:
            field_dict["recurrence_schedule"] = recurrence_schedule
        if recurrence_state is not UNSET:
            field_dict["recurrence_state"] = recurrence_state
        if was_created is not UNSET:
            field_dict["was_created"] = was_created
        if service_name is not UNSET:
            field_dict["service_name"] = service_name
        if service_type is not UNSET:
            field_dict["service_type"] = service_type
        if listing_type is not UNSET:
            field_dict["listing_type"] = listing_type
        if provider_name is not UNSET:
            field_dict["provider_name"] = provider_name
        if seller_name is not UNSET:
            field_dict["seller_name"] = seller_name
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_enrollment_public_parameters_type_0 import ServiceEnrollmentPublicParametersType0
        from ..models.service_enrollment_public_recurrence_schedule_type_0 import ServiceEnrollmentPublicRecurrenceScheduleType0
        from ..models.service_enrollment_public_recurrence_state_type_0 import ServiceEnrollmentPublicRecurrenceStateType0
        d = dict(src_dict)
        enrollment_id = UUID(d.pop("enrollment_id"))




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


        def _parse_customer_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                customer_id_type_0 = UUID(data)



                return customer_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        customer_id = _parse_customer_id(d.pop("customer_id", UNSET))


        def _parse_customer_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        customer_name = _parse_customer_name(d.pop("customer_name", UNSET))


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


        def _parse_parameters(data: object) -> None | ServiceEnrollmentPublicParametersType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_type_0 = ServiceEnrollmentPublicParametersType0.from_dict(data)



                return parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceEnrollmentPublicParametersType0 | Unset, data)

        parameters = _parse_parameters(d.pop("parameters", UNSET))


        def _parse_recurrence_schedule(data: object) -> None | ServiceEnrollmentPublicRecurrenceScheduleType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                recurrence_schedule_type_0 = ServiceEnrollmentPublicRecurrenceScheduleType0.from_dict(data)



                return recurrence_schedule_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceEnrollmentPublicRecurrenceScheduleType0 | Unset, data)

        recurrence_schedule = _parse_recurrence_schedule(d.pop("recurrence_schedule", UNSET))


        def _parse_recurrence_state(data: object) -> None | ServiceEnrollmentPublicRecurrenceStateType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                recurrence_state_type_0 = ServiceEnrollmentPublicRecurrenceStateType0.from_dict(data)



                return recurrence_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceEnrollmentPublicRecurrenceStateType0 | Unset, data)

        recurrence_state = _parse_recurrence_state(d.pop("recurrence_state", UNSET))


        def _parse_was_created(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        was_created = _parse_was_created(d.pop("was_created", UNSET))


        def _parse_service_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        service_name = _parse_service_name(d.pop("service_name", UNSET))


        def _parse_service_type(data: object) -> None | ServiceTypeEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_type_type_0 = check_service_type_enum(data)



                return service_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceTypeEnum | Unset, data)

        service_type = _parse_service_type(d.pop("service_type", UNSET))


        def _parse_listing_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        listing_type = _parse_listing_type(d.pop("listing_type", UNSET))


        def _parse_provider_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider_name = _parse_provider_name(d.pop("provider_name", UNSET))


        def _parse_seller_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        seller_name = _parse_seller_name(d.pop("seller_name", UNSET))


        def _parse_expires_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))


        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))


        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))


        service_enrollment_public = cls(
            enrollment_id=enrollment_id,
            service_id=service_id,
            customer_id=customer_id,
            customer_name=customer_name,
            status=status,
            parameters=parameters,
            recurrence_schedule=recurrence_schedule,
            recurrence_state=recurrence_state,
            was_created=was_created,
            service_name=service_name,
            service_type=service_type,
            listing_type=listing_type,
            provider_name=provider_name,
            seller_name=seller_name,
            expires_at=expires_at,
            created_at=created_at,
            updated_at=updated_at,
        )


        service_enrollment_public.additional_properties = d
        return service_enrollment_public

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
