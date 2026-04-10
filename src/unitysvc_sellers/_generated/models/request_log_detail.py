from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.gateway_request_info import GatewayRequestInfo
  from ..models.request_error_info import RequestErrorInfo
  from ..models.upstream_response_info import UpstreamResponseInfo
  from ..models.usage_event_info import UsageEventInfo
  from ..models.user_request_info import UserRequestInfo





T = TypeVar("T", bound="RequestLogDetail")



@_attrs_define
class RequestLogDetail:
    """ Full request log detail including bodies and headers.

     """

    log_id: str
    event_id: str
    event_timestamp: str
    gateway_source: str
    customer_id: str
    user_id: str
    user_request: UserRequestInfo
    """ User's original request details. """
    service_id: None | str | Unset = UNSET
    service_enrollment_id: None | str | Unset = UNSET
    gateway_request: GatewayRequestInfo | None | Unset = UNSET
    upstream_response: None | Unset | UpstreamResponseInfo = UNSET
    error: None | RequestErrorInfo | Unset = UNSET
    usage_event: None | Unset | UsageEventInfo = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.gateway_request_info import GatewayRequestInfo
        from ..models.request_error_info import RequestErrorInfo
        from ..models.upstream_response_info import UpstreamResponseInfo
        from ..models.usage_event_info import UsageEventInfo
        from ..models.user_request_info import UserRequestInfo
        log_id = self.log_id

        event_id = self.event_id

        event_timestamp = self.event_timestamp

        gateway_source = self.gateway_source

        customer_id = self.customer_id

        user_id = self.user_id

        user_request = self.user_request.to_dict()

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

        gateway_request: dict[str, Any] | None | Unset
        if isinstance(self.gateway_request, Unset):
            gateway_request = UNSET
        elif isinstance(self.gateway_request, GatewayRequestInfo):
            gateway_request = self.gateway_request.to_dict()
        else:
            gateway_request = self.gateway_request

        upstream_response: dict[str, Any] | None | Unset
        if isinstance(self.upstream_response, Unset):
            upstream_response = UNSET
        elif isinstance(self.upstream_response, UpstreamResponseInfo):
            upstream_response = self.upstream_response.to_dict()
        else:
            upstream_response = self.upstream_response

        error: dict[str, Any] | None | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        elif isinstance(self.error, RequestErrorInfo):
            error = self.error.to_dict()
        else:
            error = self.error

        usage_event: dict[str, Any] | None | Unset
        if isinstance(self.usage_event, Unset):
            usage_event = UNSET
        elif isinstance(self.usage_event, UsageEventInfo):
            usage_event = self.usage_event.to_dict()
        else:
            usage_event = self.usage_event


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "log_id": log_id,
            "event_id": event_id,
            "event_timestamp": event_timestamp,
            "gateway_source": gateway_source,
            "customer_id": customer_id,
            "user_id": user_id,
            "user_request": user_request,
        })
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if service_enrollment_id is not UNSET:
            field_dict["service_enrollment_id"] = service_enrollment_id
        if gateway_request is not UNSET:
            field_dict["gateway_request"] = gateway_request
        if upstream_response is not UNSET:
            field_dict["upstream_response"] = upstream_response
        if error is not UNSET:
            field_dict["error"] = error
        if usage_event is not UNSET:
            field_dict["usage_event"] = usage_event

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.gateway_request_info import GatewayRequestInfo
        from ..models.request_error_info import RequestErrorInfo
        from ..models.upstream_response_info import UpstreamResponseInfo
        from ..models.usage_event_info import UsageEventInfo
        from ..models.user_request_info import UserRequestInfo
        d = dict(src_dict)
        log_id = d.pop("log_id")

        event_id = d.pop("event_id")

        event_timestamp = d.pop("event_timestamp")

        gateway_source = d.pop("gateway_source")

        customer_id = d.pop("customer_id")

        user_id = d.pop("user_id")

        user_request = UserRequestInfo.from_dict(d.pop("user_request"))




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


        def _parse_gateway_request(data: object) -> GatewayRequestInfo | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                gateway_request_type_0 = GatewayRequestInfo.from_dict(data)



                return gateway_request_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GatewayRequestInfo | None | Unset, data)

        gateway_request = _parse_gateway_request(d.pop("gateway_request", UNSET))


        def _parse_upstream_response(data: object) -> None | Unset | UpstreamResponseInfo:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                upstream_response_type_0 = UpstreamResponseInfo.from_dict(data)



                return upstream_response_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpstreamResponseInfo, data)

        upstream_response = _parse_upstream_response(d.pop("upstream_response", UNSET))


        def _parse_error(data: object) -> None | RequestErrorInfo | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                error_type_0 = RequestErrorInfo.from_dict(data)



                return error_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RequestErrorInfo | Unset, data)

        error = _parse_error(d.pop("error", UNSET))


        def _parse_usage_event(data: object) -> None | Unset | UsageEventInfo:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                usage_event_type_0 = UsageEventInfo.from_dict(data)



                return usage_event_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UsageEventInfo, data)

        usage_event = _parse_usage_event(d.pop("usage_event", UNSET))


        request_log_detail = cls(
            log_id=log_id,
            event_id=event_id,
            event_timestamp=event_timestamp,
            gateway_source=gateway_source,
            customer_id=customer_id,
            user_id=user_id,
            user_request=user_request,
            service_id=service_id,
            service_enrollment_id=service_enrollment_id,
            gateway_request=gateway_request,
            upstream_response=upstream_response,
            error=error,
            usage_event=usage_event,
        )


        request_log_detail.additional_properties = d
        return request_log_detail

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
