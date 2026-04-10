from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.seller_type_enum import check_seller_type_enum
from ..models.seller_type_enum import SellerTypeEnum
from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="SellerApplicationRequest")



@_attrs_define
class SellerApplicationRequest:
    """ Request for creating a seller application (user signup flow).

     """

    name: str
    """ Unique seller identifier (URL-friendly, e.g., 'acme-corp') """
    contact_email: str
    """ Primary contact email for the seller """
    display_name: None | str | Unset = UNSET
    """ Human-readable seller name (e.g., 'ACME Corporation') """
    seller_type: SellerTypeEnum | Unset = UNSET
    description: None | str | Unset = UNSET
    """ Brief description of the seller """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        contact_email = self.contact_email

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        seller_type: str | Unset = UNSET
        if not isinstance(self.seller_type, Unset):
            seller_type = self.seller_type


        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "contact_email": contact_email,
        })
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if seller_type is not UNSET:
            field_dict["seller_type"] = seller_type
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        contact_email = d.pop("contact_email")

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))


        _seller_type = d.pop("seller_type", UNSET)
        seller_type: SellerTypeEnum | Unset
        if isinstance(_seller_type,  Unset):
            seller_type = UNSET
        else:
            seller_type = check_seller_type_enum(_seller_type)




        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        seller_application_request = cls(
            name=name,
            contact_email=contact_email,
            display_name=display_name,
            seller_type=seller_type,
            description=description,
        )


        seller_application_request.additional_properties = d
        return seller_application_request

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
