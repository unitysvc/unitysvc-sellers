from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TestRun")


@_attrs_define
class TestRun:
    """One recorded run of a test document (#2622): through one of the
    service's interfaces (``interface_id``), or an upstream probe
    (``interface_id`` null).

    """

    id: UUID
    document_id: UUID
    status: str
    document_title: None | str | Unset = UNSET
    category: None | str | Unset = UNSET
    interface_id: None | Unset | UUID = UNSET
    channel_name: None | str | Unset = UNSET
    exit_code: int | None | Unset = UNSET
    error: None | str | Unset = UNSET
    executed_at: datetime.datetime | None | Unset = UNSET
    has_stdout: bool | Unset = False
    has_stderr: bool | Unset = False
    stale: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        document_id = str(self.document_id)

        status = self.status

        document_title: None | str | Unset
        if isinstance(self.document_title, Unset):
            document_title = UNSET
        else:
            document_title = self.document_title

        category: None | str | Unset
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        interface_id: None | str | Unset
        if isinstance(self.interface_id, Unset):
            interface_id = UNSET
        elif isinstance(self.interface_id, UUID):
            interface_id = str(self.interface_id)
        else:
            interface_id = self.interface_id

        channel_name: None | str | Unset
        if isinstance(self.channel_name, Unset):
            channel_name = UNSET
        else:
            channel_name = self.channel_name

        exit_code: int | None | Unset
        if isinstance(self.exit_code, Unset):
            exit_code = UNSET
        else:
            exit_code = self.exit_code

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        executed_at: None | str | Unset
        if isinstance(self.executed_at, Unset):
            executed_at = UNSET
        elif isinstance(self.executed_at, datetime.datetime):
            executed_at = self.executed_at.isoformat()
        else:
            executed_at = self.executed_at

        has_stdout = self.has_stdout

        has_stderr = self.has_stderr

        stale = self.stale

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "document_id": document_id,
                "status": status,
            }
        )
        if document_title is not UNSET:
            field_dict["document_title"] = document_title
        if category is not UNSET:
            field_dict["category"] = category
        if interface_id is not UNSET:
            field_dict["interface_id"] = interface_id
        if channel_name is not UNSET:
            field_dict["channel_name"] = channel_name
        if exit_code is not UNSET:
            field_dict["exit_code"] = exit_code
        if error is not UNSET:
            field_dict["error"] = error
        if executed_at is not UNSET:
            field_dict["executed_at"] = executed_at
        if has_stdout is not UNSET:
            field_dict["has_stdout"] = has_stdout
        if has_stderr is not UNSET:
            field_dict["has_stderr"] = has_stderr
        if stale is not UNSET:
            field_dict["stale"] = stale

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        document_id = UUID(d.pop("document_id"))

        status = d.pop("status")

        def _parse_document_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        document_title = _parse_document_title(d.pop("document_title", UNSET))

        def _parse_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        category = _parse_category(d.pop("category", UNSET))

        def _parse_interface_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                interface_id_type_0 = UUID(data)

                return interface_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        interface_id = _parse_interface_id(d.pop("interface_id", UNSET))

        def _parse_channel_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        channel_name = _parse_channel_name(d.pop("channel_name", UNSET))

        def _parse_exit_code(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        exit_code = _parse_exit_code(d.pop("exit_code", UNSET))

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_executed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                executed_at_type_0 = isoparse(data)

                return executed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        executed_at = _parse_executed_at(d.pop("executed_at", UNSET))

        has_stdout = d.pop("has_stdout", UNSET)

        has_stderr = d.pop("has_stderr", UNSET)

        stale = d.pop("stale", UNSET)

        test_run = cls(
            id=id,
            document_id=document_id,
            status=status,
            document_title=document_title,
            category=category,
            interface_id=interface_id,
            channel_name=channel_name,
            exit_code=exit_code,
            error=error,
            executed_at=executed_at,
            has_stdout=has_stdout,
            has_stderr=has_stderr,
            stale=stale,
        )

        test_run.additional_properties = d
        return test_run

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
