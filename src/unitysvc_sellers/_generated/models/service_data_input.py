from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.provider_data import ProviderData
    from ..models.service_data import ServiceData
    from ..models.service_listing_data import ServiceListingData
    from ..models.service_offering_data import ServiceOfferingData


T = TypeVar("T", bound="ServiceDataInput")


@_attrs_define
class ServiceDataInput:
    """Complete service data input for publishing.

    Fields are typed against the shared ``unitysvc_core`` models so the
    OpenAPI spec carries the full provider/offering/listing schemas, and
    generated clients expose typed upload methods instead of ``dict[str, Any]``.

    """

    provider_data: ProviderData
    """ Base data structure for provider information.

    This model contains the core fields needed to describe a provider,
    without file-specific validation fields. It serves as:

    1. The base class for `ProviderV1` in unitysvc-core (with additional
       time_created and services_populator fields for file validation)

    2. The data structure imported by unitysvc backend for:
       - API payload validation
       - Database comparison logic in find_and_compare_provider()
       - Publish operations from CLI

    Key characteristics:
    - Uses string identifiers that match database requirements
    - Contains all user-provided data without system-generated IDs
    - Does not include permission/audit fields (handled by backend CRUD layer) """
    offering_data: ServiceOfferingData
    """ Base data structure for service offering information.

    This model contains the core fields needed to describe a service offering,
    without file-specific validation fields. It serves as:

    1. The base class for `OfferingV1` in unitysvc-core (with additional
       time_created field for file validation)

    2. The data structure imported by unitysvc backend for:
       - API payload validation
       - Database comparison logic in find_and_compare_service_offering()
       - Publish operations from CLI

    Key characteristics:
    - status maps to database 'status' field
    - Contains all user-provided data without system-generated IDs
    - Does not include permission/audit fields (handled by backend CRUD layer)
    - Provider relationship is determined by file location (SDK mode) or
      by being published together in a single API call (API mode) """
    listing_data: ServiceListingData
    """ Base data structure for service listing information.

    This model contains the core fields needed to describe a service listing,
    without file-specific validation fields. It serves as:

    1. The base class for `ListingV1` in unitysvc-core (with additional
       time_created field for file validation)

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
      by being published together in a single API call (API mode) """
    service_data: None | ServiceData | Unset = UNSET
    """ Backend-assigned service identity record (the seller's service.json). Distinct from the authored
    provider/offering/listing content, so it travels as its own field. Of its fields only service_id is read here —
    it targets an existing service (create-vs-revise-vs-replace); the rest is provenance the seller carries.
    Returned by ingest_service and replayed on the next upload. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.provider_data import ProviderData
        from ..models.service_data import ServiceData
        from ..models.service_listing_data import ServiceListingData
        from ..models.service_offering_data import ServiceOfferingData

        provider_data = self.provider_data.to_dict()

        offering_data = self.offering_data.to_dict()

        listing_data = self.listing_data.to_dict()

        service_data: dict[str, Any] | None | Unset
        if isinstance(self.service_data, Unset):
            service_data = UNSET
        elif isinstance(self.service_data, ServiceData):
            service_data = self.service_data.to_dict()
        else:
            service_data = self.service_data

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider_data": provider_data,
                "offering_data": offering_data,
                "listing_data": listing_data,
            }
        )
        if service_data is not UNSET:
            field_dict["service_data"] = service_data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provider_data import ProviderData
        from ..models.service_data import ServiceData
        from ..models.service_listing_data import ServiceListingData
        from ..models.service_offering_data import ServiceOfferingData

        d = dict(src_dict)
        provider_data = ProviderData.from_dict(d.pop("provider_data"))

        offering_data = ServiceOfferingData.from_dict(d.pop("offering_data"))

        listing_data = ServiceListingData.from_dict(d.pop("listing_data"))

        def _parse_service_data(data: object) -> None | ServiceData | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                service_data_type_0 = ServiceData.from_dict(data)

                return service_data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceData | Unset, data)

        service_data = _parse_service_data(d.pop("service_data", UNSET))

        service_data_input = cls(
            provider_data=provider_data,
            offering_data=offering_data,
            listing_data=listing_data,
            service_data=service_data,
        )

        service_data_input.additional_properties = d
        return service_data_input

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
