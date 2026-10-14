from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CatalogServicePerformance")


@_attrs_define
class CatalogServicePerformance:
    """How the service performed for real customers, and over what window.

    ``Service.runtime_stats["display"]``, written every 6 hours by
    ``refresh_service_runtime_stats`` from ``usage_events`` (ops probes
    excluded). The window is 7 days for a busy service and longer (up to 90)
    for a rarely used one, until it holds enough requests; it is always stated.
    Absent below a minimum sample, so a handful of requests never brands a
    service. A figure that needs more samples than the window holds (a p95, or
    streaming figures for a mostly non-streaming service) is None.

    """

    window_days: int
    request_count: int
    success_rate_pct: float | None | Unset = UNSET
    latency_p50_ms: float | None | Unset = UNSET
    latency_p95_ms: float | None | Unset = UNSET
    ttft_count: int | Unset = 0
    ttft_p50_ms: float | None | Unset = UNSET
    ttft_p95_ms: float | None | Unset = UNSET
    output_tokens_per_second: float | None | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        window_days = self.window_days

        request_count = self.request_count

        success_rate_pct: float | None | Unset
        if isinstance(self.success_rate_pct, Unset):
            success_rate_pct = UNSET
        else:
            success_rate_pct = self.success_rate_pct

        latency_p50_ms: float | None | Unset
        if isinstance(self.latency_p50_ms, Unset):
            latency_p50_ms = UNSET
        else:
            latency_p50_ms = self.latency_p50_ms

        latency_p95_ms: float | None | Unset
        if isinstance(self.latency_p95_ms, Unset):
            latency_p95_ms = UNSET
        else:
            latency_p95_ms = self.latency_p95_ms

        ttft_count = self.ttft_count

        ttft_p50_ms: float | None | Unset
        if isinstance(self.ttft_p50_ms, Unset):
            ttft_p50_ms = UNSET
        else:
            ttft_p50_ms = self.ttft_p50_ms

        ttft_p95_ms: float | None | Unset
        if isinstance(self.ttft_p95_ms, Unset):
            ttft_p95_ms = UNSET
        else:
            ttft_p95_ms = self.ttft_p95_ms

        output_tokens_per_second: float | None | Unset
        if isinstance(self.output_tokens_per_second, Unset):
            output_tokens_per_second = UNSET
        else:
            output_tokens_per_second = self.output_tokens_per_second

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "window_days": window_days,
                "request_count": request_count,
            }
        )
        if success_rate_pct is not UNSET:
            field_dict["success_rate_pct"] = success_rate_pct
        if latency_p50_ms is not UNSET:
            field_dict["latency_p50_ms"] = latency_p50_ms
        if latency_p95_ms is not UNSET:
            field_dict["latency_p95_ms"] = latency_p95_ms
        if ttft_count is not UNSET:
            field_dict["ttft_count"] = ttft_count
        if ttft_p50_ms is not UNSET:
            field_dict["ttft_p50_ms"] = ttft_p50_ms
        if ttft_p95_ms is not UNSET:
            field_dict["ttft_p95_ms"] = ttft_p95_ms
        if output_tokens_per_second is not UNSET:
            field_dict["output_tokens_per_second"] = output_tokens_per_second
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        window_days = d.pop("window_days")

        request_count = d.pop("request_count")

        def _parse_success_rate_pct(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        success_rate_pct = _parse_success_rate_pct(d.pop("success_rate_pct", UNSET))

        def _parse_latency_p50_ms(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        latency_p50_ms = _parse_latency_p50_ms(d.pop("latency_p50_ms", UNSET))

        def _parse_latency_p95_ms(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        latency_p95_ms = _parse_latency_p95_ms(d.pop("latency_p95_ms", UNSET))

        ttft_count = d.pop("ttft_count", UNSET)

        def _parse_ttft_p50_ms(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ttft_p50_ms = _parse_ttft_p50_ms(d.pop("ttft_p50_ms", UNSET))

        def _parse_ttft_p95_ms(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ttft_p95_ms = _parse_ttft_p95_ms(d.pop("ttft_p95_ms", UNSET))

        def _parse_output_tokens_per_second(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        output_tokens_per_second = _parse_output_tokens_per_second(d.pop("output_tokens_per_second", UNSET))

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        catalog_service_performance = cls(
            window_days=window_days,
            request_count=request_count,
            success_rate_pct=success_rate_pct,
            latency_p50_ms=latency_p50_ms,
            latency_p95_ms=latency_p95_ms,
            ttft_count=ttft_count,
            ttft_p50_ms=ttft_p50_ms,
            ttft_p95_ms=ttft_p95_ms,
            output_tokens_per_second=output_tokens_per_second,
            updated_at=updated_at,
        )

        catalog_service_performance.additional_properties = d
        return catalog_service_performance

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
