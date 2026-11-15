from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.room_origin_enrollment import RoomOriginEnrollment
    from ..models.room_origin_service import RoomOriginService


T = TypeVar("T", bound="RoomOrigin")


@_attrs_define
class RoomOrigin:
    """What the room was provisioned for (#2969): its service, and the
    caller's enrollments that brought it in. Only the enrollment's customer
    (or the service's seller) sees an enrollment here; a guest sees the
    service alone.

    """

    service: RoomOriginService
    enrollments: list[RoomOriginEnrollment] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        service = self.service.to_dict()

        enrollments: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.enrollments, Unset):
            enrollments = []
            for enrollments_item_data in self.enrollments:
                enrollments_item = enrollments_item_data.to_dict()
                enrollments.append(enrollments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service": service,
            }
        )
        if enrollments is not UNSET:
            field_dict["enrollments"] = enrollments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.room_origin_enrollment import RoomOriginEnrollment
        from ..models.room_origin_service import RoomOriginService

        d = dict(src_dict)
        service = RoomOriginService.from_dict(d.pop("service"))

        _enrollments = d.pop("enrollments", UNSET)
        enrollments: list[RoomOriginEnrollment] | Unset = UNSET
        if _enrollments is not UNSET:
            enrollments = []
            for enrollments_item_data in _enrollments:
                enrollments_item = RoomOriginEnrollment.from_dict(enrollments_item_data)

                enrollments.append(enrollments_item)

        room_origin = cls(
            service=service,
            enrollments=enrollments,
        )

        room_origin.additional_properties = d
        return room_origin

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
