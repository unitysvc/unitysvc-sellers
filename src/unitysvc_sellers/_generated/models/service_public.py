from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.service_status_enum import check_service_status_enum
from ..models.service_status_enum import ServiceStatusEnum
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.service_public_routing_vars_type_0 import ServicePublicRoutingVarsType0





T = TypeVar("T", bound="ServicePublic")



@_attrs_define
class ServicePublic:
    """ Public Service model for API responses.

    Note: name, display_name, and other derived fields are populated from
    the materialized view (ServiceMView) in the API layer.

     """

    id: UUID
    seller_id: UUID
    offering_id: UUID
    listing_id: UUID
    status: ServiceStatusEnum
    """ Status of a Service (identity layer).

    Workflow:
    - draft: Not yet submitted for review (default, seller still editing)
    - pending: Tests running (transient, after seller publishes)
    - review: Tests passed, awaiting admin approval
    - active: Approved and operational, accepting requests
    - rejected: Admin rejected (seller can revise and republish)
    - suspended: Admin suspended due to issues/violations
    - deprecated: Service ending """
    created_at: datetime.datetime
    provider_id: Union[None, UUID, Unset] = UNSET
    revision_of: Union[None, UUID, Unset] = UNSET
    pending_revision_id: Union[None, UUID, Unset] = UNSET
    name: Union[None, Unset, str] = UNSET
    display_name: Union[None, Unset, str] = UNSET
    service_type: Union[None, Unset, str] = UNSET
    provider_name: Union[None, Unset, str] = UNSET
    listing_type: Union[None, Unset, str] = UNSET
    status_message: Union[None, Unset, str] = UNSET
    is_featured: Union[Unset, bool] = False
    routing_vars: Union['ServicePublicRoutingVarsType0', None, Unset] = UNSET
    review_count: Union[Unset, int] = 0
    average_rating: Union[None, Unset, float] = UNSET
    ops_subscription_id: Union[None, UUID, Unset] = UNSET
    ops_customer_id: Union[None, UUID, Unset] = UNSET
    updated_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_public_routing_vars_type_0 import ServicePublicRoutingVarsType0
        id = str(self.id)

        seller_id = str(self.seller_id)

        offering_id = str(self.offering_id)

        listing_id = str(self.listing_id)

        status: str = self.status

        created_at = self.created_at.isoformat()

        provider_id: Union[None, Unset, str]
        if isinstance(self.provider_id, Unset):
            provider_id = UNSET
        elif isinstance(self.provider_id, UUID):
            provider_id = str(self.provider_id)
        else:
            provider_id = self.provider_id

        revision_of: Union[None, Unset, str]
        if isinstance(self.revision_of, Unset):
            revision_of = UNSET
        elif isinstance(self.revision_of, UUID):
            revision_of = str(self.revision_of)
        else:
            revision_of = self.revision_of

        pending_revision_id: Union[None, Unset, str]
        if isinstance(self.pending_revision_id, Unset):
            pending_revision_id = UNSET
        elif isinstance(self.pending_revision_id, UUID):
            pending_revision_id = str(self.pending_revision_id)
        else:
            pending_revision_id = self.pending_revision_id

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

        service_type: Union[None, Unset, str]
        if isinstance(self.service_type, Unset):
            service_type = UNSET
        else:
            service_type = self.service_type

        provider_name: Union[None, Unset, str]
        if isinstance(self.provider_name, Unset):
            provider_name = UNSET
        else:
            provider_name = self.provider_name

        listing_type: Union[None, Unset, str]
        if isinstance(self.listing_type, Unset):
            listing_type = UNSET
        else:
            listing_type = self.listing_type

        status_message: Union[None, Unset, str]
        if isinstance(self.status_message, Unset):
            status_message = UNSET
        else:
            status_message = self.status_message

        is_featured = self.is_featured

        routing_vars: Union[None, Unset, dict[str, Any]]
        if isinstance(self.routing_vars, Unset):
            routing_vars = UNSET
        elif isinstance(self.routing_vars, ServicePublicRoutingVarsType0):
            routing_vars = self.routing_vars.to_dict()
        else:
            routing_vars = self.routing_vars

        review_count = self.review_count

        average_rating: Union[None, Unset, float]
        if isinstance(self.average_rating, Unset):
            average_rating = UNSET
        else:
            average_rating = self.average_rating

        ops_subscription_id: Union[None, Unset, str]
        if isinstance(self.ops_subscription_id, Unset):
            ops_subscription_id = UNSET
        elif isinstance(self.ops_subscription_id, UUID):
            ops_subscription_id = str(self.ops_subscription_id)
        else:
            ops_subscription_id = self.ops_subscription_id

        ops_customer_id: Union[None, Unset, str]
        if isinstance(self.ops_customer_id, Unset):
            ops_customer_id = UNSET
        elif isinstance(self.ops_customer_id, UUID):
            ops_customer_id = str(self.ops_customer_id)
        else:
            ops_customer_id = self.ops_customer_id

        updated_at: Union[None, Unset, str]
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "seller_id": seller_id,
            "offering_id": offering_id,
            "listing_id": listing_id,
            "status": status,
            "created_at": created_at,
        })
        if provider_id is not UNSET:
            field_dict["provider_id"] = provider_id
        if revision_of is not UNSET:
            field_dict["revision_of"] = revision_of
        if pending_revision_id is not UNSET:
            field_dict["pending_revision_id"] = pending_revision_id
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if service_type is not UNSET:
            field_dict["service_type"] = service_type
        if provider_name is not UNSET:
            field_dict["provider_name"] = provider_name
        if listing_type is not UNSET:
            field_dict["listing_type"] = listing_type
        if status_message is not UNSET:
            field_dict["status_message"] = status_message
        if is_featured is not UNSET:
            field_dict["is_featured"] = is_featured
        if routing_vars is not UNSET:
            field_dict["routing_vars"] = routing_vars
        if review_count is not UNSET:
            field_dict["review_count"] = review_count
        if average_rating is not UNSET:
            field_dict["average_rating"] = average_rating
        if ops_subscription_id is not UNSET:
            field_dict["ops_subscription_id"] = ops_subscription_id
        if ops_customer_id is not UNSET:
            field_dict["ops_customer_id"] = ops_customer_id
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_public_routing_vars_type_0 import ServicePublicRoutingVarsType0
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        seller_id = UUID(d.pop("seller_id"))




        offering_id = UUID(d.pop("offering_id"))




        listing_id = UUID(d.pop("listing_id"))




        status = check_service_status_enum(d.pop("status"))




        created_at = isoparse(d.pop("created_at"))




        def _parse_provider_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                provider_id_type_0 = UUID(data)



                return provider_id_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        provider_id = _parse_provider_id(d.pop("provider_id", UNSET))


        def _parse_revision_of(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                revision_of_type_0 = UUID(data)



                return revision_of_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        revision_of = _parse_revision_of(d.pop("revision_of", UNSET))


        def _parse_pending_revision_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                pending_revision_id_type_0 = UUID(data)



                return pending_revision_id_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        pending_revision_id = _parse_pending_revision_id(d.pop("pending_revision_id", UNSET))


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


        def _parse_service_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        service_type = _parse_service_type(d.pop("service_type", UNSET))


        def _parse_provider_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        provider_name = _parse_provider_name(d.pop("provider_name", UNSET))


        def _parse_listing_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        listing_type = _parse_listing_type(d.pop("listing_type", UNSET))


        def _parse_status_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        status_message = _parse_status_message(d.pop("status_message", UNSET))


        is_featured = d.pop("is_featured", UNSET)

        def _parse_routing_vars(data: object) -> Union['ServicePublicRoutingVarsType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_vars_type_0 = ServicePublicRoutingVarsType0.from_dict(data)



                return routing_vars_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServicePublicRoutingVarsType0', None, Unset], data)

        routing_vars = _parse_routing_vars(d.pop("routing_vars", UNSET))


        review_count = d.pop("review_count", UNSET)

        def _parse_average_rating(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        average_rating = _parse_average_rating(d.pop("average_rating", UNSET))


        def _parse_ops_subscription_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                ops_subscription_id_type_0 = UUID(data)



                return ops_subscription_id_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        ops_subscription_id = _parse_ops_subscription_id(d.pop("ops_subscription_id", UNSET))


        def _parse_ops_customer_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                ops_customer_id_type_0 = UUID(data)



                return ops_customer_id_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        ops_customer_id = _parse_ops_customer_id(d.pop("ops_customer_id", UNSET))


        def _parse_updated_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)



                return updated_at_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))


        service_public = cls(
            id=id,
            seller_id=seller_id,
            offering_id=offering_id,
            listing_id=listing_id,
            status=status,
            created_at=created_at,
            provider_id=provider_id,
            revision_of=revision_of,
            pending_revision_id=pending_revision_id,
            name=name,
            display_name=display_name,
            service_type=service_type,
            provider_name=provider_name,
            listing_type=listing_type,
            status_message=status_message,
            is_featured=is_featured,
            routing_vars=routing_vars,
            review_count=review_count,
            average_rating=average_rating,
            ops_subscription_id=ops_subscription_id,
            ops_customer_id=ops_customer_id,
            updated_at=updated_at,
        )


        service_public.additional_properties = d
        return service_public

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
