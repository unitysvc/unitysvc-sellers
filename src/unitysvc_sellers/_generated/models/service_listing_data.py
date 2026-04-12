from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..models.listing_status_enum import check_listing_status_enum
from ..models.listing_status_enum import ListingStatusEnum
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID

if TYPE_CHECKING:
  from ..models.service_listing_data_documents_type_0 import ServiceListingDataDocumentsType0
  from ..models.service_listing_data_user_access_interfaces_type_0 import ServiceListingDataUserAccessInterfacesType0
  from ..models.service_listing_data_user_parameters_ui_schema_type_0 import ServiceListingDataUserParametersUiSchemaType0
  from ..models.service_listing_data_user_parameters_schema_type_0 import ServiceListingDataUserParametersSchemaType0
  from ..models.service_listing_data_list_price_type_0 import ServiceListingDataListPriceType0
  from ..models.service_listing_data_service_options_type_0 import ServiceListingDataServiceOptionsType0





T = TypeVar("T", bound="ServiceListingData")



@_attrs_define
class ServiceListingData:
    """ Base data structure for service listing information.

    This model contains the core fields needed to describe a service listing,
    without file-specific validation fields. It serves as:

    1. The base class for `ListingV1` in unitysvc-core (with additional
       schema_version and time_created fields for file validation)

    2. The data structure imported by unitysvc backend for:
       - API payload validation
       - Database comparison logic in find_and_compare_service_listing()
       - Publish operations from CLI

    Key characteristics:
    - Contains all user-provided data without system-generated IDs
    - Does not include permission/audit fields (handled by backend CRUD layer)
    - Uses dict types for nested structures to maintain flexibility between
      file definitions and database operations
    - Service/provider relationships are determined by file location (SDK mode) or
      by being published together in a single API call (API mode)

     """

    service_id: Union[None, UUID, Unset] = UNSET
    """ Service ID from previous publish. If provided, updates existing service. Stored in override file (e.g.,
    listing.override.json) by SDK after first publish. """
    name: Union[None, Unset, str] = UNSET
    """ Name identifier for the service listing (defaults to offering name if not provided) """
    display_name: Union[None, Unset, str] = UNSET
    """ Human-readable listing name (e.g., 'Premium GPT-4 Access', 'Enterprise AI Services') """
    status: Union[Unset, ListingStatusEnum] = UNSET
    """ Status values that sellers can set for listings.

    Seller-accessible statuses:
    - draft: Work in progress, skipped during publish (won't be sent to backend)
    - ready: Complete and ready for admin review/testing
    - deprecated: Retired/end of life, no longer offered

    Note: Admin-managed workflow statuses (upstream_ready, downstream_ready, in_service)
    are set by the backend admin after testing and validation. These are not included in this
    enum since sellers cannot set them through the CLI tool. """
    list_price: Union['ServiceListingDataListPriceType0', None, Unset] = UNSET
    """ List price: Listed price for customers per unit of service usage """
    currency: Union[Unset, CurrencyEnum] = UNSET
    """ Supported currency codes for pricing. """
    user_access_interfaces: Union['ServiceListingDataUserAccessInterfacesType0', None, Unset] = UNSET
    """ User access interfaces for the listing, keyed by name """
    documents: Union['ServiceListingDataDocumentsType0', None, Unset] = UNSET
    """ Documents associated with the listing, keyed by title (e.g., service level agreements) """
    user_parameters_schema: Union['ServiceListingDataUserParametersSchemaType0', None, Unset] = UNSET
    """ JSON Schema for user parameters """
    user_parameters_ui_schema: Union['ServiceListingDataUserParametersUiSchemaType0', None, Unset] = UNSET
    """ UI schema for user parameters form rendering """
    service_options: Union['ServiceListingDataServiceOptionsType0', None, Unset] = UNSET
    """ Service-specific options that modify backend behavior. Keys are option names, values are option
    configurations. The backend decides which options it supports. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_listing_data_documents_type_0 import ServiceListingDataDocumentsType0
        from ..models.service_listing_data_user_access_interfaces_type_0 import ServiceListingDataUserAccessInterfacesType0
        from ..models.service_listing_data_user_parameters_ui_schema_type_0 import ServiceListingDataUserParametersUiSchemaType0
        from ..models.service_listing_data_user_parameters_schema_type_0 import ServiceListingDataUserParametersSchemaType0
        from ..models.service_listing_data_list_price_type_0 import ServiceListingDataListPriceType0
        from ..models.service_listing_data_service_options_type_0 import ServiceListingDataServiceOptionsType0
        service_id: Union[None, Unset, str]
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        display_name: Union[None, Unset, str]
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status


        list_price: Union[None, Unset, dict[str, Any]]
        if isinstance(self.list_price, Unset):
            list_price = UNSET
        elif isinstance(self.list_price, ServiceListingDataListPriceType0):
            list_price = self.list_price.to_dict()
        else:
            list_price = self.list_price

        currency: Union[Unset, str] = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency


        user_access_interfaces: Union[None, Unset, dict[str, Any]]
        if isinstance(self.user_access_interfaces, Unset):
            user_access_interfaces = UNSET
        elif isinstance(self.user_access_interfaces, ServiceListingDataUserAccessInterfacesType0):
            user_access_interfaces = self.user_access_interfaces.to_dict()
        else:
            user_access_interfaces = self.user_access_interfaces

        documents: Union[None, Unset, dict[str, Any]]
        if isinstance(self.documents, Unset):
            documents = UNSET
        elif isinstance(self.documents, ServiceListingDataDocumentsType0):
            documents = self.documents.to_dict()
        else:
            documents = self.documents

        user_parameters_schema: Union[None, Unset, dict[str, Any]]
        if isinstance(self.user_parameters_schema, Unset):
            user_parameters_schema = UNSET
        elif isinstance(self.user_parameters_schema, ServiceListingDataUserParametersSchemaType0):
            user_parameters_schema = self.user_parameters_schema.to_dict()
        else:
            user_parameters_schema = self.user_parameters_schema

        user_parameters_ui_schema: Union[None, Unset, dict[str, Any]]
        if isinstance(self.user_parameters_ui_schema, Unset):
            user_parameters_ui_schema = UNSET
        elif isinstance(self.user_parameters_ui_schema, ServiceListingDataUserParametersUiSchemaType0):
            user_parameters_ui_schema = self.user_parameters_ui_schema.to_dict()
        else:
            user_parameters_ui_schema = self.user_parameters_ui_schema

        service_options: Union[None, Unset, dict[str, Any]]
        if isinstance(self.service_options, Unset):
            service_options = UNSET
        elif isinstance(self.service_options, ServiceListingDataServiceOptionsType0):
            service_options = self.service_options.to_dict()
        else:
            service_options = self.service_options


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if status is not UNSET:
            field_dict["status"] = status
        if list_price is not UNSET:
            field_dict["list_price"] = list_price
        if currency is not UNSET:
            field_dict["currency"] = currency
        if user_access_interfaces is not UNSET:
            field_dict["user_access_interfaces"] = user_access_interfaces
        if documents is not UNSET:
            field_dict["documents"] = documents
        if user_parameters_schema is not UNSET:
            field_dict["user_parameters_schema"] = user_parameters_schema
        if user_parameters_ui_schema is not UNSET:
            field_dict["user_parameters_ui_schema"] = user_parameters_ui_schema
        if service_options is not UNSET:
            field_dict["service_options"] = service_options

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_listing_data_documents_type_0 import ServiceListingDataDocumentsType0
        from ..models.service_listing_data_user_access_interfaces_type_0 import ServiceListingDataUserAccessInterfacesType0
        from ..models.service_listing_data_user_parameters_ui_schema_type_0 import ServiceListingDataUserParametersUiSchemaType0
        from ..models.service_listing_data_user_parameters_schema_type_0 import ServiceListingDataUserParametersSchemaType0
        from ..models.service_listing_data_list_price_type_0 import ServiceListingDataListPriceType0
        from ..models.service_listing_data_service_options_type_0 import ServiceListingDataServiceOptionsType0
        d = dict(src_dict)
        def _parse_service_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_id_type_0 = UUID(data)



                return service_id_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        service_id = _parse_service_id(d.pop("service_id", UNSET))


        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))


        def _parse_display_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))


        _status = d.pop("status", UNSET)
        status: Union[Unset, ListingStatusEnum]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = check_listing_status_enum(_status)




        def _parse_list_price(data: object) -> Union['ServiceListingDataListPriceType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                list_price_type_0 = ServiceListingDataListPriceType0.from_dict(data)



                return list_price_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceListingDataListPriceType0', None, Unset], data)

        list_price = _parse_list_price(d.pop("list_price", UNSET))


        _currency = d.pop("currency", UNSET)
        currency: Union[Unset, CurrencyEnum]
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        def _parse_user_access_interfaces(data: object) -> Union['ServiceListingDataUserAccessInterfacesType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_access_interfaces_type_0 = ServiceListingDataUserAccessInterfacesType0.from_dict(data)



                return user_access_interfaces_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceListingDataUserAccessInterfacesType0', None, Unset], data)

        user_access_interfaces = _parse_user_access_interfaces(d.pop("user_access_interfaces", UNSET))


        def _parse_documents(data: object) -> Union['ServiceListingDataDocumentsType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                documents_type_0 = ServiceListingDataDocumentsType0.from_dict(data)



                return documents_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceListingDataDocumentsType0', None, Unset], data)

        documents = _parse_documents(d.pop("documents", UNSET))


        def _parse_user_parameters_schema(data: object) -> Union['ServiceListingDataUserParametersSchemaType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_parameters_schema_type_0 = ServiceListingDataUserParametersSchemaType0.from_dict(data)



                return user_parameters_schema_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceListingDataUserParametersSchemaType0', None, Unset], data)

        user_parameters_schema = _parse_user_parameters_schema(d.pop("user_parameters_schema", UNSET))


        def _parse_user_parameters_ui_schema(data: object) -> Union['ServiceListingDataUserParametersUiSchemaType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_parameters_ui_schema_type_0 = ServiceListingDataUserParametersUiSchemaType0.from_dict(data)



                return user_parameters_ui_schema_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceListingDataUserParametersUiSchemaType0', None, Unset], data)

        user_parameters_ui_schema = _parse_user_parameters_ui_schema(d.pop("user_parameters_ui_schema", UNSET))


        def _parse_service_options(data: object) -> Union['ServiceListingDataServiceOptionsType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                service_options_type_0 = ServiceListingDataServiceOptionsType0.from_dict(data)



                return service_options_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceListingDataServiceOptionsType0', None, Unset], data)

        service_options = _parse_service_options(d.pop("service_options", UNSET))


        service_listing_data = cls(
            service_id=service_id,
            name=name,
            display_name=display_name,
            status=status,
            list_price=list_price,
            currency=currency,
            user_access_interfaces=user_access_interfaces,
            documents=documents,
            user_parameters_schema=user_parameters_schema,
            user_parameters_ui_schema=user_parameters_ui_schema,
            service_options=service_options,
        )


        service_listing_data.additional_properties = d
        return service_listing_data

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
