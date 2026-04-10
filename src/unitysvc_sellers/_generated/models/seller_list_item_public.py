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






T = TypeVar("T", bound="SellerListItemPublic")



@_attrs_define
class SellerListItemPublic:
    """ Seller list item with account manager info for admin API.

     """

    id: UUID
    name: str
    display_name: None | str
    seller_type: str
    status: str
    contact_email: str
    is_verified: bool
    account_manager_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    account_manager_email: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        display_name: None | str
        display_name = self.display_name

        seller_type = self.seller_type

        status = self.status

        contact_email = self.contact_email

        is_verified = self.is_verified

        account_manager_id = str(self.account_manager_id)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        account_manager_email: None | str | Unset
        if isinstance(self.account_manager_email, Unset):
            account_manager_email = UNSET
        else:
            account_manager_email = self.account_manager_email


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "display_name": display_name,
            "seller_type": seller_type,
            "status": status,
            "contact_email": contact_email,
            "is_verified": is_verified,
            "account_manager_id": account_manager_id,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if account_manager_email is not UNSET:
            field_dict["account_manager_email"] = account_manager_email

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        name = d.pop("name")

        def _parse_display_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        display_name = _parse_display_name(d.pop("display_name"))


        seller_type = d.pop("seller_type")

        status = d.pop("status")

        contact_email = d.pop("contact_email")

        is_verified = d.pop("is_verified")

        account_manager_id = UUID(d.pop("account_manager_id"))




        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        def _parse_account_manager_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        account_manager_email = _parse_account_manager_email(d.pop("account_manager_email", UNSET))


        seller_list_item_public = cls(
            id=id,
            name=name,
            display_name=display_name,
            seller_type=seller_type,
            status=status,
            contact_email=contact_email,
            is_verified=is_verified,
            account_manager_id=account_manager_id,
            created_at=created_at,
            updated_at=updated_at,
            account_manager_email=account_manager_email,
        )


        seller_list_item_public.additional_properties = d
        return seller_list_item_public

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
