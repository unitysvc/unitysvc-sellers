from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.service_detail_response_listing import ServiceDetailResponseListing
  from ..models.service_detail_response_offering import ServiceDetailResponseOffering
  from ..models.service_detail_response_provider import ServiceDetailResponseProvider
  from ..models.service_detail_response_routing_vars_type_0 import ServiceDetailResponseRoutingVarsType0
  from ..models.service_document_item import ServiceDocumentItem
  from ..models.service_interface_item import ServiceInterfaceItem





T = TypeVar("T", bound="ServiceDetailResponse")



@_attrs_define
class ServiceDetailResponse:
    """ GET /seller/services/{id} — full service record with nested
    documents and access interfaces.

    Replaces the previously-separate /documents and /interfaces sub-endpoints
    by embedding them here, since the test runner always fetches all three
    together.

     """

    service_id: str
    status: str
    provider: ServiceDetailResponseProvider
    offering: ServiceDetailResponseOffering
    listing: ServiceDetailResponseListing
    documents: list[ServiceDocumentItem]
    interfaces: list[ServiceInterfaceItem]
    service_name: None | str | Unset = UNSET
    status_message: None | str | Unset = UNSET
    routing_vars: None | ServiceDetailResponseRoutingVarsType0 | Unset = UNSET
    provider_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_detail_response_listing import ServiceDetailResponseListing
        from ..models.service_detail_response_offering import ServiceDetailResponseOffering
        from ..models.service_detail_response_provider import ServiceDetailResponseProvider
        from ..models.service_detail_response_routing_vars_type_0 import ServiceDetailResponseRoutingVarsType0
        from ..models.service_document_item import ServiceDocumentItem
        from ..models.service_interface_item import ServiceInterfaceItem
        service_id = self.service_id

        status = self.status

        provider = self.provider.to_dict()

        offering = self.offering.to_dict()

        listing = self.listing.to_dict()

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

        provider_name: None | str | Unset
        if isinstance(self.provider_name, Unset):
            provider_name = UNSET
        else:
            provider_name = self.provider_name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "service_id": service_id,
            "status": status,
            "provider": provider,
            "offering": offering,
            "listing": listing,
            "documents": documents,
            "interfaces": interfaces,
        })
        if service_name is not UNSET:
            field_dict["service_name"] = service_name
        if status_message is not UNSET:
            field_dict["status_message"] = status_message
        if routing_vars is not UNSET:
            field_dict["routing_vars"] = routing_vars
        if provider_name is not UNSET:
            field_dict["provider_name"] = provider_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_detail_response_listing import ServiceDetailResponseListing
        from ..models.service_detail_response_offering import ServiceDetailResponseOffering
        from ..models.service_detail_response_provider import ServiceDetailResponseProvider
        from ..models.service_detail_response_routing_vars_type_0 import ServiceDetailResponseRoutingVarsType0
        from ..models.service_document_item import ServiceDocumentItem
        from ..models.service_interface_item import ServiceInterfaceItem
        d = dict(src_dict)
        service_id = d.pop("service_id")

        status = d.pop("status")

        provider = ServiceDetailResponseProvider.from_dict(d.pop("provider"))




        offering = ServiceDetailResponseOffering.from_dict(d.pop("offering"))




        listing = ServiceDetailResponseListing.from_dict(d.pop("listing"))




        documents = []
        _documents = d.pop("documents")
        for documents_item_data in (_documents):
            documents_item = ServiceDocumentItem.from_dict(documents_item_data)



            documents.append(documents_item)


        interfaces = []
        _interfaces = d.pop("interfaces")
        for interfaces_item_data in (_interfaces):
            interfaces_item = ServiceInterfaceItem.from_dict(interfaces_item_data)



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


        def _parse_provider_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider_name = _parse_provider_name(d.pop("provider_name", UNSET))


        service_detail_response = cls(
            service_id=service_id,
            status=status,
            provider=provider,
            offering=offering,
            listing=listing,
            documents=documents,
            interfaces=interfaces,
            service_name=service_name,
            status_message=status_message,
            routing_vars=routing_vars,
            provider_name=provider_name,
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
