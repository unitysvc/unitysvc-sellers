from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.pending_action_request_metadata_type_0 import PendingActionRequestMetadataType0





T = TypeVar("T", bound="PendingActionRequest")



@_attrs_define
class PendingActionRequest:
    """ Request to schedule a deferred action on a subscription.

     """

    action: str
    """ Action to execute at period end: 'cancel', 'pause', or 'downgrade' """
    metadata: None | PendingActionRequestMetadataType0 | Unset = UNSET
    """ Details for the action (e.g. new_plan_id, new_quantity for downgrade) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.pending_action_request_metadata_type_0 import PendingActionRequestMetadataType0
        action = self.action

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, PendingActionRequestMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "action": action,
        })
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pending_action_request_metadata_type_0 import PendingActionRequestMetadataType0
        d = dict(src_dict)
        action = d.pop("action")

        def _parse_metadata(data: object) -> None | PendingActionRequestMetadataType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = PendingActionRequestMetadataType0.from_dict(data)



                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PendingActionRequestMetadataType0 | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))


        pending_action_request = cls(
            action=action,
            metadata=metadata,
        )


        pending_action_request.additional_properties = d
        return pending_action_request

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
