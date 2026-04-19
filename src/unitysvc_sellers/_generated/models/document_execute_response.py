from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_execute_response_test_type_0 import DocumentExecuteResponseTestType0


T = TypeVar("T", bound="DocumentExecuteResponse")


@_attrs_define
class DocumentExecuteResponse:
    """POST /seller/documents/{id}/execute — queues a Celery test run.

    This is the seller's pre-submission dry-run tool. It does NOT touch
    service status or trigger admin review — contrast with the formal
    submission flow via PATCH /seller/services/{id} (set_status=pending).

    """

    document_id: str
    status: str
    message: str
    task_id: None | str | Unset = UNSET
    test: DocumentExecuteResponseTestType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.document_execute_response_test_type_0 import DocumentExecuteResponseTestType0

        document_id = self.document_id

        status = self.status

        message = self.message

        task_id: None | str | Unset
        if isinstance(self.task_id, Unset):
            task_id = UNSET
        else:
            task_id = self.task_id

        test: dict[str, Any] | None | Unset
        if isinstance(self.test, Unset):
            test = UNSET
        elif isinstance(self.test, DocumentExecuteResponseTestType0):
            test = self.test.to_dict()
        else:
            test = self.test

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document_id": document_id,
                "status": status,
                "message": message,
            }
        )
        if task_id is not UNSET:
            field_dict["task_id"] = task_id
        if test is not UNSET:
            field_dict["test"] = test

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_execute_response_test_type_0 import DocumentExecuteResponseTestType0

        d = dict(src_dict)
        document_id = d.pop("document_id")

        status = d.pop("status")

        message = d.pop("message")

        def _parse_task_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        task_id = _parse_task_id(d.pop("task_id", UNSET))

        def _parse_test(data: object) -> DocumentExecuteResponseTestType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                test_type_0 = DocumentExecuteResponseTestType0.from_dict(data)

                return test_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentExecuteResponseTestType0 | None | Unset, data)

        test = _parse_test(d.pop("test", UNSET))

        document_execute_response = cls(
            document_id=document_id,
            status=status,
            message=message,
            task_id=task_id,
            test=test,
        )

        document_execute_response.additional_properties = d
        return document_execute_response

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
