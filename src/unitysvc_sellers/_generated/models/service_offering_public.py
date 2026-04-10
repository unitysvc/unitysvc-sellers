from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.currency_enum import check_currency_enum
from ..models.currency_enum import CurrencyEnum
from ..models.offering_status_enum import check_offering_status_enum
from ..models.offering_status_enum import OfferingStatusEnum
from ..models.service_type_enum import check_service_type_enum
from ..models.service_type_enum import ServiceTypeEnum
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.service_offering_public_details_type_0 import ServiceOfferingPublicDetailsType0
  from ..models.service_offering_public_payout_price_type_0 import ServiceOfferingPublicPayoutPriceType0





T = TypeVar("T", bound="ServiceOfferingPublic")



@_attrs_define
class ServiceOfferingPublic:
    """ Public ServiceOffering model for API responses.

     """

    id: UUID
    name: str
    service_type: ServiceTypeEnum
    """ Broad service category — defines the access pattern and protocol.

    AI modalities (vision, tools, rerank, etc.) are tracked via the
    `capabilities` list on ServiceOffering, not service_type. """
    description: str
    status: OfferingStatusEnum
    """ Status values that sellers can set for service offerings.

    Seller-accessible statuses:
    - draft: Work in progress, skipped during publish
    - ready: Complete and ready for admin review
    - deprecated: Service is retired/end of life """
    tagline: None | str | Unset = UNSET
    details: None | ServiceOfferingPublicDetailsType0 | Unset = UNSET
    currency: CurrencyEnum | Unset = UNSET
    """ Supported currency codes for pricing. """
    payout_price: None | ServiceOfferingPublicPayoutPriceType0 | Unset = UNSET
    tags: list[str] | None | Unset = UNSET
    provider_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_offering_public_details_type_0 import ServiceOfferingPublicDetailsType0
        from ..models.service_offering_public_payout_price_type_0 import ServiceOfferingPublicPayoutPriceType0
        id = str(self.id)

        name = self.name

        service_type: str = self.service_type

        description = self.description

        status: str = self.status

        tagline: None | str | Unset
        if isinstance(self.tagline, Unset):
            tagline = UNSET
        else:
            tagline = self.tagline

        details: dict[str, Any] | None | Unset
        if isinstance(self.details, Unset):
            details = UNSET
        elif isinstance(self.details, ServiceOfferingPublicDetailsType0):
            details = self.details.to_dict()
        else:
            details = self.details

        currency: str | Unset = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency


        payout_price: dict[str, Any] | None | Unset
        if isinstance(self.payout_price, Unset):
            payout_price = UNSET
        elif isinstance(self.payout_price, ServiceOfferingPublicPayoutPriceType0):
            payout_price = self.payout_price.to_dict()
        else:
            payout_price = self.payout_price

        tags: list[str] | None | Unset
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags


        else:
            tags = self.tags

        provider_name: None | str | Unset
        if isinstance(self.provider_name, Unset):
            provider_name = UNSET
        else:
            provider_name = self.provider_name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "service_type": service_type,
            "description": description,
            "status": status,
        })
        if tagline is not UNSET:
            field_dict["tagline"] = tagline
        if details is not UNSET:
            field_dict["details"] = details
        if currency is not UNSET:
            field_dict["currency"] = currency
        if payout_price is not UNSET:
            field_dict["payout_price"] = payout_price
        if tags is not UNSET:
            field_dict["tags"] = tags
        if provider_name is not UNSET:
            field_dict["provider_name"] = provider_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_offering_public_details_type_0 import ServiceOfferingPublicDetailsType0
        from ..models.service_offering_public_payout_price_type_0 import ServiceOfferingPublicPayoutPriceType0
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        name = d.pop("name")

        service_type = check_service_type_enum(d.pop("service_type"))




        description = d.pop("description")

        status = check_offering_status_enum(d.pop("status"))




        def _parse_tagline(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        tagline = _parse_tagline(d.pop("tagline", UNSET))


        def _parse_details(data: object) -> None | ServiceOfferingPublicDetailsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                details_type_0 = ServiceOfferingPublicDetailsType0.from_dict(data)



                return details_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceOfferingPublicDetailsType0 | Unset, data)

        details = _parse_details(d.pop("details", UNSET))


        _currency = d.pop("currency", UNSET)
        currency: CurrencyEnum | Unset
        if isinstance(_currency,  Unset):
            currency = UNSET
        else:
            currency = check_currency_enum(_currency)




        def _parse_payout_price(data: object) -> None | ServiceOfferingPublicPayoutPriceType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                payout_price_type_0 = ServiceOfferingPublicPayoutPriceType0.from_dict(data)



                return payout_price_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceOfferingPublicPayoutPriceType0 | Unset, data)

        payout_price = _parse_payout_price(d.pop("payout_price", UNSET))


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


        def _parse_provider_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider_name = _parse_provider_name(d.pop("provider_name", UNSET))


        service_offering_public = cls(
            id=id,
            name=name,
            service_type=service_type,
            description=description,
            status=status,
            tagline=tagline,
            details=details,
            currency=currency,
            payout_price=payout_price,
            tags=tags,
            provider_name=provider_name,
        )


        service_offering_public.additional_properties = d
        return service_offering_public

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
