from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.secret_owner_type_enum import SecretOwnerTypeEnum, check_secret_owner_type_enum
from ..types import UNSET, Unset

T = TypeVar("T", bound="SecretPublic")


@_attrs_define
class SecretPublic:
    """Public schema for secret info (excludes value - write-only)."""

    name: str
    """ Secret name (e.g., OPENAI_API_KEY). Must be uppercase letters, digits, and underscores; must start with a
    letter or underscore. """
    id: UUID
    owner_type: SecretOwnerTypeEnum
    """ Owner type for secrets - determines which entity owns the secret. """
    owner_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    last_used_at: datetime.datetime | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        id = str(self.id)

        owner_type: str = self.owner_type

        owner_id = str(self.owner_id)

        created_at = self.created_at.isoformat()

        updated_at: None | str
        if isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        last_used_at: None | str
        if isinstance(self.last_used_at, datetime.datetime):
            last_used_at = self.last_used_at.isoformat()
        else:
            last_used_at = self.last_used_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "id": id,
                "owner_type": owner_type,
                "owner_id": owner_id,
                "created_at": created_at,
                "updated_at": updated_at,
                "last_used_at": last_used_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        id = UUID(d.pop("id"))

        owner_type = check_secret_owner_type_enum(d.pop("owner_type"))

        owner_id = UUID(d.pop("owner_id"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_updated_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        updated_at = _parse_updated_at(d.pop("updated_at"))

        def _parse_last_used_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_used_at_type_0 = isoparse(data)

                return last_used_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        last_used_at = _parse_last_used_at(d.pop("last_used_at"))

        secret_public = cls(
            name=name,
            id=id,
            owner_type=owner_type,
            owner_id=owner_id,
            created_at=created_at,
            updated_at=updated_at,
            last_used_at=last_used_at,
        )

        secret_public.additional_properties = d
        return secret_public

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
