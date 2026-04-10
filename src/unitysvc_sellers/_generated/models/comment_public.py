from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.comment_status_enum import check_comment_status_enum
from ..models.comment_status_enum import CommentStatusEnum
from ..models.comment_target_type_enum import check_comment_target_type_enum
from ..models.comment_target_type_enum import CommentTargetTypeEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="CommentPublic")



@_attrs_define
class CommentPublic:
    """ Public comment for API responses.

     """

    id: UUID
    target_type: CommentTargetTypeEnum
    """ Types of entities that can receive comments/reviews. """
    target_id: UUID
    content: str
    rating: int | None
    parent_id: None | UUID
    author_id: UUID
    author_name: str
    status: CommentStatusEnum
    """ Moderation status for comments. """
    upvotes: int
    downvotes: int
    reply_count: int
    created_at: datetime.datetime
    author_avatar_url: None | str | Unset = UNSET
    edited_at: datetime.datetime | None | Unset = UNSET
    replies: list[CommentPublic] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        target_type: str = self.target_type

        target_id = str(self.target_id)

        content = self.content

        rating: int | None
        rating = self.rating

        parent_id: None | str
        if isinstance(self.parent_id, UUID):
            parent_id = str(self.parent_id)
        else:
            parent_id = self.parent_id

        author_id = str(self.author_id)

        author_name = self.author_name

        status: str = self.status

        upvotes = self.upvotes

        downvotes = self.downvotes

        reply_count = self.reply_count

        created_at = self.created_at.isoformat()

        author_avatar_url: None | str | Unset
        if isinstance(self.author_avatar_url, Unset):
            author_avatar_url = UNSET
        else:
            author_avatar_url = self.author_avatar_url

        edited_at: None | str | Unset
        if isinstance(self.edited_at, Unset):
            edited_at = UNSET
        elif isinstance(self.edited_at, datetime.datetime):
            edited_at = self.edited_at.isoformat()
        else:
            edited_at = self.edited_at

        replies: list[dict[str, Any]] | None | Unset
        if isinstance(self.replies, Unset):
            replies = UNSET
        elif isinstance(self.replies, list):
            replies = []
            for replies_type_0_item_data in self.replies:
                replies_type_0_item = replies_type_0_item_data.to_dict()
                replies.append(replies_type_0_item)


        else:
            replies = self.replies


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "target_type": target_type,
            "target_id": target_id,
            "content": content,
            "rating": rating,
            "parent_id": parent_id,
            "author_id": author_id,
            "author_name": author_name,
            "status": status,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "reply_count": reply_count,
            "created_at": created_at,
        })
        if author_avatar_url is not UNSET:
            field_dict["author_avatar_url"] = author_avatar_url
        if edited_at is not UNSET:
            field_dict["edited_at"] = edited_at
        if replies is not UNSET:
            field_dict["replies"] = replies

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        target_type = check_comment_target_type_enum(d.pop("target_type"))




        target_id = UUID(d.pop("target_id"))




        content = d.pop("content")

        def _parse_rating(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        rating = _parse_rating(d.pop("rating"))


        def _parse_parent_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                parent_id_type_0 = UUID(data)



                return parent_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        parent_id = _parse_parent_id(d.pop("parent_id"))


        author_id = UUID(d.pop("author_id"))




        author_name = d.pop("author_name")

        status = check_comment_status_enum(d.pop("status"))




        upvotes = d.pop("upvotes")

        downvotes = d.pop("downvotes")

        reply_count = d.pop("reply_count")

        created_at = isoparse(d.pop("created_at"))




        def _parse_author_avatar_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        author_avatar_url = _parse_author_avatar_url(d.pop("author_avatar_url", UNSET))


        def _parse_edited_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                edited_at_type_0 = isoparse(data)



                return edited_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        edited_at = _parse_edited_at(d.pop("edited_at", UNSET))


        def _parse_replies(data: object) -> list[CommentPublic] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                replies_type_0 = []
                _replies_type_0 = data
                for replies_type_0_item_data in (_replies_type_0):
                    replies_type_0_item = CommentPublic.from_dict(replies_type_0_item_data)



                    replies_type_0.append(replies_type_0_item)

                return replies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[CommentPublic] | None | Unset, data)

        replies = _parse_replies(d.pop("replies", UNSET))


        comment_public = cls(
            id=id,
            target_type=target_type,
            target_id=target_id,
            content=content,
            rating=rating,
            parent_id=parent_id,
            author_id=author_id,
            author_name=author_name,
            status=status,
            upvotes=upvotes,
            downvotes=downvotes,
            reply_count=reply_count,
            created_at=created_at,
            author_avatar_url=author_avatar_url,
            edited_at=edited_at,
            replies=replies,
        )


        comment_public.additional_properties = d
        return comment_public

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
