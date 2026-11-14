from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.room_connector_view import RoomConnectorView


T = TypeVar("T", bound="RoomDelivery")


@_attrs_define
class RoomDelivery:
    """How the room reaches the calling account: its connectors, oldest
    first, each with a service or null (off) for each channel. A new member
    starts with one connector, ``main``, holding its account's room defaults
    (``room-{notify,email}-as-{host,guest}``). A post that names no connector
    came in through none: it goes out through every connector.

    """

    connectors: list[RoomConnectorView]
    can_edit: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connectors = []
        for connectors_item_data in self.connectors:
            connectors_item = connectors_item_data.to_dict()
            connectors.append(connectors_item)

        can_edit = self.can_edit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "connectors": connectors,
                "can_edit": can_edit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.room_connector_view import RoomConnectorView

        d = dict(src_dict)
        connectors = []
        _connectors = d.pop("connectors")
        for connectors_item_data in _connectors:
            connectors_item = RoomConnectorView.from_dict(connectors_item_data)

            connectors.append(connectors_item)

        can_edit = d.pop("can_edit")

        room_delivery = cls(
            connectors=connectors,
            can_edit=can_edit,
        )

        room_delivery.additional_properties = d
        return room_delivery

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
