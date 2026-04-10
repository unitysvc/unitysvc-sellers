from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.comment_public import CommentPublic
  from ..models.comments_public_rating_distribution_type_0 import CommentsPublicRatingDistributionType0





T = TypeVar("T", bound="CommentsPublic")



@_attrs_define
class CommentsPublic:
    """ Paginated list of comments.

     """

    data: list[CommentPublic]
    count: int
    average_rating: float | None | Unset = UNSET
    rating_distribution: CommentsPublicRatingDistributionType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.comment_public import CommentPublic
        from ..models.comments_public_rating_distribution_type_0 import CommentsPublicRatingDistributionType0
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)



        count = self.count

        average_rating: float | None | Unset
        if isinstance(self.average_rating, Unset):
            average_rating = UNSET
        else:
            average_rating = self.average_rating

        rating_distribution: dict[str, Any] | None | Unset
        if isinstance(self.rating_distribution, Unset):
            rating_distribution = UNSET
        elif isinstance(self.rating_distribution, CommentsPublicRatingDistributionType0):
            rating_distribution = self.rating_distribution.to_dict()
        else:
            rating_distribution = self.rating_distribution


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "data": data,
            "count": count,
        })
        if average_rating is not UNSET:
            field_dict["average_rating"] = average_rating
        if rating_distribution is not UNSET:
            field_dict["rating_distribution"] = rating_distribution

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.comment_public import CommentPublic
        from ..models.comments_public_rating_distribution_type_0 import CommentsPublicRatingDistributionType0
        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in (_data):
            data_item = CommentPublic.from_dict(data_item_data)



            data.append(data_item)


        count = d.pop("count")

        def _parse_average_rating(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        average_rating = _parse_average_rating(d.pop("average_rating", UNSET))


        def _parse_rating_distribution(data: object) -> CommentsPublicRatingDistributionType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rating_distribution_type_0 = CommentsPublicRatingDistributionType0.from_dict(data)



                return rating_distribution_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CommentsPublicRatingDistributionType0 | None | Unset, data)

        rating_distribution = _parse_rating_distribution(d.pop("rating_distribution", UNSET))


        comments_public = cls(
            data=data,
            count=count,
            average_rating=average_rating,
            rating_distribution=rating_distribution,
        )


        comments_public.additional_properties = d
        return comments_public

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
