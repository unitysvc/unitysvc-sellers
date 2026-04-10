from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.provider_status_enum import check_provider_status_enum
from ..models.provider_status_enum import ProviderStatusEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="ProviderPublic")



@_attrs_define
class ProviderPublic:
    """ Public provider information for API responses.

     """

    id: UUID
    name: str
    contact_email: str
    homepage: str
    status: ProviderStatusEnum
    """ Status values that sellers can set for providers.

    Seller-accessible statuses:
    - draft: Work in progress, skipped during publish
    - ready: Complete and ready for admin review
    - deprecated: Provider is retired/end of life """
    created_at: datetime.datetime
    updated_at: datetime.datetime
    display_name: None | str | Unset = UNSET
    secondary_contact_email: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        contact_email = self.contact_email

        homepage = self.homepage

        status: str = self.status

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

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


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "contact_email": contact_email,
            "homepage": homepage,
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if secondary_contact_email is not UNSET:
            field_dict["secondary_contact_email"] = secondary_contact_email
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        name = d.pop("name")

        contact_email = d.pop("contact_email")

        homepage = d.pop("homepage")

        status = check_provider_status_enum(d.pop("status"))




        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




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


        provider_public = cls(
            id=id,
            name=name,
            contact_email=contact_email,
            homepage=homepage,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            display_name=display_name,
            secondary_contact_email=secondary_contact_email,
            description=description,
        )


        provider_public.additional_properties = d
        return provider_public

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
