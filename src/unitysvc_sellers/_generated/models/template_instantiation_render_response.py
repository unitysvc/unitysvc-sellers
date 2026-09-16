from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.template_instantiation_render_response_listing_data import (
        TemplateInstantiationRenderResponseListingData,
    )
    from ..models.template_instantiation_render_response_offering_data import (
        TemplateInstantiationRenderResponseOfferingData,
    )
    from ..models.template_instantiation_render_response_provider_data import (
        TemplateInstantiationRenderResponseProviderData,
    )


T = TypeVar("T", bound="TemplateInstantiationRenderResponse")


@_attrs_define
class TemplateInstantiationRenderResponse:
    """Fully rendered service content for inspection, without persistence."""

    provider_data: TemplateInstantiationRenderResponseProviderData
    offering_data: TemplateInstantiationRenderResponseOfferingData
    listing_data: TemplateInstantiationRenderResponseListingData
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.template_instantiation_render_response_listing_data import (
            TemplateInstantiationRenderResponseListingData,
        )
        from ..models.template_instantiation_render_response_offering_data import (
            TemplateInstantiationRenderResponseOfferingData,
        )
        from ..models.template_instantiation_render_response_provider_data import (
            TemplateInstantiationRenderResponseProviderData,
        )

        provider_data = self.provider_data.to_dict()

        offering_data = self.offering_data.to_dict()

        listing_data = self.listing_data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider_data": provider_data,
                "offering_data": offering_data,
                "listing_data": listing_data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.template_instantiation_render_response_listing_data import (
            TemplateInstantiationRenderResponseListingData,
        )
        from ..models.template_instantiation_render_response_offering_data import (
            TemplateInstantiationRenderResponseOfferingData,
        )
        from ..models.template_instantiation_render_response_provider_data import (
            TemplateInstantiationRenderResponseProviderData,
        )

        d = dict(src_dict)
        provider_data = TemplateInstantiationRenderResponseProviderData.from_dict(d.pop("provider_data"))

        offering_data = TemplateInstantiationRenderResponseOfferingData.from_dict(d.pop("offering_data"))

        listing_data = TemplateInstantiationRenderResponseListingData.from_dict(d.pop("listing_data"))

        template_instantiation_render_response = cls(
            provider_data=provider_data,
            offering_data=offering_data,
            listing_data=listing_data,
        )

        template_instantiation_render_response.additional_properties = d
        return template_instantiation_render_response

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
