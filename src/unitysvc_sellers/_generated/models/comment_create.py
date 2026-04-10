from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.comment_target_type_enum import check_comment_target_type_enum
from ..models.comment_target_type_enum import CommentTargetTypeEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID






T = TypeVar("T", bound="CommentCreate")



@_attrs_define
class CommentCreate:
    """ Schema for creating a comment or review.

     """

    target_type: CommentTargetTypeEnum
    """ Types of entities that can receive comments/reviews. """
    target_id: UUID
    content: str
    rating: int | None | Unset = UNSET
    parent_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        target_type: str = self.target_type

        target_id = str(self.target_id)

        content = self.content

        rating: int | None | Unset
        if isinstance(self.rating, Unset):
            rating = UNSET
        else:
            rating = self.rating

        parent_id: None | str | Unset
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        elif isinstance(self.parent_id, UUID):
            parent_id = str(self.parent_id)
        else:
            parent_id = self.parent_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "target_type": target_type,
            "target_id": target_id,
            "content": content,
        })
        if rating is not UNSET:
            field_dict["rating"] = rating
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        target_type = check_comment_target_type_enum(d.pop("target_type"))




        target_id = UUID(d.pop("target_id"))




        content = d.pop("content")

        def _parse_rating(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        rating = _parse_rating(d.pop("rating", UNSET))


        def _parse_parent_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                parent_id_type_0 = UUID(data)



                return parent_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        parent_id = _parse_parent_id(d.pop("parent_id", UNSET))


        comment_create = cls(
            target_type=target_type,
            target_id=target_id,
            content=content,
            rating=rating,
            parent_id=parent_id,
        )


        comment_create.additional_properties = d
        return comment_create

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
