from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_test_update_tests_type_0 import DocumentTestUpdateTestsType0


T = TypeVar("T", bound="DocumentTestUpdate")


@_attrs_define
class DocumentTestUpdate:
    """Request body for updating document test status.

    The ``status`` field drives dispatch:

    - ``skip`` — mark the test as skipped. Clears execution results and
      stamps ``skipped_at`` / ``skipped_by``. Rejected for
      ``connectivity_test`` documents (only ``code_example`` can be skipped).
    - ``pending`` — unskip. Clears execution results and stamps
      ``unskipped_at`` / ``unskipped_by``. Ready for a fresh run.
    - ``success`` / ``task_failed`` / ``script_failed`` / ``unexpected_output``
      — record the result of an external test run. Optional ``executed_at``
      and per-interface ``tests`` payload are persisted on the document.

    This endpoint replaces the previously-separate /skip and /unskip routes,
    which dispatched to the same backing field via different HTTP verbs.

    """

    status: str
    """ skip | pending | success | task_failed | script_failed | unexpected_output """
    executed_at: None | str | Unset = UNSET
    """ ISO timestamp of execution (external results only) """
    tests: DocumentTestUpdateTestsType0 | None | Unset = UNSET
    """ Per-interface test results: {name: {status, exit_code, stdout, stderr, error}} """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.document_test_update_tests_type_0 import DocumentTestUpdateTestsType0

        status = self.status

        executed_at: None | str | Unset
        if isinstance(self.executed_at, Unset):
            executed_at = UNSET
        else:
            executed_at = self.executed_at

        tests: dict[str, Any] | None | Unset
        if isinstance(self.tests, Unset):
            tests = UNSET
        elif isinstance(self.tests, DocumentTestUpdateTestsType0):
            tests = self.tests.to_dict()
        else:
            tests = self.tests

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if executed_at is not UNSET:
            field_dict["executed_at"] = executed_at
        if tests is not UNSET:
            field_dict["tests"] = tests

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_test_update_tests_type_0 import DocumentTestUpdateTestsType0

        d = dict(src_dict)
        status = d.pop("status")

        def _parse_executed_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        executed_at = _parse_executed_at(d.pop("executed_at", UNSET))

        def _parse_tests(data: object) -> DocumentTestUpdateTestsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tests_type_0 = DocumentTestUpdateTestsType0.from_dict(data)

                return tests_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentTestUpdateTestsType0 | None | Unset, data)

        tests = _parse_tests(d.pop("tests", UNSET))

        document_test_update = cls(
            status=status,
            executed_at=executed_at,
            tests=tests,
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
