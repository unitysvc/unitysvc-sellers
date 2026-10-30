from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.webhook_event_status import WebhookEventStatus, check_webhook_event_status

if TYPE_CHECKING:
    from ..models.webhook_event_public_data import WebhookEventPublicData
    from ..models.webhook_event_public_results import WebhookEventPublicResults


T = TypeVar("T", bound="WebhookEventPublic")


@_attrs_define
class WebhookEventPublic:
    id: UUID
    type_: str
    created_at: datetime.datetime
    data: WebhookEventPublicData
    endpoint_id: None | UUID
    status: WebhookEventStatus
    resent_at: datetime.datetime | None
    attempts: int
    last_attempt_at: datetime.datetime | None
    last_error: None | str
    results: WebhookEventPublicResults
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        type_ = self.type_

        created_at = self.created_at.isoformat()

        data = self.data.to_dict()

        endpoint_id: None | str
        if isinstance(self.endpoint_id, UUID):
            endpoint_id = str(self.endpoint_id)
        else:
            endpoint_id = self.endpoint_id

        status: str = self.status

        resent_at: None | str
        if isinstance(self.resent_at, datetime.datetime):
            resent_at = self.resent_at.isoformat()
        else:
            resent_at = self.resent_at

        attempts = self.attempts

        last_attempt_at: None | str
        if isinstance(self.last_attempt_at, datetime.datetime):
            last_attempt_at = self.last_attempt_at.isoformat()
        else:
            last_attempt_at = self.last_attempt_at

        last_error: None | str
        last_error = self.last_error

        results = self.results.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "created_at": created_at,
                "data": data,
                "endpoint_id": endpoint_id,
                "status": status,
                "resent_at": resent_at,
                "attempts": attempts,
                "last_attempt_at": last_attempt_at,
                "last_error": last_error,
                "results": results,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.webhook_event_public_data import WebhookEventPublicData
        from ..models.webhook_event_public_results import WebhookEventPublicResults

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        type_ = d.pop("type")

        created_at = isoparse(d.pop("created_at"))

        data = WebhookEventPublicData.from_dict(d.pop("data"))

        def _parse_endpoint_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                endpoint_id_type_0 = UUID(data)

                return endpoint_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        endpoint_id = _parse_endpoint_id(d.pop("endpoint_id"))

        status = check_webhook_event_status(d.pop("status"))

        def _parse_resent_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                resent_at_type_0 = isoparse(data)

                return resent_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        resent_at = _parse_resent_at(d.pop("resent_at"))

        attempts = d.pop("attempts")

        def _parse_last_attempt_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_attempt_at_type_0 = isoparse(data)

                return last_attempt_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        last_attempt_at = _parse_last_attempt_at(d.pop("last_attempt_at"))

        def _parse_last_error(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_error = _parse_last_error(d.pop("last_error"))

        results = WebhookEventPublicResults.from_dict(d.pop("results"))

        webhook_event_public = cls(
            id=id,
            type_=type_,
            created_at=created_at,
            data=data,
            endpoint_id=endpoint_id,
            status=status,
            resent_at=resent_at,
            attempts=attempts,
            last_attempt_at=last_attempt_at,
            last_error=last_error,
            results=results,
        )

        webhook_event_public.additional_properties = d
        return webhook_event_public

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
