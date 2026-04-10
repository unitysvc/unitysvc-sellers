from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.seller_balance_public import SellerBalancePublic





T = TypeVar("T", bound="SellerDetailsPublic")



@_attrs_define
class SellerDetailsPublic:
    """ Full seller details including balances for admin API.

     """

    id: UUID
    name: str
    display_name: None | str
    seller_type: str
    status: str
    seller_tier: str
    contact_email: str
    secondary_contact_email: None | str
    homepage: None | str
    description: None | str
    business_registration: None | str
    tax_id: None | str
    stripe_connect_id: None | str
    is_verified: bool
    account_manager_id: UUID
    payout_window_months: int | None
    preferred_payout_method: str
    payout_schedule: str
    payout_threshold: int | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    balances: list[SellerBalancePublic]
    account_manager_email: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.seller_balance_public import SellerBalancePublic
        id = str(self.id)

        name = self.name

        display_name: None | str
        display_name = self.display_name

        seller_type = self.seller_type

        status = self.status

        seller_tier = self.seller_tier

        contact_email = self.contact_email

        secondary_contact_email: None | str
        secondary_contact_email = self.secondary_contact_email

        homepage: None | str
        homepage = self.homepage

        description: None | str
        description = self.description

        business_registration: None | str
        business_registration = self.business_registration

        tax_id: None | str
        tax_id = self.tax_id

        stripe_connect_id: None | str
        stripe_connect_id = self.stripe_connect_id

        is_verified = self.is_verified

        account_manager_id = str(self.account_manager_id)

        payout_window_months: int | None
        payout_window_months = self.payout_window_months

        preferred_payout_method = self.preferred_payout_method

        payout_schedule = self.payout_schedule

        payout_threshold: int | None
        payout_threshold = self.payout_threshold

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        balances = []
        for balances_item_data in self.balances:
            balances_item = balances_item_data.to_dict()
            balances.append(balances_item)



        account_manager_email: None | str | Unset
        if isinstance(self.account_manager_email, Unset):
            account_manager_email = UNSET
        else:
            account_manager_email = self.account_manager_email


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "display_name": display_name,
            "seller_type": seller_type,
            "status": status,
            "seller_tier": seller_tier,
            "contact_email": contact_email,
            "secondary_contact_email": secondary_contact_email,
            "homepage": homepage,
            "description": description,
            "business_registration": business_registration,
            "tax_id": tax_id,
            "stripe_connect_id": stripe_connect_id,
            "is_verified": is_verified,
            "account_manager_id": account_manager_id,
            "payout_window_months": payout_window_months,
            "preferred_payout_method": preferred_payout_method,
            "payout_schedule": payout_schedule,
            "payout_threshold": payout_threshold,
            "created_at": created_at,
            "updated_at": updated_at,
            "balances": balances,
        })
        if account_manager_email is not UNSET:
            field_dict["account_manager_email"] = account_manager_email

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.seller_balance_public import SellerBalancePublic
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        name = d.pop("name")

        def _parse_display_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        display_name = _parse_display_name(d.pop("display_name"))


        seller_type = d.pop("seller_type")

        status = d.pop("status")

        seller_tier = d.pop("seller_tier")

        contact_email = d.pop("contact_email")

        def _parse_secondary_contact_email(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        secondary_contact_email = _parse_secondary_contact_email(d.pop("secondary_contact_email"))


        def _parse_homepage(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        homepage = _parse_homepage(d.pop("homepage"))


        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))


        def _parse_business_registration(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        business_registration = _parse_business_registration(d.pop("business_registration"))


        def _parse_tax_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        tax_id = _parse_tax_id(d.pop("tax_id"))


        def _parse_stripe_connect_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        stripe_connect_id = _parse_stripe_connect_id(d.pop("stripe_connect_id"))


        is_verified = d.pop("is_verified")

        account_manager_id = UUID(d.pop("account_manager_id"))




        def _parse_payout_window_months(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        payout_window_months = _parse_payout_window_months(d.pop("payout_window_months"))


        preferred_payout_method = d.pop("preferred_payout_method")

        payout_schedule = d.pop("payout_schedule")

        def _parse_payout_threshold(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        payout_threshold = _parse_payout_threshold(d.pop("payout_threshold"))


        created_at = isoparse(d.pop("created_at"))




        updated_at = isoparse(d.pop("updated_at"))




        balances = []
        _balances = d.pop("balances")
        for balances_item_data in (_balances):
            balances_item = SellerBalancePublic.from_dict(balances_item_data)



            balances.append(balances_item)


        def _parse_account_manager_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        account_manager_email = _parse_account_manager_email(d.pop("account_manager_email", UNSET))


        seller_details_public = cls(
            id=id,
            name=name,
            display_name=display_name,
            seller_type=seller_type,
            status=status,
            seller_tier=seller_tier,
            contact_email=contact_email,
            secondary_contact_email=secondary_contact_email,
            homepage=homepage,
            description=description,
            business_registration=business_registration,
            tax_id=tax_id,
            stripe_connect_id=stripe_connect_id,
            is_verified=is_verified,
            account_manager_id=account_manager_id,
            payout_window_months=payout_window_months,
            preferred_payout_method=preferred_payout_method,
            payout_schedule=payout_schedule,
            payout_threshold=payout_threshold,
            created_at=created_at,
            updated_at=updated_at,
            balances=balances,
            account_manager_email=account_manager_email,
        )


        seller_details_public.additional_properties = d
        return seller_details_public

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
