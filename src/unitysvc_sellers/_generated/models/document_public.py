from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.document_category_enum import check_document_category_enum
from ..models.document_category_enum import DocumentCategoryEnum
from ..models.document_context_enum import check_document_context_enum
from ..models.document_context_enum import DocumentContextEnum
from ..models.mime_type_enum import check_mime_type_enum
from ..models.mime_type_enum import MimeTypeEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.document_public_meta_type_0 import DocumentPublicMetaType0





T = TypeVar("T", bound="DocumentPublic")



@_attrs_define
class DocumentPublic:
    """ Public Document model for API responses.

     """

    id: UUID
    entity_id: UUID
    context_type: DocumentContextEnum
    title: str
    mime_type: MimeTypeEnum
    category: DocumentCategoryEnum
    sort_order: int
    is_active: bool
    is_public: bool
    created_at: str
    description: None | str | Unset = UNSET
    version: None | str | Unset = UNSET
    meta: DocumentPublicMetaType0 | None | Unset = UNSET
    external_url: None | str | Unset = UNSET
    object_key: None | str | Unset = UNSET
    filename: None | str | Unset = UNSET
    filesize: int | None | Unset = UNSET
    file_content: None | str | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.document_public_meta_type_0 import DocumentPublicMetaType0
        id = str(self.id)

        entity_id = str(self.entity_id)

        context_type: str = self.context_type

        title = self.title

        mime_type: str = self.mime_type

        category: str = self.category

        sort_order = self.sort_order

        is_active = self.is_active

        is_public = self.is_public

        created_at = self.created_at

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        version: None | str | Unset
        if isinstance(self.version, Unset):
            version = UNSET
        else:
            version = self.version

        meta: dict[str, Any] | None | Unset
        if isinstance(self.meta, Unset):
            meta = UNSET
        elif isinstance(self.meta, DocumentPublicMetaType0):
            meta = self.meta.to_dict()
        else:
            meta = self.meta

        external_url: None | str | Unset
        if isinstance(self.external_url, Unset):
            external_url = UNSET
        else:
            external_url = self.external_url

        object_key: None | str | Unset
        if isinstance(self.object_key, Unset):
            object_key = UNSET
        else:
            object_key = self.object_key

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

        file_content: None | str | Unset
        if isinstance(self.file_content, Unset):
            file_content = UNSET
        else:
            file_content = self.file_content

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "entity_id": entity_id,
            "context_type": context_type,
            "title": title,
            "mime_type": mime_type,
            "category": category,
            "sort_order": sort_order,
            "is_active": is_active,
            "is_public": is_public,
            "created_at": created_at,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if version is not UNSET:
            field_dict["version"] = version
        if meta is not UNSET:
            field_dict["meta"] = meta
        if external_url is not UNSET:
            field_dict["external_url"] = external_url
        if object_key is not UNSET:
            field_dict["object_key"] = object_key
        if filename is not UNSET:
            field_dict["filename"] = filename
        if filesize is not UNSET:
            field_dict["filesize"] = filesize
        if file_content is not UNSET:
            field_dict["file_content"] = file_content
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_public_meta_type_0 import DocumentPublicMetaType0
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        entity_id = UUID(d.pop("entity_id"))




        context_type = check_document_context_enum(d.pop("context_type"))




        title = d.pop("title")

        mime_type = check_mime_type_enum(d.pop("mime_type"))




        category = check_document_category_enum(d.pop("category"))




        sort_order = d.pop("sort_order")

        is_active = d.pop("is_active")

        is_public = d.pop("is_public")

        created_at = d.pop("created_at")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        version = _parse_version(d.pop("version", UNSET))


        def _parse_meta(data: object) -> DocumentPublicMetaType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                meta_type_0 = DocumentPublicMetaType0.from_dict(data)



                return meta_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentPublicMetaType0 | None | Unset, data)

        meta = _parse_meta(d.pop("meta", UNSET))


        def _parse_external_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_url = _parse_external_url(d.pop("external_url", UNSET))


        def _parse_object_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        object_key = _parse_object_key(d.pop("object_key", UNSET))


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


        def _parse_file_content(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        file_content = _parse_file_content(d.pop("file_content", UNSET))


        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))


        document_public = cls(
            id=id,
            entity_id=entity_id,
            context_type=context_type,
            title=title,
            mime_type=mime_type,
            category=category,
            sort_order=sort_order,
            is_active=is_active,
            is_public=is_public,
            created_at=created_at,
            description=description,
            version=version,
            meta=meta,
            external_url=external_url,
            object_key=object_key,
            filename=filename,
            filesize=filesize,
            file_content=file_content,
            updated_at=updated_at,
        )


        document_public.additional_properties = d
        return document_public

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
