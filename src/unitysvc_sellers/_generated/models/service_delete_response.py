from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="ServiceDeleteResponse")



@_attrs_define
class ServiceDeleteResponse:
    """ DELETE /seller/services/{id} — unified response for dryrun and real deletes.

    When dryrun=true, only the can_delete/reason fields are meaningful.
    When dryrun=false and can_delete=true, the service is deleted and
    deleted=true. When dryrun=false and can_delete=false, a 400 is raised.

     """

    can_delete: bool
    message: str
    reason: None | str | Unset = UNSET
    deleted: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        can_delete = self.can_delete

        message = self.message

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        deleted = self.deleted


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "can_delete": can_delete,
            "message": message,
        })
        if reason is not UNSET:
            field_dict["reason"] = reason
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        can_delete = d.pop("can_delete")

        message = d.pop("message")

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))


        deleted = d.pop("deleted", UNSET)

        service_delete_response = cls(
            can_delete=can_delete,
            message=message,
            reason=reason,
            deleted=deleted,
        )


        service_delete_response.additional_properties = d
        return service_delete_response

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
