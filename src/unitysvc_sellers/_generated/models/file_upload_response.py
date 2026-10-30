from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FileUploadResponse")


@_attrs_define
class FileUploadResponse:
    """Response for content-addressed file upload."""

    object_key: str
    filename: str
    mime_type: str
    size: int
    uploaded: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        object_key = self.object_key

        filename = self.filename

        mime_type = self.mime_type

        size = self.size

        uploaded = self.uploaded

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object_key": object_key,
                "filename": filename,
                "mime_type": mime_type,
                "size": size,
                "uploaded": uploaded,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        object_key = d.pop("object_key")

        filename = d.pop("filename")

        mime_type = d.pop("mime_type")

        size = d.pop("size")

        uploaded = d.pop("uploaded")

        file_upload_response = cls(
            object_key=object_key,
            filename=filename,
            mime_type=mime_type,
            size=size,
            uploaded=uploaded,
        )

        file_upload_response.additional_properties = d
        return file_upload_response

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
