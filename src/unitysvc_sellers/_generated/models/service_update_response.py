from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.service_update_response_list_price_type_0 import ServiceUpdateResponseListPriceType0
  from ..models.service_update_response_routing_vars_type_0 import ServiceUpdateResponseRoutingVarsType0





T = TypeVar("T", bound="ServiceUpdateResponse")



@_attrs_define
class ServiceUpdateResponse:
    """ Only updated fields are returned.

     """

    id: str
    status: None | str | Unset = UNSET
    visibility: None | str | Unset = UNSET
    routing_vars: None | ServiceUpdateResponseRoutingVarsType0 | Unset = UNSET
    list_price: None | ServiceUpdateResponseListPriceType0 | Unset = UNSET
    message: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_update_response_list_price_type_0 import ServiceUpdateResponseListPriceType0
        from ..models.service_update_response_routing_vars_type_0 import ServiceUpdateResponseRoutingVarsType0
        id = self.id

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        visibility: None | str | Unset
        if isinstance(self.visibility, Unset):
            visibility = UNSET
        else:
            visibility = self.visibility

        routing_vars: dict[str, Any] | None | Unset
        if isinstance(self.routing_vars, Unset):
            routing_vars = UNSET
        elif isinstance(self.routing_vars, ServiceUpdateResponseRoutingVarsType0):
            routing_vars = self.routing_vars.to_dict()
        else:
            routing_vars = self.routing_vars

        list_price: dict[str, Any] | None | Unset
        if isinstance(self.list_price, Unset):
            list_price = UNSET
        elif isinstance(self.list_price, ServiceUpdateResponseListPriceType0):
            list_price = self.list_price.to_dict()
        else:
            list_price = self.list_price

        message: None | str | Unset
        if isinstance(self.message, Unset):
            message = UNSET
        else:
            message = self.message


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
        })
        if status is not UNSET:
            field_dict["status"] = status
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if routing_vars is not UNSET:
            field_dict["routing_vars"] = routing_vars
        if list_price is not UNSET:
            field_dict["list_price"] = list_price
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_update_response_list_price_type_0 import ServiceUpdateResponseListPriceType0
        from ..models.service_update_response_routing_vars_type_0 import ServiceUpdateResponseRoutingVarsType0
        d = dict(src_dict)
        id = d.pop("id")

        def _parse_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status = _parse_status(d.pop("status", UNSET))


        def _parse_visibility(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        visibility = _parse_visibility(d.pop("visibility", UNSET))


        def _parse_routing_vars(data: object) -> None | ServiceUpdateResponseRoutingVarsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_vars_type_0 = ServiceUpdateResponseRoutingVarsType0.from_dict(data)



                return routing_vars_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceUpdateResponseRoutingVarsType0 | Unset, data)

        routing_vars = _parse_routing_vars(d.pop("routing_vars", UNSET))


        def _parse_list_price(data: object) -> None | ServiceUpdateResponseListPriceType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                list_price_type_0 = ServiceUpdateResponseListPriceType0.from_dict(data)



                return list_price_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceUpdateResponseListPriceType0 | Unset, data)

        list_price = _parse_list_price(d.pop("list_price", UNSET))


        def _parse_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        message = _parse_message(d.pop("message", UNSET))


        service_update_response = cls(
            id=id,
            status=status,
            visibility=visibility,
            routing_vars=routing_vars,
            list_price=list_price,
            message=message,
        )


        service_update_response.additional_properties = d
        return service_update_response

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
