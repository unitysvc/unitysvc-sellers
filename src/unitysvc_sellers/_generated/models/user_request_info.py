from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.user_request_info_headers_type_0 import UserRequestInfoHeadersType0





T = TypeVar("T", bound="UserRequestInfo")



@_attrs_define
class UserRequestInfo:
    """ User's original request details.

     """

    method: str
    path: str
    content_type: str
    headers: None | Unset | UserRequestInfoHeadersType0 = UNSET
    body: Any | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.user_request_info_headers_type_0 import UserRequestInfoHeadersType0
        method = self.method

        path = self.path

        content_type = self.content_type

        headers: dict[str, Any] | None | Unset
        if isinstance(self.headers, Unset):
            headers = UNSET
        elif isinstance(self.headers, UserRequestInfoHeadersType0):
            headers = self.headers.to_dict()
        else:
            headers = self.headers

        body = self.body


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "method": method,
            "path": path,
            "content_type": content_type,
        })
        if headers is not UNSET:
            field_dict["headers"] = headers
        if body is not UNSET:
            field_dict["body"] = body

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_request_info_headers_type_0 import UserRequestInfoHeadersType0
        d = dict(src_dict)
        method = d.pop("method")

        path = d.pop("path")

        content_type = d.pop("content_type")

        def _parse_headers(data: object) -> None | Unset | UserRequestInfoHeadersType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                headers_type_0 = UserRequestInfoHeadersType0.from_dict(data)



                return headers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UserRequestInfoHeadersType0, data)

        headers = _parse_headers(d.pop("headers", UNSET))


        body = d.pop("body", UNSET)

        user_request_info = cls(
            method=method,
            path=path,
            content_type=content_type,
            headers=headers,
            body=body,
        )


        user_request_info.additional_properties = d
        return user_request_info

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
