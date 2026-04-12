from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.routing_vars_update_response_routing_vars_type_0 import RoutingVarsUpdateResponseRoutingVarsType0





T = TypeVar("T", bound="RoutingVarsUpdateResponse")



@_attrs_define
class RoutingVarsUpdateResponse:
    """ PATCH /seller/services/{id}/routing-vars.

     """

    id: str
    routing_vars: Union['RoutingVarsUpdateResponseRoutingVarsType0', None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.routing_vars_update_response_routing_vars_type_0 import RoutingVarsUpdateResponseRoutingVarsType0
        id = self.id

        routing_vars: Union[None, Unset, dict[str, Any]]
        if isinstance(self.routing_vars, Unset):
            routing_vars = UNSET
        elif isinstance(self.routing_vars, RoutingVarsUpdateResponseRoutingVarsType0):
            routing_vars = self.routing_vars.to_dict()
        else:
            routing_vars = self.routing_vars


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
        })
        if routing_vars is not UNSET:
            field_dict["routing_vars"] = routing_vars

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.routing_vars_update_response_routing_vars_type_0 import RoutingVarsUpdateResponseRoutingVarsType0
        d = dict(src_dict)
        id = d.pop("id")

        def _parse_routing_vars(data: object) -> Union['RoutingVarsUpdateResponseRoutingVarsType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_vars_type_0 = RoutingVarsUpdateResponseRoutingVarsType0.from_dict(data)



                return routing_vars_type_0
            except: # noqa: E722
                pass
            return cast(Union['RoutingVarsUpdateResponseRoutingVarsType0', None, Unset], data)

        routing_vars = _parse_routing_vars(d.pop("routing_vars", UNSET))


        routing_vars_update_response = cls(
            id=id,
            routing_vars=routing_vars,
        )


        routing_vars_update_response.additional_properties = d
        return routing_vars_update_response

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
