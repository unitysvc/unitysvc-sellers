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
  from ..models.list_price_update_response_list_price_type_0 import ListPriceUpdateResponseListPriceType0





T = TypeVar("T", bound="ListPriceUpdateResponse")



@_attrs_define
class ListPriceUpdateResponse:
    """ PATCH /seller/services/{id}/list-price.

     """

    id: str
    list_price: Union['ListPriceUpdateResponseListPriceType0', None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.list_price_update_response_list_price_type_0 import ListPriceUpdateResponseListPriceType0
        id = self.id

        list_price: Union[None, Unset, dict[str, Any]]
        if isinstance(self.list_price, Unset):
            list_price = UNSET
        elif isinstance(self.list_price, ListPriceUpdateResponseListPriceType0):
            list_price = self.list_price.to_dict()
        else:
            list_price = self.list_price


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
        })
        if list_price is not UNSET:
            field_dict["list_price"] = list_price

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_price_update_response_list_price_type_0 import ListPriceUpdateResponseListPriceType0
        d = dict(src_dict)
        id = d.pop("id")

        def _parse_list_price(data: object) -> Union['ListPriceUpdateResponseListPriceType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                list_price_type_0 = ListPriceUpdateResponseListPriceType0.from_dict(data)



                return list_price_type_0
            except: # noqa: E722
                pass
            return cast(Union['ListPriceUpdateResponseListPriceType0', None, Unset], data)

        list_price = _parse_list_price(d.pop("list_price", UNSET))


        list_price_update_response = cls(
            id=id,
            list_price=list_price,
        )


        list_price_update_response.additional_properties = d
        return list_price_update_response

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
