from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.service_probe_result_outcome import ServiceProbeResultOutcome, check_service_probe_result_outcome
from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceProbeResult")


@_attrs_define
class ServiceProbeResult:
    """The daily connectivity probe's latest verdict on a service.

    From ``Service.runtime_stats["last_health_check"]``
    (``service_health_tasks.probe.stamp_health_check``). Only the verdict: the
    per-check ``gateway`` / ``upstream`` records hold request details and error
    text that are not for the public page.

    ``outcome``: ``healthy`` (passed), ``upstream_fault`` (the provider's
    service failed the check) or ``platform_fault`` (the platform failed it,
    not the provider; #866).

    """

    checked_at: str
    outcome: ServiceProbeResultOutcome
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        checked_at = self.checked_at

        outcome: str = self.outcome

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "checked_at": checked_at,
                "outcome": outcome,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        checked_at = d.pop("checked_at")

        outcome = check_service_probe_result_outcome(d.pop("outcome"))

        service_probe_result = cls(
            checked_at=checked_at,
            outcome=outcome,
        )

        service_probe_result.additional_properties = d
        return service_probe_result

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
