from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.customer_membership_status import check_customer_membership_status
from ..models.customer_membership_status import CustomerMembershipStatus
from ..models.customer_role_enum import check_customer_role_enum
from ..models.customer_role_enum import CustomerRoleEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="CustomerMembershipPublic")



@_attrs_define
class CustomerMembershipPublic:
    """ Public CustomerMembership information for API responses.

     """

    id: UUID
    user_id: UUID
    customer_id: UUID
    joined_at: datetime.datetime
    invited_by_id: None | UUID
    left_at: datetime.datetime | None
    role: CustomerRoleEnum | Unset = UNSET
    status: CustomerMembershipStatus | Unset = UNSET
    """ Status of a user's membership in a customer (team). """





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        user_id = str(self.user_id)

        customer_id = str(self.customer_id)

        joined_at = self.joined_at.isoformat()

        invited_by_id: None | str
        if isinstance(self.invited_by_id, UUID):
            invited_by_id = str(self.invited_by_id)
        else:
            invited_by_id = self.invited_by_id

        left_at: None | str
        if isinstance(self.left_at, datetime.datetime):
            left_at = self.left_at.isoformat()
        else:
            left_at = self.left_at

        role: str | Unset = UNSET
        if not isinstance(self.role, Unset):
            role = self.role


        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status



        field_dict: dict[str, Any] = {}

        field_dict.update({
            "id": id,
            "user_id": user_id,
            "customer_id": customer_id,
            "joined_at": joined_at,
            "invited_by_id": invited_by_id,
            "left_at": left_at,
        })
        if role is not UNSET:
            field_dict["role"] = role
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        user_id = UUID(d.pop("user_id"))




        customer_id = UUID(d.pop("customer_id"))




        joined_at = isoparse(d.pop("joined_at"))




        def _parse_invited_by_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                invited_by_id_type_0 = UUID(data)



                return invited_by_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        invited_by_id = _parse_invited_by_id(d.pop("invited_by_id"))


        def _parse_left_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                left_at_type_0 = isoparse(data)



                return left_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        left_at = _parse_left_at(d.pop("left_at"))


        _role = d.pop("role", UNSET)
        role: CustomerRoleEnum | Unset
        if isinstance(_role,  Unset):
            role = UNSET
        else:
            role = check_customer_role_enum(_role)




        _status = d.pop("status", UNSET)
        status: CustomerMembershipStatus | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_customer_membership_status(_status)




        customer_membership_public = cls(
            id=id,
            user_id=user_id,
            customer_id=customer_id,
            joined_at=joined_at,
            invited_by_id=invited_by_id,
            left_at=left_at,
            role=role,
            status=status,
        )

        return customer_membership_public

