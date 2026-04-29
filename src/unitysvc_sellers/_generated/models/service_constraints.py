from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.auth_method_enum import AuthMethodEnum, check_auth_method_enum
from ..models.content_filter_enum import ContentFilterEnum, check_content_filter_enum
from ..models.overage_policy_enum import OveragePolicyEnum, check_overage_policy_enum
from ..models.quota_reset_cycle_enum import QuotaResetCycleEnum, check_quota_reset_cycle_enum
from ..models.rate_limit_unit_enum import RateLimitUnitEnum, check_rate_limit_unit_enum
from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceConstraints")


@_attrs_define
class ServiceConstraints:
    monthly_quota: int | None | Unset = UNSET
    """ Monthly usage quota (requests, tokens, etc.) """
    daily_quota: int | None | Unset = UNSET
    """ Daily usage quota (requests, tokens, etc.) """
    quota_unit: None | RateLimitUnitEnum | Unset = UNSET
    """ Unit for quota limits """
    quota_reset_cycle: None | QuotaResetCycleEnum | Unset = UNSET
    """ How often quotas reset """
    overage_policy: None | OveragePolicyEnum | Unset = UNSET
    """ What happens when quota is exceeded """
    auth_methods: list[AuthMethodEnum] | None | Unset = UNSET
    """ Supported authentication methods """
    ip_whitelist_required: bool | None | Unset = UNSET
    """ Whether IP whitelisting is required """
    tls_version_min: None | str | Unset = UNSET
    """ Minimum TLS version required """
    max_request_size_bytes: int | None | Unset = UNSET
    """ Maximum request payload size in bytes """
    max_response_size_bytes: int | None | Unset = UNSET
    """ Maximum response payload size in bytes """
    timeout_seconds: int | None | Unset = UNSET
    """ Request timeout in seconds """
    max_batch_size: int | None | Unset = UNSET
    """ Maximum number of items in batch requests """
    content_filters: list[ContentFilterEnum] | None | Unset = UNSET
    """ Active content filtering policies """
    input_languages: list[str] | None | Unset = UNSET
    """ Supported input languages (ISO 639-1 codes) """
    output_languages: list[str] | None | Unset = UNSET
    """ Supported output languages (ISO 639-1 codes) """
    max_context_length: int | None | Unset = UNSET
    """ Maximum context length in tokens """
    region_restrictions: list[str] | None | Unset = UNSET
    """ Geographic restrictions (ISO country codes) """
    uptime_sla_percent: float | None | Unset = UNSET
    """ Uptime SLA percentage (e.g., 99.9) """
    response_time_sla_ms: int | None | Unset = UNSET
    """ Response time SLA in milliseconds """
    maintenance_windows: list[str] | None | Unset = UNSET
    """ Scheduled maintenance windows """
    max_concurrent_requests: int | None | Unset = UNSET
    """ Maximum concurrent requests allowed """
    connection_timeout_seconds: int | None | Unset = UNSET
    """ Connection timeout in seconds """
    max_connections_per_ip: int | None | Unset = UNSET
    """ Maximum connections per IP address """

    def to_dict(self) -> dict[str, Any]:
        monthly_quota: int | None | Unset
        if isinstance(self.monthly_quota, Unset):
            monthly_quota = UNSET
        else:
            monthly_quota = self.monthly_quota

        daily_quota: int | None | Unset
        if isinstance(self.daily_quota, Unset):
            daily_quota = UNSET
        else:
            daily_quota = self.daily_quota

        quota_unit: None | str | Unset
        if isinstance(self.quota_unit, Unset):
            quota_unit = UNSET
        elif isinstance(self.quota_unit, str):
            quota_unit = self.quota_unit
        else:
            quota_unit = self.quota_unit

        quota_reset_cycle: None | str | Unset
        if isinstance(self.quota_reset_cycle, Unset):
            quota_reset_cycle = UNSET
        elif isinstance(self.quota_reset_cycle, str):
            quota_reset_cycle = self.quota_reset_cycle
        else:
            quota_reset_cycle = self.quota_reset_cycle

        overage_policy: None | str | Unset
        if isinstance(self.overage_policy, Unset):
            overage_policy = UNSET
        elif isinstance(self.overage_policy, str):
            overage_policy = self.overage_policy
        else:
            overage_policy = self.overage_policy

        auth_methods: list[str] | None | Unset
        if isinstance(self.auth_methods, Unset):
            auth_methods = UNSET
        elif isinstance(self.auth_methods, list):
            auth_methods = []
            for auth_methods_type_0_item_data in self.auth_methods:
                auth_methods_type_0_item: str = auth_methods_type_0_item_data
                auth_methods.append(auth_methods_type_0_item)

        else:
            auth_methods = self.auth_methods

        ip_whitelist_required: bool | None | Unset
        if isinstance(self.ip_whitelist_required, Unset):
            ip_whitelist_required = UNSET
        else:
            ip_whitelist_required = self.ip_whitelist_required

        tls_version_min: None | str | Unset
        if isinstance(self.tls_version_min, Unset):
            tls_version_min = UNSET
        else:
            tls_version_min = self.tls_version_min

        max_request_size_bytes: int | None | Unset
        if isinstance(self.max_request_size_bytes, Unset):
            max_request_size_bytes = UNSET
        else:
            max_request_size_bytes = self.max_request_size_bytes

        max_response_size_bytes: int | None | Unset
        if isinstance(self.max_response_size_bytes, Unset):
            max_response_size_bytes = UNSET
        else:
            max_response_size_bytes = self.max_response_size_bytes

        timeout_seconds: int | None | Unset
        if isinstance(self.timeout_seconds, Unset):
            timeout_seconds = UNSET
        else:
            timeout_seconds = self.timeout_seconds

        max_batch_size: int | None | Unset
        if isinstance(self.max_batch_size, Unset):
            max_batch_size = UNSET
        else:
            max_batch_size = self.max_batch_size

        content_filters: list[str] | None | Unset
        if isinstance(self.content_filters, Unset):
            content_filters = UNSET
        elif isinstance(self.content_filters, list):
            content_filters = []
            for content_filters_type_0_item_data in self.content_filters:
                content_filters_type_0_item: str = content_filters_type_0_item_data
                content_filters.append(content_filters_type_0_item)

        else:
            content_filters = self.content_filters

        input_languages: list[str] | None | Unset
        if isinstance(self.input_languages, Unset):
            input_languages = UNSET
        elif isinstance(self.input_languages, list):
            input_languages = self.input_languages

        else:
            input_languages = self.input_languages

        output_languages: list[str] | None | Unset
        if isinstance(self.output_languages, Unset):
            output_languages = UNSET
        elif isinstance(self.output_languages, list):
            output_languages = self.output_languages

        else:
            output_languages = self.output_languages

        max_context_length: int | None | Unset
        if isinstance(self.max_context_length, Unset):
            max_context_length = UNSET
        else:
            max_context_length = self.max_context_length

        region_restrictions: list[str] | None | Unset
        if isinstance(self.region_restrictions, Unset):
            region_restrictions = UNSET
        elif isinstance(self.region_restrictions, list):
            region_restrictions = self.region_restrictions

        else:
            region_restrictions = self.region_restrictions

        uptime_sla_percent: float | None | Unset
        if isinstance(self.uptime_sla_percent, Unset):
            uptime_sla_percent = UNSET
        else:
            uptime_sla_percent = self.uptime_sla_percent

        response_time_sla_ms: int | None | Unset
        if isinstance(self.response_time_sla_ms, Unset):
            response_time_sla_ms = UNSET
        else:
            response_time_sla_ms = self.response_time_sla_ms

        maintenance_windows: list[str] | None | Unset
        if isinstance(self.maintenance_windows, Unset):
            maintenance_windows = UNSET
        elif isinstance(self.maintenance_windows, list):
            maintenance_windows = self.maintenance_windows

        else:
            maintenance_windows = self.maintenance_windows

        max_concurrent_requests: int | None | Unset
        if isinstance(self.max_concurrent_requests, Unset):
            max_concurrent_requests = UNSET
        else:
            max_concurrent_requests = self.max_concurrent_requests

        connection_timeout_seconds: int | None | Unset
        if isinstance(self.connection_timeout_seconds, Unset):
            connection_timeout_seconds = UNSET
        else:
            connection_timeout_seconds = self.connection_timeout_seconds

        max_connections_per_ip: int | None | Unset
        if isinstance(self.max_connections_per_ip, Unset):
            max_connections_per_ip = UNSET
        else:
            max_connections_per_ip = self.max_connections_per_ip

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if monthly_quota is not UNSET:
            field_dict["monthly_quota"] = monthly_quota
        if daily_quota is not UNSET:
            field_dict["daily_quota"] = daily_quota
        if quota_unit is not UNSET:
            field_dict["quota_unit"] = quota_unit
        if quota_reset_cycle is not UNSET:
            field_dict["quota_reset_cycle"] = quota_reset_cycle
        if overage_policy is not UNSET:
            field_dict["overage_policy"] = overage_policy
        if auth_methods is not UNSET:
            field_dict["auth_methods"] = auth_methods
        if ip_whitelist_required is not UNSET:
            field_dict["ip_whitelist_required"] = ip_whitelist_required
        if tls_version_min is not UNSET:
            field_dict["tls_version_min"] = tls_version_min
        if max_request_size_bytes is not UNSET:
            field_dict["max_request_size_bytes"] = max_request_size_bytes
        if max_response_size_bytes is not UNSET:
            field_dict["max_response_size_bytes"] = max_response_size_bytes
        if timeout_seconds is not UNSET:
            field_dict["timeout_seconds"] = timeout_seconds
        if max_batch_size is not UNSET:
            field_dict["max_batch_size"] = max_batch_size
        if content_filters is not UNSET:
            field_dict["content_filters"] = content_filters
        if input_languages is not UNSET:
            field_dict["input_languages"] = input_languages
        if output_languages is not UNSET:
            field_dict["output_languages"] = output_languages
        if max_context_length is not UNSET:
            field_dict["max_context_length"] = max_context_length
        if region_restrictions is not UNSET:
            field_dict["region_restrictions"] = region_restrictions
        if uptime_sla_percent is not UNSET:
            field_dict["uptime_sla_percent"] = uptime_sla_percent
        if response_time_sla_ms is not UNSET:
            field_dict["response_time_sla_ms"] = response_time_sla_ms
        if maintenance_windows is not UNSET:
            field_dict["maintenance_windows"] = maintenance_windows
        if max_concurrent_requests is not UNSET:
            field_dict["max_concurrent_requests"] = max_concurrent_requests
        if connection_timeout_seconds is not UNSET:
            field_dict["connection_timeout_seconds"] = connection_timeout_seconds
        if max_connections_per_ip is not UNSET:
            field_dict["max_connections_per_ip"] = max_connections_per_ip

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_monthly_quota(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        monthly_quota = _parse_monthly_quota(d.pop("monthly_quota", UNSET))

        def _parse_daily_quota(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        daily_quota = _parse_daily_quota(d.pop("daily_quota", UNSET))

        def _parse_quota_unit(data: object) -> None | RateLimitUnitEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                quota_unit_type_0 = check_rate_limit_unit_enum(data)

                return quota_unit_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RateLimitUnitEnum | Unset, data)

        quota_unit = _parse_quota_unit(d.pop("quota_unit", UNSET))

        def _parse_quota_reset_cycle(data: object) -> None | QuotaResetCycleEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                quota_reset_cycle_type_0 = check_quota_reset_cycle_enum(data)

                return quota_reset_cycle_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | QuotaResetCycleEnum | Unset, data)

        quota_reset_cycle = _parse_quota_reset_cycle(d.pop("quota_reset_cycle", UNSET))

        def _parse_overage_policy(data: object) -> None | OveragePolicyEnum | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                overage_policy_type_0 = check_overage_policy_enum(data)

                return overage_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OveragePolicyEnum | Unset, data)

        overage_policy = _parse_overage_policy(d.pop("overage_policy", UNSET))

        def _parse_auth_methods(data: object) -> list[AuthMethodEnum] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                auth_methods_type_0 = []
                _auth_methods_type_0 = data
                for auth_methods_type_0_item_data in _auth_methods_type_0:
                    auth_methods_type_0_item = check_auth_method_enum(auth_methods_type_0_item_data)

                    auth_methods_type_0.append(auth_methods_type_0_item)

                return auth_methods_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[AuthMethodEnum] | None | Unset, data)

        auth_methods = _parse_auth_methods(d.pop("auth_methods", UNSET))

        def _parse_ip_whitelist_required(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        ip_whitelist_required = _parse_ip_whitelist_required(d.pop("ip_whitelist_required", UNSET))

        def _parse_tls_version_min(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        tls_version_min = _parse_tls_version_min(d.pop("tls_version_min", UNSET))

        def _parse_max_request_size_bytes(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_request_size_bytes = _parse_max_request_size_bytes(d.pop("max_request_size_bytes", UNSET))

        def _parse_max_response_size_bytes(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_response_size_bytes = _parse_max_response_size_bytes(d.pop("max_response_size_bytes", UNSET))

        def _parse_timeout_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        timeout_seconds = _parse_timeout_seconds(d.pop("timeout_seconds", UNSET))

        def _parse_max_batch_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_batch_size = _parse_max_batch_size(d.pop("max_batch_size", UNSET))

        def _parse_content_filters(data: object) -> list[ContentFilterEnum] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                content_filters_type_0 = []
                _content_filters_type_0 = data
                for content_filters_type_0_item_data in _content_filters_type_0:
                    content_filters_type_0_item = check_content_filter_enum(content_filters_type_0_item_data)

                    content_filters_type_0.append(content_filters_type_0_item)

                return content_filters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ContentFilterEnum] | None | Unset, data)

        content_filters = _parse_content_filters(d.pop("content_filters", UNSET))

        def _parse_input_languages(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                input_languages_type_0 = cast(list[str], data)

                return input_languages_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        input_languages = _parse_input_languages(d.pop("input_languages", UNSET))

        def _parse_output_languages(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                output_languages_type_0 = cast(list[str], data)

                return output_languages_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        output_languages = _parse_output_languages(d.pop("output_languages", UNSET))

        def _parse_max_context_length(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_context_length = _parse_max_context_length(d.pop("max_context_length", UNSET))

        def _parse_region_restrictions(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                region_restrictions_type_0 = cast(list[str], data)

                return region_restrictions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        region_restrictions = _parse_region_restrictions(d.pop("region_restrictions", UNSET))

        def _parse_uptime_sla_percent(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        uptime_sla_percent = _parse_uptime_sla_percent(d.pop("uptime_sla_percent", UNSET))

        def _parse_response_time_sla_ms(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        response_time_sla_ms = _parse_response_time_sla_ms(d.pop("response_time_sla_ms", UNSET))

        def _parse_maintenance_windows(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                maintenance_windows_type_0 = cast(list[str], data)

                return maintenance_windows_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        maintenance_windows = _parse_maintenance_windows(d.pop("maintenance_windows", UNSET))

        def _parse_max_concurrent_requests(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_concurrent_requests = _parse_max_concurrent_requests(d.pop("max_concurrent_requests", UNSET))

        def _parse_connection_timeout_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        connection_timeout_seconds = _parse_connection_timeout_seconds(d.pop("connection_timeout_seconds", UNSET))

        def _parse_max_connections_per_ip(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_connections_per_ip = _parse_max_connections_per_ip(d.pop("max_connections_per_ip", UNSET))

        service_constraints = cls(
            monthly_quota=monthly_quota,
            daily_quota=daily_quota,
            quota_unit=quota_unit,
            quota_reset_cycle=quota_reset_cycle,
            overage_policy=overage_policy,
            auth_methods=auth_methods,
            ip_whitelist_required=ip_whitelist_required,
            tls_version_min=tls_version_min,
            max_request_size_bytes=max_request_size_bytes,
            max_response_size_bytes=max_response_size_bytes,
            timeout_seconds=timeout_seconds,
            max_batch_size=max_batch_size,
            content_filters=content_filters,
            input_languages=input_languages,
            output_languages=output_languages,
            max_context_length=max_context_length,
            region_restrictions=region_restrictions,
            uptime_sla_percent=uptime_sla_percent,
            response_time_sla_ms=response_time_sla_ms,
            maintenance_windows=maintenance_windows,
            max_concurrent_requests=max_concurrent_requests,
            connection_timeout_seconds=connection_timeout_seconds,
            max_connections_per_ip=max_connections_per_ip,
        )

        return service_constraints
