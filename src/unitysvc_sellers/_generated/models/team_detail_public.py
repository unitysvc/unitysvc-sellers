from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.team_member_public import TeamMemberPublic





T = TypeVar("T", bound="TeamDetailPublic")



@_attrs_define
class TeamDetailPublic:
    """ Team detail with members and plan info.

     """

    id: UUID
    name: None | str
    customer_type: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    members: list[TeamMemberPublic]
    plan_name: None | str | Unset = UNSET
    plan_tier: None | str | Unset = UNSET
    seats_used: int | Unset = 0
    seats_total: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.team_member_public import TeamMemberPublic
        id = str(self.id)

        name: None | str
        name = self.name

        customer_type = self.customer_type

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        members = []
        for members_item_data in self.members:
            members_item = members_item_data.to_dict()
            members.append(members_item)



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

        seats_used = self.seats_used

        seats_total = self.seats_total


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "customer_type": customer_type,
            "created_at": created_at,
            "updated_at": updated_at,
            "members": members,
        })
        if plan_name is not UNSET:
            field_dict["plan_name"] = plan_name
        if plan_tier is not UNSET:
            field_dict["plan_tier"] = plan_tier
        if seats_used is not UNSET:
            field_dict["seats_used"] = seats_used
        if seats_total is not UNSET:
            field_dict["seats_total"] = seats_total

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team_member_public import TeamMemberPublic
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))


        customer_type = d.pop("customer_type")

        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        members = []
        _members = d.pop("members")
        for members_item_data in (_members):
            members_item = TeamMemberPublic.from_dict(members_item_data)



            members.append(members_item)


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


        seats_used = d.pop("seats_used", UNSET)

        seats_total = d.pop("seats_total", UNSET)

        team_detail_public = cls(
            id=id,
            name=name,
            customer_type=customer_type,
            created_at=created_at,
            updated_at=updated_at,
            members=members,
            plan_name=plan_name,
            plan_tier=plan_tier,
            seats_used=seats_used,
            seats_total=seats_total,
        )


        team_detail_public.additional_properties = d
        return team_detail_public

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
