from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.upstream_response_info_headers_type_0 import UpstreamResponseInfoHeadersType0





T = TypeVar("T", bound="UpstreamResponseInfo")



@_attrs_define
class UpstreamResponseInfo:
    """ Response received from the upstream service.

     """

    status_code: int
    headers: None | Unset | UpstreamResponseInfoHeadersType0 = UNSET
    body: Any | Unset = UNSET
    time_ms: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.upstream_response_info_headers_type_0 import UpstreamResponseInfoHeadersType0
        status_code = self.status_code

        headers: dict[str, Any] | None | Unset
        if isinstance(self.headers, Unset):
            headers = UNSET
        elif isinstance(self.headers, UpstreamResponseInfoHeadersType0):
            headers = self.headers.to_dict()
        else:
            headers = self.headers

        body = self.body

        time_ms: float | None | Unset
        if isinstance(self.time_ms, Unset):
            time_ms = UNSET
        else:
            time_ms = self.time_ms


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "status_code": status_code,
        })
        if headers is not UNSET:
            field_dict["headers"] = headers
        if body is not UNSET:
            field_dict["body"] = body
        if time_ms is not UNSET:
            field_dict["time_ms"] = time_ms

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.upstream_response_info_headers_type_0 import UpstreamResponseInfoHeadersType0
        d = dict(src_dict)
        status_code = d.pop("status_code")

        def _parse_headers(data: object) -> None | Unset | UpstreamResponseInfoHeadersType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                headers_type_0 = UpstreamResponseInfoHeadersType0.from_dict(data)



                return headers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpstreamResponseInfoHeadersType0, data)

        headers = _parse_headers(d.pop("headers", UNSET))


        body = d.pop("body", UNSET)

        def _parse_time_ms(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        time_ms = _parse_time_ms(d.pop("time_ms", UNSET))


        upstream_response_info = cls(
            status_code=status_code,
            headers=headers,
            body=body,
            time_ms=time_ms,
        )


        upstream_response_info.additional_properties = d
        return upstream_response_info

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
