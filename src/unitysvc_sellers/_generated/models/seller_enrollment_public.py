from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.service_enrollment_status_enum import ServiceEnrollmentStatusEnum, check_service_enrollment_status_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.seller_enrollment_public_parameters_type_0 import SellerEnrollmentPublicParametersType0


T = TypeVar("T", bound="SellerEnrollmentPublic")


@_attrs_define
class SellerEnrollmentPublic:
    """An enrollment in one of the seller's services, without the customer's
    identity. Sensitive parameters are masked.

    """

    id: UUID
    service_id: UUID
    channel: str
    code: str
    status: ServiceEnrollmentStatusEnum
    """ Status of a customer's service enrollment.

    Workflow for services requiring parameters (user_parameters_schema exists):

        [not enrolled] → (enroll) → pending → (task completes) → incomplete → (configure) → active
                              │                                                                ↓
                              │                                  paused ← (pause) ←───────────┘
                              │
                              └─→ active  (if required secret already exists)

    Workflow for services without parameters:

        [not enrolled] → (enroll) → pending → (task completes) → active
                                                                    ↓
                                      paused ← (pause) ←──────────┘

    States:
    - pending: Celery task is processing (transient, show spinner)
    - incomplete: Needs user configuration (required parameters not provided)
    - active: Enrolled and fully configured
    - paused: Enrolled but temporarily disabled
    - cancelled: Enrollment cancelled

    Secrets do not affect enrollment status — they are resolved at routing time. """
    created_at: datetime.datetime
    parameters: None | SellerEnrollmentPublicParametersType0 | Unset = UNSET
    expires_at: datetime.datetime | None | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.seller_enrollment_public_parameters_type_0 import SellerEnrollmentPublicParametersType0

        id = str(self.id)

        service_id = str(self.service_id)

        channel = self.channel

        code = self.code

        status: str = self.status

        created_at = self.created_at.isoformat()

        parameters: dict[str, Any] | None | Unset
        if isinstance(self.parameters, Unset):
            parameters = UNSET
        elif isinstance(self.parameters, SellerEnrollmentPublicParametersType0):
            parameters = self.parameters.to_dict()
        else:
            parameters = self.parameters

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "service_id": service_id,
                "channel": channel,
                "code": code,
                "status": status,
                "created_at": created_at,
            }
        )
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.seller_enrollment_public_parameters_type_0 import SellerEnrollmentPublicParametersType0

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        service_id = UUID(d.pop("service_id"))

        channel = d.pop("channel")

        code = d.pop("code")

        status = check_service_enrollment_status_enum(d.pop("status"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_parameters(data: object) -> None | SellerEnrollmentPublicParametersType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_type_0 = SellerEnrollmentPublicParametersType0.from_dict(data)

                return parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SellerEnrollmentPublicParametersType0 | Unset, data)

        parameters = _parse_parameters(d.pop("parameters", UNSET))

        def _parse_expires_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        seller_enrollment_public = cls(
            id=id,
            service_id=service_id,
            channel=channel,
            code=code,
            status=status,
            created_at=created_at,
            parameters=parameters,
            expires_at=expires_at,
            updated_at=updated_at,
        )

        seller_enrollment_public.additional_properties = d
        return seller_enrollment_public

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
