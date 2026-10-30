from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.webhook_endpoint_status import WebhookEndpointStatus, check_webhook_endpoint_status
from ..types import UNSET, Unset

T = TypeVar("T", bound="WebhookEndpointUpdate")


@_attrs_define
class WebhookEndpointUpdate:
    url: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    enabled_events: list[str] | None | Unset = UNSET
    status: None | Unset | WebhookEndpointStatus = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        enabled_events: list[str] | None | Unset
        if isinstance(self.enabled_events, Unset):
            enabled_events = UNSET
        elif isinstance(self.enabled_events, list):
            enabled_events = self.enabled_events

        else:
            enabled_events = self.enabled_events

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, str):
            status = self.status
        else:
            status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if description is not UNSET:
            field_dict["description"] = description
        if enabled_events is not UNSET:
            field_dict["enabled_events"] = enabled_events
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_enabled_events(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                enabled_events_type_0 = cast(list[str], data)

                return enabled_events_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        enabled_events = _parse_enabled_events(d.pop("enabled_events", UNSET))

        def _parse_status(data: object) -> None | Unset | WebhookEndpointStatus:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = check_webhook_endpoint_status(data)

                return status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | WebhookEndpointStatus, data)

        status = _parse_status(d.pop("status", UNSET))

        webhook_endpoint_update = cls(
            url=url,
            description=description,
            enabled_events=enabled_events,
            status=status,
        )

        webhook_endpoint_update.additional_properties = d
        return webhook_endpoint_update

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
