from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="RequestLogListItem")



@_attrs_define
class RequestLogListItem:
    """ Lightweight request log item for list/pagination views.

     """

    log_id: str
    event_id: str
    event_timestamp: str
    gateway_source: str
    user_request_method: str
    user_request_path: str
    customer_id: None | str | Unset = UNSET
    service_id: None | str | Unset = UNSET
    service_enrollment_id: None | str | Unset = UNSET
    upstream_response_status_code: int | None | Unset = UNSET
    upstream_response_time_ms: float | None | Unset = UNSET
    error_source: None | str | Unset = UNSET
    error_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        log_id = self.log_id

        event_id = self.event_id

        event_timestamp = self.event_timestamp

        gateway_source = self.gateway_source

        user_request_method = self.user_request_method

        user_request_path = self.user_request_path

        customer_id: None | str | Unset
        if isinstance(self.customer_id, Unset):
            customer_id = UNSET
        else:
            customer_id = self.customer_id

        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        else:
            service_id = self.service_id

        service_enrollment_id: None | str | Unset
        if isinstance(self.service_enrollment_id, Unset):
            service_enrollment_id = UNSET
        else:
            service_enrollment_id = self.service_enrollment_id

        upstream_response_status_code: int | None | Unset
        if isinstance(self.upstream_response_status_code, Unset):
            upstream_response_status_code = UNSET
        else:
            upstream_response_status_code = self.upstream_response_status_code

        upstream_response_time_ms: float | None | Unset
        if isinstance(self.upstream_response_time_ms, Unset):
            upstream_response_time_ms = UNSET
        else:
            upstream_response_time_ms = self.upstream_response_time_ms

        error_source: None | str | Unset
        if isinstance(self.error_source, Unset):
            error_source = UNSET
        else:
            error_source = self.error_source

        error_type: None | str | Unset
        if isinstance(self.error_type, Unset):
            error_type = UNSET
        else:
            error_type = self.error_type


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "log_id": log_id,
            "event_id": event_id,
            "event_timestamp": event_timestamp,
            "gateway_source": gateway_source,
            "user_request_method": user_request_method,
            "user_request_path": user_request_path,
        })
        if customer_id is not UNSET:
            field_dict["customer_id"] = customer_id
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if service_enrollment_id is not UNSET:
            field_dict["service_enrollment_id"] = service_enrollment_id
        if upstream_response_status_code is not UNSET:
            field_dict["upstream_response_status_code"] = upstream_response_status_code
        if upstream_response_time_ms is not UNSET:
            field_dict["upstream_response_time_ms"] = upstream_response_time_ms
        if error_source is not UNSET:
            field_dict["error_source"] = error_source
        if error_type is not UNSET:
            field_dict["error_type"] = error_type

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        log_id = d.pop("log_id")

        event_id = d.pop("event_id")

        event_timestamp = d.pop("event_timestamp")

        gateway_source = d.pop("gateway_source")

        user_request_method = d.pop("user_request_method")

        user_request_path = d.pop("user_request_path")

        def _parse_customer_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        customer_id = _parse_customer_id(d.pop("customer_id", UNSET))


        def _parse_service_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        service_id = _parse_service_id(d.pop("service_id", UNSET))


        def _parse_service_enrollment_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        service_enrollment_id = _parse_service_enrollment_id(d.pop("service_enrollment_id", UNSET))


        def _parse_upstream_response_status_code(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        upstream_response_status_code = _parse_upstream_response_status_code(d.pop("upstream_response_status_code", UNSET))


        def _parse_upstream_response_time_ms(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        upstream_response_time_ms = _parse_upstream_response_time_ms(d.pop("upstream_response_time_ms", UNSET))


        def _parse_error_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_source = _parse_error_source(d.pop("error_source", UNSET))


        def _parse_error_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_type = _parse_error_type(d.pop("error_type", UNSET))


        request_log_list_item = cls(
            log_id=log_id,
            event_id=event_id,
            event_timestamp=event_timestamp,
            gateway_source=gateway_source,
            user_request_method=user_request_method,
            user_request_path=user_request_path,
            customer_id=customer_id,
            service_id=service_id,
            service_enrollment_id=service_enrollment_id,
            upstream_response_status_code=upstream_response_status_code,
            upstream_response_time_ms=upstream_response_time_ms,
            error_source=error_source,
            error_type=error_type,
        )


        request_log_list_item.additional_properties = d
        return request_log_list_item

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
