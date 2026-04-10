from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.request_log_list_item import RequestLogListItem





T = TypeVar("T", bound="RequestLogListResponse")



@_attrs_define
class RequestLogListResponse:
    """ Paginated list of request log items.

     """

    total_count: int
    skip: int
    limit: int
    items: list[RequestLogListItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.request_log_list_item import RequestLogListItem
        total_count = self.total_count

        skip = self.skip

        limit = self.limit

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "items": items,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.request_log_list_item import RequestLogListItem
        d = dict(src_dict)
        total_count = d.pop("total_count")

        skip = d.pop("skip")

        limit = d.pop("limit")

        items = []
        _items = d.pop("items")
        for items_item_data in (_items):
            items_item = RequestLogListItem.from_dict(items_item_data)



            items.append(items_item)


        request_log_list_response = cls(
            total_count=total_count,
            skip=skip,
            limit=limit,
            items=items,
        )


        request_log_list_response.additional_properties = d
        return request_log_list_response

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
