from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnrollmentKeyLease")


@_attrs_define
class EnrollmentKeyLease:
    """A key acting for the enrollment, returned once. Return it when done."""

    key_id: UUID
    apikey_identifier: str
    apikey: str
    expires_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key_id = str(self.key_id)

        apikey_identifier = self.apikey_identifier

        apikey = self.apikey

        expires_at = self.expires_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key_id": key_id,
                "apikey_identifier": apikey_identifier,
                "apikey": apikey,
                "expires_at": expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        key_id = UUID(d.pop("key_id"))

        apikey_identifier = d.pop("apikey_identifier")

        apikey = d.pop("apikey")

        expires_at = isoparse(d.pop("expires_at"))

        enrollment_key_lease = cls(
            key_id=key_id,
            apikey_identifier=apikey_identifier,
            apikey=apikey,
            expires_at=expires_at,
        )

        enrollment_key_lease.additional_properties = d
        return enrollment_key_lease

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
