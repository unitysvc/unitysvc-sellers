from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.skipped_test_document import SkippedTestDocument
    from ..models.test_run import TestRun
    from ..models.test_run_gap import TestRunGap


T = TypeVar("T", bound="ServiceTestResultsResponse")


@_attrs_define
class ServiceTestResultsResponse:
    """GET /seller/services/{id}/test-results — a service's test results.

    A service is tested on its own documents through its own interfaces; a
    platform member on its PLATFORM SERVICE's documents, through the platform
    service's ``/p`` address pinned to it (#2622) — then
    ``platform_service_id`` / ``platform_service_name`` are set. ``passed`` /
    ``error`` are the admission verdict; ``runs`` are the runs that decide it
    (plus a service's upstream probes); ``not_run`` are required runs that
    are missing or stale — the same computation the verdict uses. Output for
    a run: ``…/test-results/{run_id}/output``.

    """

    service_id: UUID
    passed: bool
    runs: list[TestRun]
    not_run: list[TestRunGap]
    platform_service_id: None | Unset | UUID = UNSET
    platform_service_name: None | str | Unset = UNSET
    error: None | str | Unset = UNSET
    skipped: list[SkippedTestDocument] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        service_id = str(self.service_id)

        passed = self.passed

        runs = []
        for runs_item_data in self.runs:
            runs_item = runs_item_data.to_dict()
            runs.append(runs_item)

        not_run = []
        for not_run_item_data in self.not_run:
            not_run_item = not_run_item_data.to_dict()
            not_run.append(not_run_item)

        platform_service_id: None | str | Unset
        if isinstance(self.platform_service_id, Unset):
            platform_service_id = UNSET
        elif isinstance(self.platform_service_id, UUID):
            platform_service_id = str(self.platform_service_id)
        else:
            platform_service_id = self.platform_service_id

        platform_service_name: None | str | Unset
        if isinstance(self.platform_service_name, Unset):
            platform_service_name = UNSET
        else:
            platform_service_name = self.platform_service_name

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        skipped: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.skipped, Unset):
            skipped = []
            for skipped_item_data in self.skipped:
                skipped_item = skipped_item_data.to_dict()
                skipped.append(skipped_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service_id": service_id,
                "passed": passed,
                "runs": runs,
                "not_run": not_run,
            }
        )
        if platform_service_id is not UNSET:
            field_dict["platform_service_id"] = platform_service_id
        if platform_service_name is not UNSET:
            field_dict["platform_service_name"] = platform_service_name
        if error is not UNSET:
            field_dict["error"] = error
        if skipped is not UNSET:
            field_dict["skipped"] = skipped

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.skipped_test_document import SkippedTestDocument
        from ..models.test_run import TestRun
        from ..models.test_run_gap import TestRunGap

        d = dict(src_dict)
        service_id = UUID(d.pop("service_id"))

        passed = d.pop("passed")

        runs = []
        _runs = d.pop("runs")
        for runs_item_data in _runs:
            runs_item = TestRun.from_dict(runs_item_data)

            runs.append(runs_item)

        not_run = []
        _not_run = d.pop("not_run")
        for not_run_item_data in _not_run:
            not_run_item = TestRunGap.from_dict(not_run_item_data)

            not_run.append(not_run_item)

        def _parse_platform_service_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                platform_service_id_type_0 = UUID(data)

                return platform_service_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        platform_service_id = _parse_platform_service_id(d.pop("platform_service_id", UNSET))

        def _parse_platform_service_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        platform_service_name = _parse_platform_service_name(d.pop("platform_service_name", UNSET))

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        _skipped = d.pop("skipped", UNSET)
        skipped: list[SkippedTestDocument] | Unset = UNSET
        if _skipped is not UNSET:
            skipped = []
            for skipped_item_data in _skipped:
                skipped_item = SkippedTestDocument.from_dict(skipped_item_data)

                skipped.append(skipped_item)

        service_test_results_response = cls(
            service_id=service_id,
            passed=passed,
            runs=runs,
            not_run=not_run,
            platform_service_id=platform_service_id,
            platform_service_name=platform_service_name,
            error=error,
            skipped=skipped,
        )

        service_test_results_response.additional_properties = d
        return service_test_results_response

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
