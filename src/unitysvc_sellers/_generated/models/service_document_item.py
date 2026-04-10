from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.service_document_item_meta_type_0 import ServiceDocumentItemMetaType0





T = TypeVar("T", bound="ServiceDocumentItem")



@_attrs_define
class ServiceDocumentItem:
    """ Document metadata embedded in ServiceDetailResponse.

    Does not include file_content — fetch that separately via
    GET /seller/documents/{id} when needed.

     """

    id: str
    title: str
    description: None | str | Unset = UNSET
    category: None | str | Unset = UNSET
    mime_type: None | str | Unset = UNSET
    filename: None | str | Unset = UNSET
    filesize: int | None | Unset = UNSET
    context_type: None | str | Unset = UNSET
    meta: None | ServiceDocumentItemMetaType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_document_item_meta_type_0 import ServiceDocumentItemMetaType0
        id = self.id

        title = self.title

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        category: None | str | Unset
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        mime_type: None | str | Unset
        if isinstance(self.mime_type, Unset):
            mime_type = UNSET
        else:
            mime_type = self.mime_type

        filename: None | str | Unset
        if isinstance(self.filename, Unset):
            filename = UNSET
        else:
            filename = self.filename

        filesize: int | None | Unset
        if isinstance(self.filesize, Unset):
            filesize = UNSET
        else:
            filesize = self.filesize

        context_type: None | str | Unset
        if isinstance(self.context_type, Unset):
            context_type = UNSET
        else:
            context_type = self.context_type

        meta: dict[str, Any] | None | Unset
        if isinstance(self.meta, Unset):
            meta = UNSET
        elif isinstance(self.meta, ServiceDocumentItemMetaType0):
            meta = self.meta.to_dict()
        else:
            meta = self.meta


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "title": title,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if category is not UNSET:
            field_dict["category"] = category
        if mime_type is not UNSET:
            field_dict["mime_type"] = mime_type
        if filename is not UNSET:
            field_dict["filename"] = filename
        if filesize is not UNSET:
            field_dict["filesize"] = filesize
        if context_type is not UNSET:
            field_dict["context_type"] = context_type
        if meta is not UNSET:
            field_dict["meta"] = meta

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_document_item_meta_type_0 import ServiceDocumentItemMetaType0
        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        category = _parse_category(d.pop("category", UNSET))


        def _parse_mime_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mime_type = _parse_mime_type(d.pop("mime_type", UNSET))


        def _parse_filename(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        filename = _parse_filename(d.pop("filename", UNSET))


        def _parse_filesize(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        filesize = _parse_filesize(d.pop("filesize", UNSET))


        def _parse_context_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        context_type = _parse_context_type(d.pop("context_type", UNSET))


        def _parse_meta(data: object) -> None | ServiceDocumentItemMetaType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                meta_type_0 = ServiceDocumentItemMetaType0.from_dict(data)



                return meta_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceDocumentItemMetaType0 | Unset, data)

        meta = _parse_meta(d.pop("meta", UNSET))


        service_document_item = cls(
            id=id,
            title=title,
            description=description,
            category=category,
            mime_type=mime_type,
            filename=filename,
            filesize=filesize,
            context_type=context_type,
            meta=meta,
        )


        service_document_item.additional_properties = d
        return service_document_item

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
