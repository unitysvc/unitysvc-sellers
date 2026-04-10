from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="AttachPaymentMethodRequest")



@_attrs_define
class AttachPaymentMethodRequest:
    """ Request for attaching a payment method to an existing customer.

     """

    payment_method_id: str
    """ Unattached PM from Stripe Elements """
    set_as_default: bool | Unset = False
    """ Set this PM as default for the customer """
    nickname: None | str | Unset = UNSET
    """ Optional display name for the card (e.g. 'Personal Visa') """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        payment_method_id = self.payment_method_id

        set_as_default = self.set_as_default

        nickname: None | str | Unset
        if isinstance(self.nickname, Unset):
            nickname = UNSET
        else:
            nickname = self.nickname


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "payment_method_id": payment_method_id,
        })
        if set_as_default is not UNSET:
            field_dict["set_as_default"] = set_as_default
        if nickname is not UNSET:
            field_dict["nickname"] = nickname

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        payment_method_id = d.pop("payment_method_id")

        set_as_default = d.pop("set_as_default", UNSET)

        def _parse_nickname(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        nickname = _parse_nickname(d.pop("nickname", UNSET))


        attach_payment_method_request = cls(
            payment_method_id=payment_method_id,
            set_as_default=set_as_default,
            nickname=nickname,
        )


        attach_payment_method_request.additional_properties = d
        return attach_payment_method_request

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
