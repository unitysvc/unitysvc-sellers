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
import datetime

if TYPE_CHECKING:
  from ..models.blog_post_create_meta_type_0 import BlogPostCreateMetaType0





T = TypeVar("T", bound="BlogPostCreate")



@_attrs_define
class BlogPostCreate:
    """ Schema for creating BlogPost.

     """

    title: str
    """ Blog post title """
    slug: str
    """ URL-friendly slug for the post """
    author_name: str
    """ Display name of the author """
    excerpt: None | str | Unset = UNSET
    """ Short preview/summary of the post """
    tags: list[str] | None | Unset = UNSET
    """ List of tags for categorization """
    status: BlogStatusEnum | Unset = UNSET
    """ Publication status of a blog post. """
    published_at: datetime.datetime | None | Unset = UNSET
    """ When the post was/will be published """
    meta: BlogPostCreateMetaType0 | None | Unset = UNSET
    """ Additional metadata (reading time, views, etc.) """
    content: None | str | Unset = UNSET
    """ Markdown content of the blog post """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.blog_post_create_meta_type_0 import BlogPostCreateMetaType0
        title = self.title

        slug = self.slug

        author_name = self.author_name

        excerpt: None | str | Unset
        if isinstance(self.excerpt, Unset):
            excerpt = UNSET
        else:
            excerpt = self.excerpt

        tags: list[str] | None | Unset
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags


        else:
            tags = self.tags

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status


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
        elif isinstance(self.meta, BlogPostCreateMetaType0):
            meta = self.meta.to_dict()
        else:
            meta = self.meta

        content: None | str | Unset
        if isinstance(self.content, Unset):
            content = UNSET
        else:
            content = self.content


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "title": title,
            "slug": slug,
            "author_name": author_name,
        })
        if excerpt is not UNSET:
            field_dict["excerpt"] = excerpt
        if tags is not UNSET:
            field_dict["tags"] = tags
        if status is not UNSET:
            field_dict["status"] = status
        if published_at is not UNSET:
            field_dict["published_at"] = published_at
        if meta is not UNSET:
            field_dict["meta"] = meta
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.blog_post_create_meta_type_0 import BlogPostCreateMetaType0
        d = dict(src_dict)
        title = d.pop("title")

        slug = d.pop("slug")

        author_name = d.pop("author_name")

        def _parse_excerpt(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        excerpt = _parse_excerpt(d.pop("excerpt", UNSET))


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


        _status = d.pop("status", UNSET)
        status: BlogStatusEnum | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_blog_status_enum(_status)




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


        def _parse_meta(data: object) -> BlogPostCreateMetaType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                meta_type_0 = BlogPostCreateMetaType0.from_dict(data)



                return meta_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BlogPostCreateMetaType0 | None | Unset, data)

        meta = _parse_meta(d.pop("meta", UNSET))


        def _parse_content(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        content = _parse_content(d.pop("content", UNSET))


        blog_post_create = cls(
            title=title,
            slug=slug,
            author_name=author_name,
            excerpt=excerpt,
            tags=tags,
            status=status,
            published_at=published_at,
            meta=meta,
            content=content,
        )


        blog_post_create.additional_properties = d
        return blog_post_create

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
