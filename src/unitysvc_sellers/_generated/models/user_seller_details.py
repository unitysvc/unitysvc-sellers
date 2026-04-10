from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from uuid import UUID






T = TypeVar("T", bound="UserSellerDetails")



@_attrs_define
class UserSellerDetails:
    """ User's seller account details.

    Represents a seller account the user manages (as account_manager, creator, or updater).

     """

    seller_id: UUID
    seller_name: str
    display_name: None | str
    seller_type: str
    status: str
    is_verified: bool
    is_account_manager: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        seller_id = str(self.seller_id)

        seller_name = self.seller_name

        display_name: None | str
        display_name = self.display_name

        seller_type = self.seller_type

        status = self.status

        is_verified = self.is_verified

        is_account_manager = self.is_account_manager


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "seller_id": seller_id,
            "seller_name": seller_name,
            "display_name": display_name,
            "seller_type": seller_type,
            "status": status,
            "is_verified": is_verified,
            "is_account_manager": is_account_manager,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        seller_id = UUID(d.pop("seller_id"))




        seller_name = d.pop("seller_name")

        def _parse_display_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        display_name = _parse_display_name(d.pop("display_name"))


        seller_type = d.pop("seller_type")

        status = d.pop("status")

        is_verified = d.pop("is_verified")

        is_account_manager = d.pop("is_account_manager")

        user_seller_details = cls(
            seller_id=seller_id,
            seller_name=seller_name,
            display_name=display_name,
            seller_type=seller_type,
            status=status,
            is_verified=is_verified,
            is_account_manager=is_account_manager,
        )


        user_seller_details.additional_properties = d
        return user_seller_details

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
