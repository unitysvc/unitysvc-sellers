from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.service_status_enum import ServiceStatusEnum, check_service_status_enum
from ..models.service_visibility_enum import ServiceVisibilityEnum, check_service_visibility_enum
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.service_update_price_type_0 import ServiceUpdatePriceType0
    from ..models.service_update_routing_vars_type_0 import ServiceUpdateRoutingVarsType0


T = TypeVar("T", bound="ServiceUpdate")


@_attrs_define
class ServiceUpdate:
    """Unified request body for updating a service.

    All fields are optional — include only the fields you want to change.
    Multiple fields can be updated in a single request.

    ``routing_vars`` and ``price`` accept two forms:

    - **Full replacement** — a plain dict replaces the entire value::

        {"routing_vars": {"region": "us-east", "count": 42}}

    - **Partial update** — a dict with ``set`` and/or ``remove`` keys::

        {"routing_vars": {"set": {"count": 43}, "remove": ["region"]}}

    """

    status: None | ServiceStatusEnum | Unset = UNSET
    run_tests: bool | Unset = True
    visibility: None | ServiceVisibilityEnum | Unset = UNSET
    routing_vars: None | ServiceUpdateRoutingVarsType0 | Unset = UNSET
    price: None | ServiceUpdatePriceType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.service_update_price_type_0 import ServiceUpdatePriceType0
        from ..models.service_update_routing_vars_type_0 import ServiceUpdateRoutingVarsType0

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, str):
            status = self.status
        else:
            status = self.status

        run_tests = self.run_tests

        visibility: None | str | Unset
        if isinstance(self.visibility, Unset):
            visibility = UNSET
        elif isinstance(self.visibility, str):
            visibility = self.visibility
        else:
            visibility = self.visibility

        routing_vars: dict[str, Any] | None | Unset
        if isinstance(self.routing_vars, Unset):
            routing_vars = UNSET
        elif isinstance(self.routing_vars, ServiceUpdateRoutingVarsType0):
            routing_vars = self.routing_vars.to_dict()
        else:
            routing_vars = self.routing_vars

        price: dict[str, Any] | None | Unset
        if isinstance(self.price, Unset):
            price = UNSET
        elif isinstance(self.price, ServiceUpdatePriceType0):
            price = self.price.to_dict()
        else:
            price = self.price

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if run_tests is not UNSET:
            field_dict["run_tests"] = run_tests
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if routing_vars is not UNSET:
            field_dict["routing_vars"] = routing_vars
        if price is not UNSET:
            field_dict["price"] = price

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_update_price_type_0 import ServiceUpdatePriceType0
        from ..models.service_update_routing_vars_type_0 import ServiceUpdateRoutingVarsType0

        d = dict(src_dict)

        def _parse_status(data: object) -> None | ServiceStatusEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = check_service_status_enum(data)

                return status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceStatusEnum | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        run_tests = d.pop("run_tests", UNSET)

        def _parse_visibility(data: object) -> None | ServiceVisibilityEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                visibility_type_0 = check_service_visibility_enum(data)

                return visibility_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceVisibilityEnum | Unset, data)

        visibility = _parse_visibility(d.pop("visibility", UNSET))

        def _parse_routing_vars(data: object) -> None | ServiceUpdateRoutingVarsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_vars_type_0 = ServiceUpdateRoutingVarsType0.from_dict(data)

                return routing_vars_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceUpdateRoutingVarsType0 | Unset, data)

        routing_vars = _parse_routing_vars(d.pop("routing_vars", UNSET))

        def _parse_price(data: object) -> None | ServiceUpdatePriceType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                price_type_0 = ServiceUpdatePriceType0.from_dict(data)

                return price_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ServiceUpdatePriceType0 | Unset, data)

        price = _parse_price(d.pop("price", UNSET))

        service_update = cls(
            status=status,
            run_tests=run_tests,
            visibility=visibility,
            routing_vars=routing_vars,
            price=price,
        )

        service_update.additional_properties = d
        return service_update

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
