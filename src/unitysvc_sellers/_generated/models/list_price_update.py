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
  from ..models.list_price_update_set_type_0 import ListPriceUpdateSetType0





T = TypeVar("T", bound="ListPriceUpdate")



@_attrs_define
class ListPriceUpdate:
    """ Request body for updating list_price on an active service.

     """

    set_: Union['ListPriceUpdateSetType0', None, Unset] = UNSET
    remove: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.list_price_update_set_type_0 import ListPriceUpdateSetType0
        set_: Union[None, Unset, dict[str, Any]]
        if isinstance(self.set_, Unset):
            set_ = UNSET
        elif isinstance(self.set_, ListPriceUpdateSetType0):
            set_ = self.set_.to_dict()
        else:
            set_ = self.set_

        remove: Union[None, Unset, list[str]]
        if isinstance(self.remove, Unset):
            remove = UNSET
        elif isinstance(self.remove, list):
            remove = self.remove


        else:
            remove = self.remove


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if set_ is not UNSET:
            field_dict["set"] = set_
        if remove is not UNSET:
            field_dict["remove"] = remove

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_price_update_set_type_0 import ListPriceUpdateSetType0
        d = dict(src_dict)
        def _parse_set_(data: object) -> Union['ListPriceUpdateSetType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                set_type_0 = ListPriceUpdateSetType0.from_dict(data)



                return set_type_0
            except: # noqa: E722
                pass
            return cast(Union['ListPriceUpdateSetType0', None, Unset], data)

        set_ = _parse_set_(d.pop("set", UNSET))


        def _parse_remove(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                remove_type_0 = cast(list[str], data)

                return remove_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        remove = _parse_remove(d.pop("remove", UNSET))


        list_price_update = cls(
            set_=set_,
            remove=remove,
        )


        list_price_update.additional_properties = d
        return list_price_update

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
