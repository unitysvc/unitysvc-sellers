from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.test_run_gap_reason import TestRunGapReason, check_test_run_gap_reason
from ..types import UNSET, Unset

T = TypeVar("T", bound="TestRunGap")


@_attrs_define
class TestRunGap:
    """A run admission requires but does not have: never run
    (``reason="missing"``) or, for a platform member, run before the test or
    the member changed (``reason="stale"``).

    """

    document_id: UUID
    document_title: str
    interface_id: None | Unset | UUID = UNSET
    channel_name: None | str | Unset = UNSET
    reason: TestRunGapReason | Unset = "missing"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        document_id = str(self.document_id)

        document_title = self.document_title

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

        reason: str | Unset = UNSET
        if not isinstance(self.reason, Unset):
            reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document_id": document_id,
                "document_title": document_title,
            }
        )
        if interface_id is not UNSET:
            field_dict["interface_id"] = interface_id
        if channel_name is not UNSET:
            field_dict["channel_name"] = channel_name
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        document_id = UUID(d.pop("document_id"))

        document_title = d.pop("document_title")

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

        _reason = d.pop("reason", UNSET)
        reason: TestRunGapReason | Unset
        if isinstance(_reason, Unset):
            reason = UNSET
        else:
            reason = check_test_run_gap_reason(_reason)

        test_run_gap = cls(
            document_id=document_id,
            document_title=document_title,
            interface_id=interface_id,
            channel_name=channel_name,
            reason=reason,
        )

        test_run_gap.additional_properties = d
        return test_run_gap

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
