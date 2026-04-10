from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.audit_log_event_type import AuditLogEventType
from ..models.audit_log_event_type import check_audit_log_event_type
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.audit_log_public_event_metadata_type_0 import AuditLogPublicEventMetadataType0
  from ..models.audit_log_public_new_value_type_0 import AuditLogPublicNewValueType0
  from ..models.audit_log_public_old_value_type_0 import AuditLogPublicOldValueType0





T = TypeVar("T", bound="AuditLogPublic")



@_attrs_define
class AuditLogPublic:
    """ Public audit log entry for API responses.

     """

    event_type: AuditLogEventType
    """ Types of auditable events in the system. """
    event_timestamp: datetime.datetime
    """ When the event occurred (may differ from created_at) """
    resource_type: str
    """ Type of resource: customer, wallet, api_key, etc. """
    id: UUID
    created_at: datetime.datetime
    user_id: None | Unset | UUID = UNSET
    """ User who triggered this event (if applicable) """
    customer_id: None | Unset | UUID = UNSET
    """ Customer affected by this event (if applicable) """
    system_initiated: bool | Unset = False
    """ True if this was an automated system action """
    resource_id: None | Unset | UUID = UNSET
    """ ID of the affected resource """
    old_value: AuditLogPublicOldValueType0 | None | Unset = UNSET
    """ Previous state (for update operations) """
    new_value: AuditLogPublicNewValueType0 | None | Unset = UNSET
    """ New state (for create/update operations) """
    reason: None | str | Unset = UNSET
    """ Human-readable reason for this event """
    event_metadata: AuditLogPublicEventMetadataType0 | None | Unset = UNSET
    """ Additional context (payment stats, request details, etc.) """
    ip_address: None | str | Unset = UNSET
    """ IP address of the actor (if applicable) """
    user_agent: None | str | Unset = UNSET
    """ User agent string (for API requests) """





    def to_dict(self) -> dict[str, Any]:
        from ..models.audit_log_public_event_metadata_type_0 import AuditLogPublicEventMetadataType0
        from ..models.audit_log_public_new_value_type_0 import AuditLogPublicNewValueType0
        from ..models.audit_log_public_old_value_type_0 import AuditLogPublicOldValueType0
        event_type: str = self.event_type

        event_timestamp = self.event_timestamp.isoformat()

        resource_type = self.resource_type

        id = str(self.id)

        created_at = self.created_at.isoformat()

        user_id: None | str | Unset
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        elif isinstance(self.user_id, UUID):
            user_id = str(self.user_id)
        else:
            user_id = self.user_id

        customer_id: None | str | Unset
        if isinstance(self.customer_id, Unset):
            customer_id = UNSET
        elif isinstance(self.customer_id, UUID):
            customer_id = str(self.customer_id)
        else:
            customer_id = self.customer_id

        system_initiated = self.system_initiated

        resource_id: None | str | Unset
        if isinstance(self.resource_id, Unset):
            resource_id = UNSET
        elif isinstance(self.resource_id, UUID):
            resource_id = str(self.resource_id)
        else:
            resource_id = self.resource_id

        old_value: dict[str, Any] | None | Unset
        if isinstance(self.old_value, Unset):
            old_value = UNSET
        elif isinstance(self.old_value, AuditLogPublicOldValueType0):
            old_value = self.old_value.to_dict()
        else:
            old_value = self.old_value

        new_value: dict[str, Any] | None | Unset
        if isinstance(self.new_value, Unset):
            new_value = UNSET
        elif isinstance(self.new_value, AuditLogPublicNewValueType0):
            new_value = self.new_value.to_dict()
        else:
            new_value = self.new_value

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        event_metadata: dict[str, Any] | None | Unset
        if isinstance(self.event_metadata, Unset):
            event_metadata = UNSET
        elif isinstance(self.event_metadata, AuditLogPublicEventMetadataType0):
            event_metadata = self.event_metadata.to_dict()
        else:
            event_metadata = self.event_metadata

        ip_address: None | str | Unset
        if isinstance(self.ip_address, Unset):
            ip_address = UNSET
        else:
            ip_address = self.ip_address

        user_agent: None | str | Unset
        if isinstance(self.user_agent, Unset):
            user_agent = UNSET
        else:
            user_agent = self.user_agent


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "event_type": event_type,
            "event_timestamp": event_timestamp,
            "resource_type": resource_type,
            "id": id,
            "created_at": created_at,
        })
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if customer_id is not UNSET:
            field_dict["customer_id"] = customer_id
        if system_initiated is not UNSET:
            field_dict["system_initiated"] = system_initiated
        if resource_id is not UNSET:
            field_dict["resource_id"] = resource_id
        if old_value is not UNSET:
            field_dict["old_value"] = old_value
        if new_value is not UNSET:
            field_dict["new_value"] = new_value
        if reason is not UNSET:
            field_dict["reason"] = reason
        if event_metadata is not UNSET:
            field_dict["event_metadata"] = event_metadata
        if ip_address is not UNSET:
            field_dict["ip_address"] = ip_address
        if user_agent is not UNSET:
            field_dict["user_agent"] = user_agent

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audit_log_public_event_metadata_type_0 import AuditLogPublicEventMetadataType0
        from ..models.audit_log_public_new_value_type_0 import AuditLogPublicNewValueType0
        from ..models.audit_log_public_old_value_type_0 import AuditLogPublicOldValueType0
        d = dict(src_dict)
        event_type = check_audit_log_event_type(d.pop("event_type"))




        event_timestamp = isoparse(d.pop("event_timestamp"))




        resource_type = d.pop("resource_type")

        id = UUID(d.pop("id"))




        created_at = isoparse(d.pop("created_at"))




        def _parse_user_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                user_id_type_0 = UUID(data)



                return user_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        user_id = _parse_user_id(d.pop("user_id", UNSET))


        def _parse_customer_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                customer_id_type_0 = UUID(data)



                return customer_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        customer_id = _parse_customer_id(d.pop("customer_id", UNSET))


        system_initiated = d.pop("system_initiated", UNSET)

        def _parse_resource_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                resource_id_type_0 = UUID(data)



                return resource_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        resource_id = _parse_resource_id(d.pop("resource_id", UNSET))


        def _parse_old_value(data: object) -> AuditLogPublicOldValueType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                old_value_type_0 = AuditLogPublicOldValueType0.from_dict(data)



                return old_value_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuditLogPublicOldValueType0 | None | Unset, data)

        old_value = _parse_old_value(d.pop("old_value", UNSET))


        def _parse_new_value(data: object) -> AuditLogPublicNewValueType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                new_value_type_0 = AuditLogPublicNewValueType0.from_dict(data)



                return new_value_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuditLogPublicNewValueType0 | None | Unset, data)

        new_value = _parse_new_value(d.pop("new_value", UNSET))


        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))


        def _parse_event_metadata(data: object) -> AuditLogPublicEventMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                event_metadata_type_0 = AuditLogPublicEventMetadataType0.from_dict(data)



                return event_metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuditLogPublicEventMetadataType0 | None | Unset, data)

        event_metadata = _parse_event_metadata(d.pop("event_metadata", UNSET))


        def _parse_ip_address(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ip_address = _parse_ip_address(d.pop("ip_address", UNSET))


        def _parse_user_agent(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_agent = _parse_user_agent(d.pop("user_agent", UNSET))


        audit_log_public = cls(
            event_type=event_type,
            event_timestamp=event_timestamp,
            resource_type=resource_type,
            id=id,
            created_at=created_at,
            user_id=user_id,
            customer_id=customer_id,
            system_initiated=system_initiated,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            event_metadata=event_metadata,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return audit_log_public

