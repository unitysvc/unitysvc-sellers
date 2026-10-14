from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_test_update_status import DocumentTestUpdateStatus, check_document_test_update_status
from ..types import UNSET, Unset

T = TypeVar("T", bound="DocumentTestUpdate")


@_attrs_define
class DocumentTestUpdate:
    """Request body for updating document test status.

    The ``status`` field drives dispatch:

    - ``skip`` — mark the test as skipped (stamps ``skipped_at`` /
      ``skipped_by``). Rejected for ``connectivity_test`` documents (only
      ``code_example`` can be skipped).
    - ``pending`` — unskip, and forget the document's recorded runs
      (including earned sticky passes), so the next run re-proves it.

    Test results are recorded only by the platform's own runners; a seller
    cannot report one.

    This endpoint replaces the previously-separate /skip and /unskip routes,
    which dispatched to the same backing field via different HTTP verbs.

    """

    status: DocumentTestUpdateStatus
    """ skip | pending """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status: str = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = check_document_test_update_status(d.pop("status"))

        document_test_update = cls(
            status=status,
        )

        document_test_update.additional_properties = d
        return document_test_update

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
