from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.provider_status_enum import check_provider_status_enum
from ..models.provider_status_enum import ProviderStatusEnum
from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="ProviderCreate")



@_attrs_define
class ProviderCreate:
    """ Schema for creating a new Provider - same as base (pure content).

     """

    name: str
    """ Provider identifier (URL-friendly, e.g., 'fireworks', 'anthropic') """
    contact_email: str
    """ Primary contact email for the provider """
    homepage: str
    """ Provider's homepage URL """
    display_name: None | str | Unset = UNSET
    """ Human-readable provider name (e.g., 'Fireworks AI', 'Anthropic') """
    secondary_contact_email: None | str | Unset = UNSET
    """ Secondary contact email """
    description: None | str | Unset = UNSET
    """ Brief description of the provider """
    status: ProviderStatusEnum | Unset = UNSET
    """ Status values that sellers can set for providers.

    Seller-accessible statuses:
    - draft: Work in progress, skipped during publish
    - ready: Complete and ready for admin review
    - deprecated: Provider is retired/end of life """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        contact_email = self.contact_email

        homepage = self.homepage

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        secondary_contact_email: None | str | Unset
        if isinstance(self.secondary_contact_email, Unset):
            secondary_contact_email = UNSET
        else:
            secondary_contact_email = self.secondary_contact_email

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "contact_email": contact_email,
            "homepage": homepage,
        })
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if secondary_contact_email is not UNSET:
            field_dict["secondary_contact_email"] = secondary_contact_email
        if description is not UNSET:
            field_dict["description"] = description
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        contact_email = d.pop("contact_email")

        homepage = d.pop("homepage")

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))


        def _parse_secondary_contact_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        secondary_contact_email = _parse_secondary_contact_email(d.pop("secondary_contact_email", UNSET))


        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))


        _status = d.pop("status", UNSET)
        status: ProviderStatusEnum | Unset
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_provider_status_enum(_status)




        provider_create = cls(
            name=name,
            contact_email=contact_email,
            homepage=homepage,
            display_name=display_name,
            secondary_contact_email=secondary_contact_email,
            description=description,
            status=status,
        )


        provider_create.additional_properties = d
        return provider_create

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
