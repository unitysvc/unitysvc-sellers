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
from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="SellerPayoutSettingsUpdate")



@_attrs_define
class SellerPayoutSettingsUpdate:
    """ Schema for updating only payout settings.

    This is a specialized update schema that only includes payout-related fields,
    making it easier for sellers to update their payout preferences.

     """

    preferred_payout_method: None | PayoutMethodEnum | Unset = UNSET
    payout_schedule: None | PayoutScheduleEnum | Unset = UNSET
    payout_threshold: int | None | Unset = UNSET
    """ Minimum balance (in cents) to trigger automatic payout """
    zelle_email: None | str | Unset = UNSET
    zelle_phone: None | str | Unset = UNSET
    check_payee_name: None | str | Unset = UNSET
    check_address_line1: None | str | Unset = UNSET
    check_address_line2: None | str | Unset = UNSET
    check_city: None | str | Unset = UNSET
    check_state: None | str | Unset = UNSET
    check_postal_code: None | str | Unset = UNSET
    check_country: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        preferred_payout_method: None | str | Unset
        if isinstance(self.preferred_payout_method, Unset):
            preferred_payout_method = UNSET
        elif isinstance(self.preferred_payout_method, str):
            preferred_payout_method = self.preferred_payout_method
        else:
            preferred_payout_method = self.preferred_payout_method

        payout_schedule: None | str | Unset
        if isinstance(self.payout_schedule, Unset):
            payout_schedule = UNSET
        elif isinstance(self.payout_schedule, str):
            payout_schedule = self.payout_schedule
        else:
            payout_schedule = self.payout_schedule

        payout_threshold: int | None | Unset
        if isinstance(self.payout_threshold, Unset):
            payout_threshold = UNSET
        else:
            payout_threshold = self.payout_threshold

        zelle_email: None | str | Unset
        if isinstance(self.zelle_email, Unset):
            zelle_email = UNSET
        else:
            zelle_email = self.zelle_email

        zelle_phone: None | str | Unset
        if isinstance(self.zelle_phone, Unset):
            zelle_phone = UNSET
        else:
            zelle_phone = self.zelle_phone

        check_payee_name: None | str | Unset
        if isinstance(self.check_payee_name, Unset):
            check_payee_name = UNSET
        else:
            check_payee_name = self.check_payee_name

        check_address_line1: None | str | Unset
        if isinstance(self.check_address_line1, Unset):
            check_address_line1 = UNSET
        else:
            check_address_line1 = self.check_address_line1

        check_address_line2: None | str | Unset
        if isinstance(self.check_address_line2, Unset):
            check_address_line2 = UNSET
        else:
            check_address_line2 = self.check_address_line2

        check_city: None | str | Unset
        if isinstance(self.check_city, Unset):
            check_city = UNSET
        else:
            check_city = self.check_city

        check_state: None | str | Unset
        if isinstance(self.check_state, Unset):
            check_state = UNSET
        else:
            check_state = self.check_state

        check_postal_code: None | str | Unset
        if isinstance(self.check_postal_code, Unset):
            check_postal_code = UNSET
        else:
            check_postal_code = self.check_postal_code

        check_country: None | str | Unset
        if isinstance(self.check_country, Unset):
            check_country = UNSET
        else:
            check_country = self.check_country


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if preferred_payout_method is not UNSET:
            field_dict["preferred_payout_method"] = preferred_payout_method
        if payout_schedule is not UNSET:
            field_dict["payout_schedule"] = payout_schedule
        if payout_threshold is not UNSET:
            field_dict["payout_threshold"] = payout_threshold
        if zelle_email is not UNSET:
            field_dict["zelle_email"] = zelle_email
        if zelle_phone is not UNSET:
            field_dict["zelle_phone"] = zelle_phone
        if check_payee_name is not UNSET:
            field_dict["check_payee_name"] = check_payee_name
        if check_address_line1 is not UNSET:
            field_dict["check_address_line1"] = check_address_line1
        if check_address_line2 is not UNSET:
            field_dict["check_address_line2"] = check_address_line2
        if check_city is not UNSET:
            field_dict["check_city"] = check_city
        if check_state is not UNSET:
            field_dict["check_state"] = check_state
        if check_postal_code is not UNSET:
            field_dict["check_postal_code"] = check_postal_code
        if check_country is not UNSET:
            field_dict["check_country"] = check_country

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_preferred_payout_method(data: object) -> None | PayoutMethodEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                preferred_payout_method_type_0 = check_payout_method_enum(data)



                return preferred_payout_method_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PayoutMethodEnum | Unset, data)

        preferred_payout_method = _parse_preferred_payout_method(d.pop("preferred_payout_method", UNSET))


        def _parse_payout_schedule(data: object) -> None | PayoutScheduleEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                payout_schedule_type_0 = check_payout_schedule_enum(data)



                return payout_schedule_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PayoutScheduleEnum | Unset, data)

        payout_schedule = _parse_payout_schedule(d.pop("payout_schedule", UNSET))


        def _parse_payout_threshold(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        payout_threshold = _parse_payout_threshold(d.pop("payout_threshold", UNSET))


        def _parse_zelle_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        zelle_email = _parse_zelle_email(d.pop("zelle_email", UNSET))


        def _parse_zelle_phone(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        zelle_phone = _parse_zelle_phone(d.pop("zelle_phone", UNSET))


        def _parse_check_payee_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_payee_name = _parse_check_payee_name(d.pop("check_payee_name", UNSET))


        def _parse_check_address_line1(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_address_line1 = _parse_check_address_line1(d.pop("check_address_line1", UNSET))


        def _parse_check_address_line2(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_address_line2 = _parse_check_address_line2(d.pop("check_address_line2", UNSET))


        def _parse_check_city(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_city = _parse_check_city(d.pop("check_city", UNSET))


        def _parse_check_state(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_state = _parse_check_state(d.pop("check_state", UNSET))


        def _parse_check_postal_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_postal_code = _parse_check_postal_code(d.pop("check_postal_code", UNSET))


        def _parse_check_country(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_country = _parse_check_country(d.pop("check_country", UNSET))


        seller_payout_settings_update = cls(
            preferred_payout_method=preferred_payout_method,
            payout_schedule=payout_schedule,
            payout_threshold=payout_threshold,
            zelle_email=zelle_email,
            zelle_phone=zelle_phone,
            check_payee_name=check_payee_name,
            check_address_line1=check_address_line1,
            check_address_line2=check_address_line2,
            check_city=check_city,
            check_state=check_state,
            check_postal_code=check_postal_code,
            check_country=check_country,
        )


        seller_payout_settings_update.additional_properties = d
        return seller_payout_settings_update

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
