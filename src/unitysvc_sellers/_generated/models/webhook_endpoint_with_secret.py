from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.webhook_endpoint_status import WebhookEndpointStatus, check_webhook_endpoint_status

T = TypeVar("T", bound="WebhookEndpointWithSecret")


@_attrs_define
class WebhookEndpointWithSecret:
    """Returned only by create and roll-secret: the one time the secret is shown."""

    id: UUID
    url: str
    description: None | str
    enabled_events: list[str]
    status: WebhookEndpointStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime
    secret: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        url = self.url

        description: None | str
        description = self.description

        enabled_events = self.enabled_events

        status: str = self.status

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        secret = self.secret

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "url": url,
                "description": description,
                "enabled_events": enabled_events,
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
                "secret": secret,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        url = d.pop("url")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        enabled_events = cast(list[str], d.pop("enabled_events"))

        status = check_webhook_endpoint_status(d.pop("status"))

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        secret = d.pop("secret")

        webhook_endpoint_with_secret = cls(
            id=id,
            url=url,
            description=description,
            enabled_events=enabled_events,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            secret=secret,
        )

        webhook_endpoint_with_secret.additional_properties = d
        return webhook_endpoint_with_secret

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
