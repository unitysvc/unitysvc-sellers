from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.document_test_status_response_test_type_0 import DocumentTestStatusResponseTestType0





T = TypeVar("T", bound="DocumentTestStatusResponse")



@_attrs_define
class DocumentTestStatusResponse:
    """ PATCH /seller/documents/{id} — unified response for skip/unskip/update.

    The same endpoint now handles three operations via the status field in
    the request body: skip, pending (unskip), or an external test result
    status (success|task_failed|script_failed|unexpected_output).

     """

    document_id: str
    status: str
    message: str
    test: DocumentTestStatusResponseTestType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.document_test_status_response_test_type_0 import DocumentTestStatusResponseTestType0
        document_id = self.document_id

        status = self.status

        message = self.message

        test: dict[str, Any] | None | Unset
        if isinstance(self.test, Unset):
            test = UNSET
        elif isinstance(self.test, DocumentTestStatusResponseTestType0):
            test = self.test.to_dict()
        else:
            test = self.test


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "document_id": document_id,
            "status": status,
            "message": message,
        })
        if test is not UNSET:
            field_dict["test"] = test

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_test_status_response_test_type_0 import DocumentTestStatusResponseTestType0
        d = dict(src_dict)
        document_id = d.pop("document_id")

        status = d.pop("status")

        message = d.pop("message")

        def _parse_test(data: object) -> DocumentTestStatusResponseTestType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                test_type_0 = DocumentTestStatusResponseTestType0.from_dict(data)



                return test_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentTestStatusResponseTestType0 | None | Unset, data)

        test = _parse_test(d.pop("test", UNSET))


        document_test_status_response = cls(
            document_id=document_id,
            status=status,
            message=message,
            test=test,
        )


        document_test_status_response.additional_properties = d
        return document_test_status_response

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
