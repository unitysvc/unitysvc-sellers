from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.provider_status_enum import check_provider_status_enum
from ..models.provider_status_enum import ProviderStatusEnum
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.provider_data_documents_type_0 import ProviderDataDocumentsType0





T = TypeVar("T", bound="ProviderData")



@_attrs_define
class ProviderData:
    """ Base data structure for provider information.

    This model contains the core fields needed to describe a provider,
    without file-specific validation fields. It serves as:

    1. The base class for `ProviderV1` in unitysvc-core (with additional
       schema_version, time_created, and services_populator fields for file validation)

    2. The data structure imported by unitysvc backend for:
       - API payload validation
       - Database comparison logic in find_and_compare_provider()
       - Publish operations from CLI

    Key characteristics:
    - Uses string identifiers that match database requirements
    - Contains all user-provided data without system-generated IDs
    - Does not include permission/audit fields (handled by backend CRUD layer)

     """

    name: str
    """ Unique provider identifier (URL-friendly, e.g., 'fireworks', 'anthropic') """
    contact_email: str
    """ Primary contact email for the provider """
    homepage: str
    """ Provider's homepage URL """
    display_name: Union[None, Unset, str] = UNSET
    """ Human-readable provider name (e.g., 'Fireworks AI', 'Anthropic') """
    secondary_contact_email: Union[None, Unset, str] = UNSET
    """ Secondary contact email """
    description: Union[None, Unset, str] = UNSET
    """ Brief description of the provider """
    status: Union[Unset, ProviderStatusEnum] = UNSET
    """ Status values that sellers can set for providers.

    Seller-accessible statuses:
    - draft: Work in progress, skipped during publish
    - ready: Complete and ready for admin review
    - deprecated: Provider is retired/end of life """
    documents: Union['ProviderDataDocumentsType0', None, Unset] = UNSET
    """ Documents associated with the provider, keyed by title """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.provider_data_documents_type_0 import ProviderDataDocumentsType0
        name = self.name

        contact_email = self.contact_email

        homepage = self.homepage

        display_name: Union[None, Unset, str]
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        secondary_contact_email: Union[None, Unset, str]
        if isinstance(self.secondary_contact_email, Unset):
            secondary_contact_email = UNSET
        else:
            secondary_contact_email = self.secondary_contact_email

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status


        documents: Union[None, Unset, dict[str, Any]]
        if isinstance(self.documents, Unset):
            documents = UNSET
        elif isinstance(self.documents, ProviderDataDocumentsType0):
            documents = self.documents.to_dict()
        else:
            documents = self.documents


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
        if documents is not UNSET:
            field_dict["documents"] = documents

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provider_data_documents_type_0 import ProviderDataDocumentsType0
        d = dict(src_dict)
        name = d.pop("name")

        contact_email = d.pop("contact_email")

        homepage = d.pop("homepage")

        def _parse_display_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))


        def _parse_secondary_contact_email(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        secondary_contact_email = _parse_secondary_contact_email(d.pop("secondary_contact_email", UNSET))


        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        _status = d.pop("status", UNSET)
        status: Union[Unset, ProviderStatusEnum]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_provider_status_enum(_status)




        def _parse_documents(data: object) -> Union['ProviderDataDocumentsType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                documents_type_0 = ProviderDataDocumentsType0.from_dict(data)



                return documents_type_0
            except: # noqa: E722
                pass
            return cast(Union['ProviderDataDocumentsType0', None, Unset], data)

        documents = _parse_documents(d.pop("documents", UNSET))


        provider_data = cls(
            name=name,
            contact_email=contact_email,
            homepage=homepage,
            display_name=display_name,
            secondary_contact_email=secondary_contact_email,
            description=description,
            status=status,
            documents=documents,
        )


        provider_data.additional_properties = d
        return provider_data

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
