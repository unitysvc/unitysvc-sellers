from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.account_file_object import AccountFileObject


T = TypeVar("T", bound="SellerFilesListResponse")


@_attrs_define
class SellerFilesListResponse:
    """One page of a seller account-files listing."""

    path: str
    objects: list[AccountFileObject]
    common_prefixes: list[str]
    is_truncated: bool
    next_continuation_token: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.account_file_object import AccountFileObject

        path = self.path

        objects = []
        for objects_item_data in self.objects:
            objects_item = objects_item_data.to_dict()
            objects.append(objects_item)

        common_prefixes = self.common_prefixes

        is_truncated = self.is_truncated

        next_continuation_token: None | str
        next_continuation_token = self.next_continuation_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "objects": objects,
                "common_prefixes": common_prefixes,
                "is_truncated": is_truncated,
                "next_continuation_token": next_continuation_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.account_file_object import AccountFileObject

        d = dict(src_dict)
        path = d.pop("path")

        objects = []
        _objects = d.pop("objects")
        for objects_item_data in _objects:
            objects_item = AccountFileObject.from_dict(objects_item_data)

            objects.append(objects_item)

        common_prefixes = cast(list[str], d.pop("common_prefixes"))

        is_truncated = d.pop("is_truncated")

        def _parse_next_continuation_token(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_continuation_token = _parse_next_continuation_token(d.pop("next_continuation_token"))

        seller_files_list_response = cls(
            path=path,
            objects=objects,
            common_prefixes=common_prefixes,
            is_truncated=is_truncated,
            next_continuation_token=next_continuation_token,
        )

        seller_files_list_response.additional_properties = d
        return seller_files_list_response

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
