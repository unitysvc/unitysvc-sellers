from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeprecatedServiceItem")


@_attrs_define
class DeprecatedServiceItem:
    """GET /seller/services/deprecated — row in the deprecation archive.

    Deprecated services are excluded from ``service_mview`` and from
    every browse surface (see #1027). This minimal shape exists only to
    support the recovery workflow: a seller can find a service they
    deprecated and email the id to platform support, who has admin
    access to flip ``deprecated → active``.

    ``deprecated_at`` is the service's ``updated_at`` at the time of the
    status flip. It can drift if the deprecated row is later edited
    (rare), so callers should treat it as "roughly when this was
    deprecated", not as an authoritative event time.

    """

    id: UUID
    name: None | str | Unset = UNSET
    display_name: None | str | Unset = UNSET
    provider_name: None | str | Unset = UNSET
    deprecated_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        provider_name: None | str | Unset
        if isinstance(self.provider_name, Unset):
            provider_name = UNSET
        else:
            provider_name = self.provider_name

        deprecated_at: None | str | Unset
        if isinstance(self.deprecated_at, Unset):
            deprecated_at = UNSET
        elif isinstance(self.deprecated_at, datetime.datetime):
            deprecated_at = self.deprecated_at.isoformat()
        else:
            deprecated_at = self.deprecated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if provider_name is not UNSET:
            field_dict["provider_name"] = provider_name
        if deprecated_at is not UNSET:
            field_dict["deprecated_at"] = deprecated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_provider_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider_name = _parse_provider_name(d.pop("provider_name", UNSET))

        def _parse_deprecated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deprecated_at_type_0 = isoparse(data)

                return deprecated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        deprecated_at = _parse_deprecated_at(d.pop("deprecated_at", UNSET))

        deprecated_service_item = cls(
            id=id,
            name=name,
            display_name=display_name,
            provider_name=provider_name,
            deprecated_at=deprecated_at,
        )

        deprecated_service_item.additional_properties = d
        return deprecated_service_item

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
