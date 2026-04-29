from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_interface_public import AccessInterfacePublic
    from ..models.provider_data import ProviderData
    from ..models.service_detail_response_routing_vars_type_0 import ServiceDetailResponseRoutingVarsType0
    from ..models.service_document_item import ServiceDocumentItem
    from ..models.service_listing_data import ServiceListingData
    from ..models.service_offering_data import ServiceOfferingData


T = TypeVar("T", bound="ServiceDetailResponse")


@_attrs_define
class ServiceDetailResponse:
    """GET /seller/services/{id} — live service record.

    The provider / offering / listing fields carry the same typed shapes
    the seller used to upload the service (``ProviderData`` /
    ``ServiceOfferingData`` / ``ServiceListingData`` from
    ``unitysvc_core.models``), so SDK consumers get autocomplete and
    typed access to the nested data without re-defining the schema.

    The shape reflects the **live** state of the service, not a snapshot
    of the original upload — in particular ``interfaces`` includes all
    interfaces available to the caller: listing-native, service-group-derived,
    and enrollment-scoped interfaces owned by the caller (ops enrollment for
    sellers). Per-customer enrollment interfaces are hidden from sellers.

    The embedded ``documents`` carry metadata only; fetch file content
    separately via ``GET /seller/documents/{id}``.

    """

    service_id: str
    status: str
    documents: list[ServiceDocumentItem]
    interfaces: list[AccessInterfacePublic]
    service_name: None | str | Unset = UNSET
    status_message: None | str | Unset = UNSET
    routing_vars: None | ServiceDetailResponseRoutingVarsType0 | Unset = UNSET
    provider: None | ProviderData | Unset = UNSET
    offering: None | ServiceOfferingData | Unset = UNSET
    listing: None | ServiceListingData | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_interface_public import AccessInterfacePublic
        from ..models.provider_data import ProviderData
        from ..models.service_detail_response_routing_vars_type_0 import ServiceDetailResponseRoutingVarsType0
        from ..models.service_document_item import ServiceDocumentItem
        from ..models.service_listing_data import ServiceListingData
        from ..models.service_offering_data import ServiceOfferingData

        service_id = self.service_id

        status = self.status

        documents = []
        for documents_item_data in self.documents:
            documents_item = documents_item_data.to_dict()
            documents.append(documents_item)

        interfaces = []
        for interfaces_item_data in self.interfaces:
            interfaces_item = interfaces_item_data.to_dict()
            interfaces.append(interfaces_item)

        service_name: None | str | Unset
        if isinstance(self.service_name, Unset):
            service_name = UNSET
        else:
            service_name = self.service_name

        status_message: None | str | Unset
        if isinstance(self.status_message, Unset):
            status_message = UNSET
        else:
            status_message = self.status_message

        routing_vars: dict[str, Any] | None | Unset
        if isinstance(self.routing_vars, Unset):
            routing_vars = UNSET
        elif isinstance(self.routing_vars, ServiceDetailResponseRoutingVarsType0):
            routing_vars = self.routing_vars.to_dict()
        else:
            routing_vars = self.routing_vars

        provider: dict[str, Any] | None | Unset
        if isinstance(self.provider, Unset):
            provider = UNSET
        elif isinstance(self.provider, ProviderData):
            provider = self.provider.to_dict()
        else:
            provider = self.provider

        offering: dict[str, Any] | None | Unset
        if isinstance(self.offering, Unset):
            offering = UNSET
        elif isinstance(self.offering, ServiceOfferingData):
            offering = self.offering.to_dict()
        else:
            offering = self.offering

        listing: dict[str, Any] | None | Unset
        if isinstance(self.listing, Unset):
            listing = UNSET
        elif isinstance(self.listing, ServiceListingData):
            listing = self.listing.to_dict()
        else:
            listing = self.listing

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service_id": service_id,
                "status": status,
                "documents": documents,
                "interfaces": interfaces,
            }
        )
        if service_name is not UNSET:
            field_dict["service_name"] = service_name
        if status_message is not UNSET:
            field_dict["status_message"] = status_message
        if routing_vars is not UNSET:
            field_dict["routing_vars"] = routing_vars
        if provider is not UNSET:
            field_dict["provider"] = provider
        if offering is not UNSET:
            field_dict["offering"] = offering
        if listing is not UNSET:
            field_dict["listing"] = listing

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_interface_public import AccessInterfacePublic
        from ..models.provider_data import ProviderData
        from ..models.service_detail_response_routing_vars_type_0 import ServiceDetailResponseRoutingVarsType0
        from ..models.service_document_item import ServiceDocumentItem
        from ..models.service_listing_data import ServiceListingData
        from ..models.service_offering_data import ServiceOfferingData

        d = dict(src_dict)
        service_id = d.pop("service_id")

        status = d.pop("status")

        documents = []
        _documents = d.pop("documents")
        for documents_item_data in _documents:
            documents_item = ServiceDocumentItem.from_dict(documents_item_data)

            documents.append(documents_item)

        interfaces = []
        _interfaces = d.pop("interfaces")
        for interfaces_item_data in _interfaces:
            interfaces_item = AccessInterfacePublic.from_dict(interfaces_item_data)

            interfaces.append(interfaces_item)

        def _parse_service_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        service_name = _parse_service_name(d.pop("service_name", UNSET))

        def _parse_status_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status_message = _parse_status_message(d.pop("status_message", UNSET))

        def _parse_routing_vars(data: object) -> None | ServiceDetailResponseRoutingVarsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_vars_type_0 = ServiceDetailResponseRoutingVarsType0.from_dict(data)

                return routing_vars_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceDetailResponseRoutingVarsType0 | Unset, data)

        routing_vars = _parse_routing_vars(d.pop("routing_vars", UNSET))

        def _parse_provider(data: object) -> None | ProviderData | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                provider_type_0 = ProviderData.from_dict(data)

                return provider_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ProviderData | Unset, data)

        provider = _parse_provider(d.pop("provider", UNSET))

        def _parse_offering(data: object) -> None | ServiceOfferingData | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                offering_type_0 = ServiceOfferingData.from_dict(data)

                return offering_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceOfferingData | Unset, data)

        offering = _parse_offering(d.pop("offering", UNSET))

        def _parse_listing(data: object) -> None | ServiceListingData | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                listing_type_0 = ServiceListingData.from_dict(data)

                return listing_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceListingData | Unset, data)

        listing = _parse_listing(d.pop("listing", UNSET))

        service_detail_response = cls(
            service_id=service_id,
            status=status,
            documents=documents,
            interfaces=interfaces,
            service_name=service_name,
            status_message=status_message,
            routing_vars=routing_vars,
            provider=provider,
            offering=offering,
            listing=listing,
        )

        service_detail_response.additional_properties = d
        return service_detail_response

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
