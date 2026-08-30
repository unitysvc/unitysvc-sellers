from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.rate_limit_unit_enum import RateLimitUnitEnum, check_rate_limit_unit_enum
from ..models.time_window_enum import TimeWindowEnum, check_time_window_enum
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProviderAccountRateLimit")


@_attrs_define
class ProviderAccountRateLimit:
    """One ceiling the provider grants the SELLER'S ACCOUNT.

    This is the only rate limit a seller can state truthfully. Providers scope
    their limits to the account that owns the upstream key — OpenAI, Groq and
    Anthropic at the org level, Mistral per workspace, Parasail per account —
    so the number belongs to the provider record, once, not to each of the
    seller's services.

    Declaring it per service is not merely coarse, it inverts: a 60 RPM account
    ceiling written onto 18 services authorises 1080 RPM against an account
    that grants 60. See unitysvc/unitysvc#1937.

    What a seller CANNOT state is any individual customer's allowance — that
    depends on how many customers are active at request time. The gateway
    derives that from this ceiling; nobody authors it.

    """

    name: str
    """ Seller-scoped rate-limit bucket name. Channels reference this name via rate_limit_refs /
    ops_rate_limit_refs; all matching refs for the same seller consume the same live gateway bucket. """
    limit: int
    """ Maximum allowed — in flight for `concurrent`, per window otherwise """
    unit: RateLimitUnitEnum
    window: None | TimeWindowEnum | Unset = UNSET
    """ Time window. Omitted for `concurrent`, which is a gauge rather than a counter. """
    description: None | str | Unset = UNSET
    """ Where the number came from, e.g. the provider's published limit for this tier """

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        limit = self.limit

        unit: str = self.unit

        window: None | str | Unset
        if isinstance(self.window, Unset):
            window = UNSET
        elif isinstance(self.window, str):
            window = self.window
        else:
            window = self.window

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "limit": limit,
                "unit": unit,
            }
        )
        if window is not UNSET:
            field_dict["window"] = window
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        limit = d.pop("limit")

        unit = check_rate_limit_unit_enum(d.pop("unit"))

        def _parse_window(data: object) -> None | TimeWindowEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                window_type_0 = check_time_window_enum(data)

                return window_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TimeWindowEnum | Unset, data)

        window = _parse_window(d.pop("window", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        provider_account_rate_limit = cls(
            name=name,
            limit=limit,
            unit=unit,
            window=window,
            description=description,
        )

        return provider_account_rate_limit
