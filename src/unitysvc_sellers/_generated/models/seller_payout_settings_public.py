from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.payout_method_enum import check_payout_method_enum
from ..models.payout_method_enum import PayoutMethodEnum
from ..models.payout_schedule_enum import check_payout_schedule_enum
from ..models.payout_schedule_enum import PayoutScheduleEnum
from typing import cast






T = TypeVar("T", bound="SellerPayoutSettingsPublic")



@_attrs_define
class SellerPayoutSettingsPublic:
    """ Public payout settings for API responses.

     """

    preferred_payout_method: PayoutMethodEnum
    """ Supported payout methods for sellers.

    - stripe_connect: Automatic payout via Stripe Connect (requires stripe_connect_id)
    - zelle: Zelle transfer (requires email or phone)
    - check: Physical check mailed to address """
    payout_schedule: PayoutScheduleEnum
    """ Payout schedule options for sellers.

    - on_demand: Seller manually requests payouts
    - automatic: Payouts triggered automatically when threshold is met """
    payout_threshold: int | None
    payout_window_months: int | None
    zelle_email: None | str
    zelle_phone: None | str
    check_payee_name: None | str
    check_address_line1: None | str
    check_address_line2: None | str
    check_city: None | str
    check_state: None | str
    check_postal_code: None | str
    check_country: None | str
    stripe_connect_id: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        preferred_payout_method: str = self.preferred_payout_method

        payout_schedule: str = self.payout_schedule

        payout_threshold: int | None
        payout_threshold = self.payout_threshold

        payout_window_months: int | None
        payout_window_months = self.payout_window_months

        zelle_email: None | str
        zelle_email = self.zelle_email

        zelle_phone: None | str
        zelle_phone = self.zelle_phone

        check_payee_name: None | str
        check_payee_name = self.check_payee_name

        check_address_line1: None | str
        check_address_line1 = self.check_address_line1

        check_address_line2: None | str
        check_address_line2 = self.check_address_line2

        check_city: None | str
        check_city = self.check_city

        check_state: None | str
        check_state = self.check_state

        check_postal_code: None | str
        check_postal_code = self.check_postal_code

        check_country: None | str
        check_country = self.check_country

        stripe_connect_id: None | str
        stripe_connect_id = self.stripe_connect_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "preferred_payout_method": preferred_payout_method,
            "payout_schedule": payout_schedule,
            "payout_threshold": payout_threshold,
            "payout_window_months": payout_window_months,
            "zelle_email": zelle_email,
            "zelle_phone": zelle_phone,
            "check_payee_name": check_payee_name,
            "check_address_line1": check_address_line1,
            "check_address_line2": check_address_line2,
            "check_city": check_city,
            "check_state": check_state,
            "check_postal_code": check_postal_code,
            "check_country": check_country,
            "stripe_connect_id": stripe_connect_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        preferred_payout_method = check_payout_method_enum(d.pop("preferred_payout_method"))




        payout_schedule = check_payout_schedule_enum(d.pop("payout_schedule"))




        def _parse_payout_threshold(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        payout_threshold = _parse_payout_threshold(d.pop("payout_threshold"))


        def _parse_payout_window_months(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        payout_window_months = _parse_payout_window_months(d.pop("payout_window_months"))


        def _parse_zelle_email(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        zelle_email = _parse_zelle_email(d.pop("zelle_email"))


        def _parse_zelle_phone(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        zelle_phone = _parse_zelle_phone(d.pop("zelle_phone"))


        def _parse_check_payee_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        check_payee_name = _parse_check_payee_name(d.pop("check_payee_name"))


        def _parse_check_address_line1(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        check_address_line1 = _parse_check_address_line1(d.pop("check_address_line1"))


        def _parse_check_address_line2(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        check_address_line2 = _parse_check_address_line2(d.pop("check_address_line2"))


        def _parse_check_city(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        check_city = _parse_check_city(d.pop("check_city"))


        def _parse_check_state(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        check_state = _parse_check_state(d.pop("check_state"))


        def _parse_check_postal_code(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        check_postal_code = _parse_check_postal_code(d.pop("check_postal_code"))


        def _parse_check_country(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        check_country = _parse_check_country(d.pop("check_country"))


        def _parse_stripe_connect_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        stripe_connect_id = _parse_stripe_connect_id(d.pop("stripe_connect_id"))


        seller_payout_settings_public = cls(
            preferred_payout_method=preferred_payout_method,
            payout_schedule=payout_schedule,
            payout_threshold=payout_threshold,
            payout_window_months=payout_window_months,
            zelle_email=zelle_email,
            zelle_phone=zelle_phone,
            check_payee_name=check_payee_name,
            check_address_line1=check_address_line1,
            check_address_line2=check_address_line2,
            check_city=check_city,
            check_state=check_state,
            check_postal_code=check_postal_code,
            check_country=check_country,
            stripe_connect_id=stripe_connect_id,
        )


        seller_payout_settings_public.additional_properties = d
        return seller_payout_settings_public

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
