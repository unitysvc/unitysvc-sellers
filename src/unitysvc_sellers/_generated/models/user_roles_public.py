from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.customer_membership_with_details import CustomerMembershipWithDetails
  from ..models.user_seller_details import UserSellerDetails





T = TypeVar("T", bound="UserRolesPublic")



@_attrs_define
class UserRolesPublic:
    """ Combined user roles including customers and sellers.

    Used for multi-tenant account switching and seller mode detection in the frontend.

     """

    customers: list[CustomerMembershipWithDetails]
    sellers: list[UserSellerDetails]
    is_admin: bool | Unset = False
    full_name: None | str | Unset = UNSET
    email: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_membership_with_details import CustomerMembershipWithDetails
        from ..models.user_seller_details import UserSellerDetails
        customers = []
        for customers_item_data in self.customers:
            customers_item = customers_item_data.to_dict()
            customers.append(customers_item)



        sellers = []
        for sellers_item_data in self.sellers:
            sellers_item = sellers_item_data.to_dict()
            sellers.append(sellers_item)



        is_admin = self.is_admin

        full_name: None | str | Unset
        if isinstance(self.full_name, Unset):
            full_name = UNSET
        else:
            full_name = self.full_name

        email: None | str | Unset
        if isinstance(self.email, Unset):
            email = UNSET
        else:
            email = self.email


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "customers": customers,
            "sellers": sellers,
        })
        if is_admin is not UNSET:
            field_dict["is_admin"] = is_admin
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if email is not UNSET:
            field_dict["email"] = email

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_membership_with_details import CustomerMembershipWithDetails
        from ..models.user_seller_details import UserSellerDetails
        d = dict(src_dict)
        customers = []
        _customers = d.pop("customers")
        for customers_item_data in (_customers):
            customers_item = CustomerMembershipWithDetails.from_dict(customers_item_data)



            customers.append(customers_item)


        sellers = []
        _sellers = d.pop("sellers")
        for sellers_item_data in (_sellers):
            sellers_item = UserSellerDetails.from_dict(sellers_item_data)



            sellers.append(sellers_item)


        is_admin = d.pop("is_admin", UNSET)

        def _parse_full_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        full_name = _parse_full_name(d.pop("full_name", UNSET))


        def _parse_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        email = _parse_email(d.pop("email", UNSET))


        user_roles_public = cls(
            customers=customers,
            sellers=sellers,
            is_admin=is_admin,
            full_name=full_name,
            email=email,
        )


        user_roles_public.additional_properties = d
        return user_roles_public

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
