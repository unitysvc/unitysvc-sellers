from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..models.listing_status_enum import check_listing_status_enum
from ..models.listing_status_enum import ListingStatusEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.service_listing_public_parameters_schema_type_0 import ServiceListingPublicParametersSchemaType0
  from ..models.service_listing_public_parameters_ui_schema_type_0 import ServiceListingPublicParametersUiSchemaType0





T = TypeVar("T", bound="ServiceListingPublic")



@_attrs_define
class ServiceListingPublic:
    """ Public model for ServiceListing API responses.

    Contains only listing content fields. For service-level metadata like
    provider_name, seller_name, service_type, etc., use ServicePublic.

     """

    id: UUID
    status: ListingStatusEnum
    """ Status values that sellers can set for listings.

    Seller-accessible statuses:
    - draft: Work in progress, skipped during publish (won't be sent to backend)
    - ready: Complete and ready for admin review/testing
    - deprecated: Retired/end of life, no longer offered

    Note: Admin-managed workflow statuses (upstream_ready, downstream_ready, in_service)
    are set by the backend admin after testing and validation. These are not included in this
    enum since sellers cannot set them through the CLI tool. """
    created_at: str
    name: str | Unset = 'default'
    display_name: None | str | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    parameters_schema: None | ServiceListingPublicParametersSchemaType0 | Unset = UNSET
    parameters_ui_schema: None | ServiceListingPublicParametersUiSchemaType0 | Unset = UNSET
    tags: None | str | Unset = UNSET
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_listing_public_parameters_schema_type_0 import ServiceListingPublicParametersSchemaType0
        from ..models.service_listing_public_parameters_ui_schema_type_0 import ServiceListingPublicParametersUiSchemaType0
        id = str(self.id)

        status: str = self.status

        created_at = self.created_at

        name = self.name

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        parameters_schema: dict[str, Any] | None | Unset
        if isinstance(self.parameters_schema, Unset):
            parameters_schema = UNSET
        elif isinstance(self.parameters_schema, ServiceListingPublicParametersSchemaType0):
            parameters_schema = self.parameters_schema.to_dict()
        else:
            parameters_schema = self.parameters_schema

        parameters_ui_schema: dict[str, Any] | None | Unset
        if isinstance(self.parameters_ui_schema, Unset):
            parameters_ui_schema = UNSET
        elif isinstance(self.parameters_ui_schema, ServiceListingPublicParametersUiSchemaType0):
            parameters_ui_schema = self.parameters_ui_schema.to_dict()
        else:
            parameters_ui_schema = self.parameters_ui_schema

        tags: None | str | Unset
        if isinstance(self.tags, Unset):
            tags = UNSET
        else:
            tags = self.tags

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "status": status,
            "created_at": created_at,
        })
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if parameters_schema is not UNSET:
            field_dict["parameters_schema"] = parameters_schema
        if parameters_ui_schema is not UNSET:
            field_dict["parameters_ui_schema"] = parameters_ui_schema
        if tags is not UNSET:
            field_dict["tags"] = tags
        if currency is not UNSET:
            field_dict["currency"] = currency

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_listing_public_parameters_schema_type_0 import ServiceListingPublicParametersSchemaType0
        from ..models.service_listing_public_parameters_ui_schema_type_0 import ServiceListingPublicParametersUiSchemaType0
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        status = check_listing_status_enum(d.pop("status"))




        created_at = d.pop("created_at")

        name = d.pop("name", UNSET)

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))


        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))


        def _parse_parameters_schema(data: object) -> None | ServiceListingPublicParametersSchemaType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_schema_type_0 = ServiceListingPublicParametersSchemaType0.from_dict(data)



                return parameters_schema_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceListingPublicParametersSchemaType0 | Unset, data)

        parameters_schema = _parse_parameters_schema(d.pop("parameters_schema", UNSET))


        def _parse_parameters_ui_schema(data: object) -> None | ServiceListingPublicParametersUiSchemaType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_ui_schema_type_0 = ServiceListingPublicParametersUiSchemaType0.from_dict(data)



                return parameters_ui_schema_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceListingPublicParametersUiSchemaType0 | Unset, data)

        parameters_ui_schema = _parse_parameters_ui_schema(d.pop("parameters_ui_schema", UNSET))


        def _parse_tags(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        tags = _parse_tags(d.pop("tags", UNSET))


        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        service_listing_public = cls(
            id=id,
            status=status,
            created_at=created_at,
            name=name,
            display_name=display_name,
            updated_at=updated_at,
            parameters_schema=parameters_schema,
            parameters_ui_schema=parameters_ui_schema,
            tags=tags,
            currency=currency,
        )


        service_listing_public.additional_properties = d
        return service_listing_public

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
