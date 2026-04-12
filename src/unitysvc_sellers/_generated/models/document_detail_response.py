from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.document_detail_response_meta_type_0 import DocumentDetailResponseMetaType0





T = TypeVar("T", bound="DocumentDetailResponse")



@_attrs_define
class DocumentDetailResponse:
    """ GET /seller/documents/{id} — full document including file content.

    The prior behaviour was file_content=false by default; this response
    always includes file_content for predictable codegen.

     """

    id: str
    entity_id: str
    context_type: str
    title: str
    is_active: bool
    is_public: bool
    description: Union[None, Unset, str] = UNSET
    mime_type: Union[None, Unset, str] = UNSET
    category: Union[None, Unset, str] = UNSET
    filename: Union[None, Unset, str] = UNSET
    filesize: Union[None, Unset, int] = UNSET
    meta: Union['DocumentDetailResponseMetaType0', None, Unset] = UNSET
    file_content: Union[None, Unset, str] = UNSET
    created_at: Union[None, Unset, str] = UNSET
    updated_at: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.document_detail_response_meta_type_0 import DocumentDetailResponseMetaType0
        id = self.id

        entity_id = self.entity_id

        context_type = self.context_type

        title = self.title

        is_active = self.is_active

        is_public = self.is_public

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        mime_type: Union[None, Unset, str]
        if isinstance(self.mime_type, Unset):
            mime_type = UNSET
        else:
            mime_type = self.mime_type

        category: Union[None, Unset, str]
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        filename: Union[None, Unset, str]
        if isinstance(self.filename, Unset):
            filename = UNSET
        else:
            filename = self.filename

        filesize: Union[None, Unset, int]
        if isinstance(self.filesize, Unset):
            filesize = UNSET
        else:
            filesize = self.filesize

        meta: Union[None, Unset, dict[str, Any]]
        if isinstance(self.meta, Unset):
            meta = UNSET
        elif isinstance(self.meta, DocumentDetailResponseMetaType0):
            meta = self.meta.to_dict()
        else:
            meta = self.meta

        file_content: Union[None, Unset, str]
        if isinstance(self.file_content, Unset):
            file_content = UNSET
        else:
            file_content = self.file_content

        created_at: Union[None, Unset, str]
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        updated_at: Union[None, Unset, str]
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
            "is_active": is_active,
            "is_public": is_public,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if mime_type is not UNSET:
            field_dict["mime_type"] = mime_type
        if category is not UNSET:
            field_dict["category"] = category
        if filename is not UNSET:
            field_dict["filename"] = filename
        if filesize is not UNSET:
            field_dict["filesize"] = filesize
        if meta is not UNSET:
            field_dict["meta"] = meta
        if file_content is not UNSET:
            field_dict["file_content"] = file_content
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_detail_response_meta_type_0 import DocumentDetailResponseMetaType0
        d = dict(src_dict)
        id = d.pop("id")

        entity_id = d.pop("entity_id")

        context_type = d.pop("context_type")

        title = d.pop("title")

        is_active = d.pop("is_active")

        is_public = d.pop("is_public")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_mime_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        mime_type = _parse_mime_type(d.pop("mime_type", UNSET))


        def _parse_category(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        category = _parse_category(d.pop("category", UNSET))


        def _parse_filename(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        filename = _parse_filename(d.pop("filename", UNSET))


        def _parse_filesize(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        filesize = _parse_filesize(d.pop("filesize", UNSET))


        def _parse_meta(data: object) -> Union['DocumentDetailResponseMetaType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                meta_type_0 = DocumentDetailResponseMetaType0.from_dict(data)



                return meta_type_0
            except: # noqa: E722
                pass
            return cast(Union['DocumentDetailResponseMetaType0', None, Unset], data)

        meta = _parse_meta(d.pop("meta", UNSET))


        def _parse_file_content(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        file_content = _parse_file_content(d.pop("file_content", UNSET))


        def _parse_created_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))


        def _parse_updated_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))


        document_detail_response = cls(
            id=id,
            entity_id=entity_id,
            context_type=context_type,
            title=title,
            is_active=is_active,
            is_public=is_public,
            description=description,
            mime_type=mime_type,
            category=category,
            filename=filename,
            filesize=filesize,
            meta=meta,
            file_content=file_content,
            created_at=created_at,
            updated_at=updated_at,
        )


        document_detail_response.additional_properties = d
        return document_detail_response

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
