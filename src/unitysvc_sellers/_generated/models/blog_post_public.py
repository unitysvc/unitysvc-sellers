from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.blog_status_enum import BlogStatusEnum
from ..models.blog_status_enum import check_blog_status_enum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.blog_post_public_meta_type_0 import BlogPostPublicMetaType0





T = TypeVar("T", bound="BlogPostPublic")



@_attrs_define
class BlogPostPublic:
    """ Public BlogPost model for API responses.

     """

    id: UUID
    title: str
    slug: str
    author_name: str
    status: BlogStatusEnum
    """ Publication status of a blog post. """
    created_at: datetime.datetime
    excerpt: None | str | Unset = UNSET
    cover_image_url: None | str | Unset = UNSET
    tags: list[str] | None | Unset = UNSET
    published_at: datetime.datetime | None | Unset = UNSET
    meta: BlogPostPublicMetaType0 | None | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    content: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.blog_post_public_meta_type_0 import BlogPostPublicMetaType0
        id = str(self.id)

        title = self.title

        slug = self.slug

        author_name = self.author_name

        status: str = self.status

        created_at = self.created_at.isoformat()

        excerpt: None | str | Unset
        if isinstance(self.excerpt, Unset):
            excerpt = UNSET
        else:
            excerpt = self.excerpt

        cover_image_url: None | str | Unset
        if isinstance(self.cover_image_url, Unset):
            cover_image_url = UNSET
        else:
            cover_image_url = self.cover_image_url

        tags: list[str] | None | Unset
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags


        else:
            tags = self.tags

        published_at: None | str | Unset
        if isinstance(self.published_at, Unset):
            published_at = UNSET
        elif isinstance(self.published_at, datetime.datetime):
            published_at = self.published_at.isoformat()
        else:
            published_at = self.published_at

        meta: dict[str, Any] | None | Unset
        if isinstance(self.meta, Unset):
            meta = UNSET
        elif isinstance(self.meta, BlogPostPublicMetaType0):
            meta = self.meta.to_dict()
        else:
            meta = self.meta

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        content: None | str | Unset
        if isinstance(self.content, Unset):
            content = UNSET
        else:
            content = self.content


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "title": title,
            "slug": slug,
            "author_name": author_name,
            "status": status,
            "created_at": created_at,
        })
        if excerpt is not UNSET:
            field_dict["excerpt"] = excerpt
        if cover_image_url is not UNSET:
            field_dict["cover_image_url"] = cover_image_url
        if tags is not UNSET:
            field_dict["tags"] = tags
        if published_at is not UNSET:
            field_dict["published_at"] = published_at
        if meta is not UNSET:
            field_dict["meta"] = meta
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.blog_post_public_meta_type_0 import BlogPostPublicMetaType0
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        title = d.pop("title")

        slug = d.pop("slug")

        author_name = d.pop("author_name")

        status = check_blog_status_enum(d.pop("status"))




        created_at = isoparse(d.pop("created_at"))




        def _parse_excerpt(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        excerpt = _parse_excerpt(d.pop("excerpt", UNSET))


        def _parse_cover_image_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cover_image_url = _parse_cover_image_url(d.pop("cover_image_url", UNSET))


        def _parse_tags(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = cast(list[str], data)

                return tags_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        tags = _parse_tags(d.pop("tags", UNSET))


        def _parse_published_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                published_at_type_0 = isoparse(data)



                return published_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        published_at = _parse_published_at(d.pop("published_at", UNSET))


        def _parse_meta(data: object) -> BlogPostPublicMetaType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                meta_type_0 = BlogPostPublicMetaType0.from_dict(data)



                return meta_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BlogPostPublicMetaType0 | None | Unset, data)

        meta = _parse_meta(d.pop("meta", UNSET))


        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)



                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))


        def _parse_content(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        content = _parse_content(d.pop("content", UNSET))


        blog_post_public = cls(
            id=id,
            title=title,
            slug=slug,
            author_name=author_name,
            status=status,
            created_at=created_at,
            excerpt=excerpt,
            cover_image_url=cover_image_url,
            tags=tags,
            published_at=published_at,
            meta=meta,
            updated_at=updated_at,
            content=content,
        )


        blog_post_public.additional_properties = d
        return blog_post_public

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
