from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.rate_limit_unit_enum import check_rate_limit_unit_enum
from ..models.rate_limit_unit_enum import RateLimitUnitEnum
from ..models.time_window_enum import check_time_window_enum
from ..models.time_window_enum import TimeWindowEnum
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union






T = TypeVar("T", bound="RateLimit")



@_attrs_define
class RateLimit:
    """ Store rate limiting rules for services.

     """

    limit: int
    """ Maximum allowed in the time window """
    unit: RateLimitUnitEnum
    window: TimeWindowEnum
    description: Union[None, Unset, str] = UNSET
    """ Human-readable description """
    burst_limit: Union[None, Unset, int] = UNSET
    """ Short-term burst allowance """
    is_active: Union[Unset, bool] = True
    """ Whether rate limit is active """





    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        unit: str = self.unit

        window: str = self.window

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        burst_limit: Union[None, Unset, int]
        if isinstance(self.burst_limit, Unset):
            burst_limit = UNSET
        else:
            burst_limit = self.burst_limit

        is_active = self.is_active


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "limit": limit,
            "unit": unit,
            "window": window,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if burst_limit is not UNSET:
            field_dict["burst_limit"] = burst_limit
        if is_active is not UNSET:
            field_dict["is_active"] = is_active

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        limit = d.pop("limit")

        unit = check_rate_limit_unit_enum(d.pop("unit"))




        window = check_time_window_enum(d.pop("window"))




        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_burst_limit(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        burst_limit = _parse_burst_limit(d.pop("burst_limit", UNSET))


        is_active = d.pop("is_active", UNSET)

        rate_limit = cls(
            limit=limit,
            unit=unit,
            window=window,
            description=description,
            burst_limit=burst_limit,
            is_active=is_active,
        )

        return rate_limit

