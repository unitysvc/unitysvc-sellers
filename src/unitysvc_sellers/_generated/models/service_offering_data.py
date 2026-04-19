from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.currency_enum import CurrencyEnum, check_currency_enum
from ..models.offering_status_enum import OfferingStatusEnum, check_offering_status_enum
from ..models.service_type_enum import ServiceTypeEnum, check_service_type_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_offering_data_details_type_0 import ServiceOfferingDataDetailsType0
    from ..models.service_offering_data_documents_type_0 import ServiceOfferingDataDocumentsType0
    from ..models.service_offering_data_payout_price_type_0 import ServiceOfferingDataPayoutPriceType0
    from ..models.service_offering_data_upstream_access_config_type_0 import (
        ServiceOfferingDataUpstreamAccessConfigType0,
    )


T = TypeVar("T", bound="ServiceOfferingData")


@_attrs_define
class ServiceOfferingData:
    """Base data structure for service offering information.

    This model contains the core fields needed to describe a service offering,
    without file-specific validation fields. It serves as:

    1. The base class for `OfferingV1` in unitysvc-core (with additional
       schema_version and time_created fields for file validation)

    2. The data structure imported by unitysvc backend for:
       - API payload validation
       - Database comparison logic in find_and_compare_service_offering()
       - Publish operations from CLI

    Key characteristics:
    - status maps to database 'status' field
    - Contains all user-provided data without system-generated IDs
    - Does not include permission/audit fields (handled by backend CRUD layer)
    - Provider relationship is determined by file location (SDK mode) or
      by being published together in a single API call (API mode)

    """

    name: str
    """ Technical service name (e.g., 'gpt-4') """
    display_name: None | str | Unset = UNSET
    """ Human-readable service name for display (e.g., 'GPT-4 Turbo', 'Claude 3 Opus') """
    service_type: ServiceTypeEnum | Unset = UNSET
    """ Broad service category — defines the access pattern and protocol.

    AI modalities (vision, tools, rerank, etc.) are tracked via the
    `capabilities` list on ServiceOffering, not service_type. """
    capabilities: list[str] | Unset = UNSET
    """ Specific features this service provides (e.g., 'text_to_speech', 'embedding') """
    description: None | str | Unset = UNSET
    """ Service description """
    tagline: None | str | Unset = UNSET
    """ Short elevator pitch or description for the service """
    status: OfferingStatusEnum | Unset = UNSET
    """ Status values that sellers can set for service offerings.

    Seller-accessible statuses:
    - draft: Work in progress, skipped during publish
    - ready: Complete and ready for admin review
    - deprecated: Service is retired/end of life """
    details: None | ServiceOfferingDataDetailsType0 | Unset = UNSET
    """ Static technical specifications and features """
    payout_price: None | ServiceOfferingDataPayoutPriceType0 | Unset = UNSET
    """ Payout pricing: How to calculate seller payout """
    upstream_access_config: None | ServiceOfferingDataUpstreamAccessConfigType0 | Unset = UNSET
    """ Upstream access interfaces, keyed by name """
    documents: None | ServiceOfferingDataDocumentsType0 | Unset = UNSET
    """ Documents associated with the service, keyed by title """
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    tags: list[str] | None | Unset = UNSET
    """ List of tags for the service (arbitrary strings) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_offering_data_details_type_0 import ServiceOfferingDataDetailsType0
        from ..models.service_offering_data_documents_type_0 import ServiceOfferingDataDocumentsType0
        from ..models.service_offering_data_payout_price_type_0 import ServiceOfferingDataPayoutPriceType0
        from ..models.service_offering_data_upstream_access_config_type_0 import (
            ServiceOfferingDataUpstreamAccessConfigType0,
        )

        name = self.name

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        service_type: str | Unset = UNSET
        if not isinstance(self.service_type, Unset):
            service_type = self.service_type

        capabilities: list[str] | Unset = UNSET
        if not isinstance(self.capabilities, Unset):
            capabilities = self.capabilities

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        tagline: None | str | Unset
        if isinstance(self.tagline, Unset):
            tagline = UNSET
        else:
            tagline = self.tagline

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        details: dict[str, Any] | None | Unset
        if isinstance(self.details, Unset):
            details = UNSET
        elif isinstance(self.details, ServiceOfferingDataDetailsType0):
            details = self.details.to_dict()
        else:
            details = self.details

        payout_price: dict[str, Any] | None | Unset
        if isinstance(self.payout_price, Unset):
            payout_price = UNSET
        elif isinstance(self.payout_price, ServiceOfferingDataPayoutPriceType0):
            payout_price = self.payout_price.to_dict()
        else:
            payout_price = self.payout_price

        upstream_access_config: dict[str, Any] | None | Unset
        if isinstance(self.upstream_access_config, Unset):
            upstream_access_config = UNSET
        elif isinstance(self.upstream_access_config, ServiceOfferingDataUpstreamAccessConfigType0):
            upstream_access_config = self.upstream_access_config.to_dict()
        else:
            upstream_access_config = self.upstream_access_config

        documents: dict[str, Any] | None | Unset
        if isinstance(self.documents, Unset):
            documents = UNSET
        elif isinstance(self.documents, ServiceOfferingDataDocumentsType0):
            documents = self.documents.to_dict()
        else:
            documents = self.documents

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency

        tags: list[str] | None | Unset
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags

        else:
            tags = self.tags

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if service_type is not UNSET:
            field_dict["service_type"] = service_type
        if capabilities is not UNSET:
            field_dict["capabilities"] = capabilities
        if description is not UNSET:
            field_dict["description"] = description
        if tagline is not UNSET:
            field_dict["tagline"] = tagline
        if status is not UNSET:
            field_dict["status"] = status
        if details is not UNSET:
            field_dict["details"] = details
        if payout_price is not UNSET:
            field_dict["payout_price"] = payout_price
        if upstream_access_config is not UNSET:
            field_dict["upstream_access_config"] = upstream_access_config
        if documents is not UNSET:
            field_dict["documents"] = documents
        if currency is not UNSET:
            field_dict["currency"] = currency
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_offering_data_details_type_0 import ServiceOfferingDataDetailsType0
        from ..models.service_offering_data_documents_type_0 import ServiceOfferingDataDocumentsType0
        from ..models.service_offering_data_payout_price_type_0 import ServiceOfferingDataPayoutPriceType0
        from ..models.service_offering_data_upstream_access_config_type_0 import (
            ServiceOfferingDataUpstreamAccessConfigType0,
        )

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        _service_type = d.pop("service_type", UNSET)
        service_type: ServiceTypeEnum | Unset
        if isinstance(_service_type, Unset):
            service_type = UNSET
        else:
            service_type = check_service_type_enum(_service_type)

        capabilities = cast(list[str], d.pop("capabilities", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_tagline(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        tagline = _parse_tagline(d.pop("tagline", UNSET))

        _status = d.pop("status", UNSET)
        status: OfferingStatusEnum | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = check_offering_status_enum(_status)

        def _parse_details(data: object) -> None | ServiceOfferingDataDetailsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                details_type_0 = ServiceOfferingDataDetailsType0.from_dict(data)

                return details_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceOfferingDataDetailsType0 | Unset, data)

        details = _parse_details(d.pop("details", UNSET))

        def _parse_payout_price(data: object) -> None | ServiceOfferingDataPayoutPriceType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                payout_price_type_0 = ServiceOfferingDataPayoutPriceType0.from_dict(data)

                return payout_price_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceOfferingDataPayoutPriceType0 | Unset, data)

        payout_price = _parse_payout_price(d.pop("payout_price", UNSET))

        def _parse_upstream_access_config(data: object) -> None | ServiceOfferingDataUpstreamAccessConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                upstream_access_config_type_0 = ServiceOfferingDataUpstreamAccessConfigType0.from_dict(data)

                return upstream_access_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceOfferingDataUpstreamAccessConfigType0 | Unset, data)

        upstream_access_config = _parse_upstream_access_config(d.pop("upstream_access_config", UNSET))

        def _parse_documents(data: object) -> None | ServiceOfferingDataDocumentsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                documents_type_0 = ServiceOfferingDataDocumentsType0.from_dict(data)

                return documents_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceOfferingDataDocumentsType0 | Unset, data)

        documents = _parse_documents(d.pop("documents", UNSET))

        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency, Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)

        def _parse_tags(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = cast(list[str], data)

                return tags_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        tags = _parse_tags(d.pop("tags", UNSET))

        service_offering_data = cls(
            name=name,
            display_name=display_name,
            service_type=service_type,
            capabilities=capabilities,
            description=description,
            tagline=tagline,
            status=status,
            details=details,
            payout_price=payout_price,
            upstream_access_config=upstream_access_config,
            documents=documents,
            currency=currency,
            tags=tags,
        )

        service_offering_data.additional_properties = d
        return service_offering_data

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
