from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.customer_role_enum import check_customer_role_enum
from ..models.customer_role_enum import CustomerRoleEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="CustomerMembershipWithDetails")



@_attrs_define
class CustomerMembershipWithDetails:
    """ User's customer membership with full customer and subscription details.

    Used for multi-tenant account switching in the frontend.

     """

    id: UUID
    role: CustomerRoleEnum
    joined_at: datetime.datetime
    customer_id: UUID
    customer_name: None | str
    customer_type: str
    customer_status: str | Unset = 'active'
    plan_name: None | str | Unset = UNSET
    plan_tier: None | str | Unset = UNSET
    subscription_status: None | str | Unset = UNSET
    member_count: int | None | Unset = UNSET
    seat_limit: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        role: str = self.role

        joined_at = self.joined_at.isoformat()

        customer_id = str(self.customer_id)

        customer_name: None | str
        customer_name = self.customer_name

        customer_type = self.customer_type

        customer_status = self.customer_status

        plan_name: None | str | Unset
        if isinstance(self.plan_name, Unset):
            plan_name = UNSET
        else:
            plan_name = self.plan_name

        plan_tier: None | str | Unset
        if isinstance(self.plan_tier, Unset):
            plan_tier = UNSET
        else:
            plan_tier = self.plan_tier

        subscription_status: None | str | Unset
        if isinstance(self.subscription_status, Unset):
            subscription_status = UNSET
        else:
            subscription_status = self.subscription_status

        member_count: int | None | Unset
        if isinstance(self.member_count, Unset):
            member_count = UNSET
        else:
            member_count = self.member_count

        seat_limit: int | None | Unset
        if isinstance(self.seat_limit, Unset):
            seat_limit = UNSET
        else:
            seat_limit = self.seat_limit


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "role": role,
            "joined_at": joined_at,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "customer_type": customer_type,
        })
        if customer_status is not UNSET:
            field_dict["customer_status"] = customer_status
        if plan_name is not UNSET:
            field_dict["plan_name"] = plan_name
        if plan_tier is not UNSET:
            field_dict["plan_tier"] = plan_tier
        if subscription_status is not UNSET:
            field_dict["subscription_status"] = subscription_status
        if member_count is not UNSET:
            field_dict["member_count"] = member_count
        if seat_limit is not UNSET:
            field_dict["seat_limit"] = seat_limit

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        role = check_customer_role_enum(d.pop("role"))




        joined_at = isoparse(d.pop("joined_at"))




        customer_id = UUID(d.pop("customer_id"))




        def _parse_customer_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        customer_name = _parse_customer_name(d.pop("customer_name"))


        customer_type = d.pop("customer_type")

        customer_status = d.pop("customer_status", UNSET)

        def _parse_plan_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        plan_name = _parse_plan_name(d.pop("plan_name", UNSET))


        def _parse_plan_tier(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        plan_tier = _parse_plan_tier(d.pop("plan_tier", UNSET))


        def _parse_subscription_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        subscription_status = _parse_subscription_status(d.pop("subscription_status", UNSET))


        def _parse_member_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        member_count = _parse_member_count(d.pop("member_count", UNSET))


        def _parse_seat_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        seat_limit = _parse_seat_limit(d.pop("seat_limit", UNSET))


        customer_membership_with_details = cls(
            id=id,
            role=role,
            joined_at=joined_at,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_type=customer_type,
            customer_status=customer_status,
            plan_name=plan_name,
            plan_tier=plan_tier,
            subscription_status=subscription_status,
            member_count=member_count,
            seat_limit=seat_limit,
        )


        customer_membership_with_details.additional_properties = d
        return customer_membership_with_details

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
