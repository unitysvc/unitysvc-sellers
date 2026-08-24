from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.test_detail_response_source_type_0 import (
    TestDetailResponseSourceType0,
    check_test_detail_response_source_type_0,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.test_detail_response_env_type_0 import TestDetailResponseEnvType0


T = TypeVar("T", bound="TestDetailResponse")


@_attrs_define
class TestDetailResponse:
    """GET /seller/documents/{id}/test-details — one result cell's details.

    Serves the bulky per-execution fields (stdout/stderr/masked env/rendered
    script) for one ``meta.test`` cell. During the #1901 transition the
    fields come either from the cell's content-addressed S3 blob
    (``source="blob"``) or from the legacy inline meta fields
    (``source="inline"``). ``expired=True`` means the cell exists but its
    blob has aged out of ``TEST_DETAIL_RETENTION_DAYS`` — re-run the test to
    reproduce the details; ``status``/``executed_at`` still describe the
    recorded outcome.

    """

    expired: bool | Unset = False
    source: None | TestDetailResponseSourceType0 | Unset = UNSET
    status: None | str | Unset = UNSET
    executed_at: None | str | Unset = UNSET
    exit_code: int | None | Unset = UNSET
    error: None | str | Unset = UNSET
    stdout: None | str | Unset = UNSET
    stderr: None | str | Unset = UNSET
    env: None | TestDetailResponseEnvType0 | Unset = UNSET
    rendered_script: None | str | Unset = UNSET
    rendered_mime_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.test_detail_response_env_type_0 import TestDetailResponseEnvType0

        expired = self.expired

        source: None | str | Unset
        if isinstance(self.source, Unset):
            source = UNSET
        elif isinstance(self.source, str):
            source = self.source
        else:
            source = self.source

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        executed_at: None | str | Unset
        if isinstance(self.executed_at, Unset):
            executed_at = UNSET
        else:
            executed_at = self.executed_at

        exit_code: int | None | Unset
        if isinstance(self.exit_code, Unset):
            exit_code = UNSET
        else:
            exit_code = self.exit_code

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        stdout: None | str | Unset
        if isinstance(self.stdout, Unset):
            stdout = UNSET
        else:
            stdout = self.stdout

        stderr: None | str | Unset
        if isinstance(self.stderr, Unset):
            stderr = UNSET
        else:
            stderr = self.stderr

        env: dict[str, Any] | None | Unset
        if isinstance(self.env, Unset):
            env = UNSET
        elif isinstance(self.env, TestDetailResponseEnvType0):
            env = self.env.to_dict()
        else:
            env = self.env

        rendered_script: None | str | Unset
        if isinstance(self.rendered_script, Unset):
            rendered_script = UNSET
        else:
            rendered_script = self.rendered_script

        rendered_mime_type: None | str | Unset
        if isinstance(self.rendered_mime_type, Unset):
            rendered_mime_type = UNSET
        else:
            rendered_mime_type = self.rendered_mime_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if expired is not UNSET:
            field_dict["expired"] = expired
        if source is not UNSET:
            field_dict["source"] = source
        if status is not UNSET:
            field_dict["status"] = status
        if executed_at is not UNSET:
            field_dict["executed_at"] = executed_at
        if exit_code is not UNSET:
            field_dict["exit_code"] = exit_code
        if error is not UNSET:
            field_dict["error"] = error
        if stdout is not UNSET:
            field_dict["stdout"] = stdout
        if stderr is not UNSET:
            field_dict["stderr"] = stderr
        if env is not UNSET:
            field_dict["env"] = env
        if rendered_script is not UNSET:
            field_dict["rendered_script"] = rendered_script
        if rendered_mime_type is not UNSET:
            field_dict["rendered_mime_type"] = rendered_mime_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.test_detail_response_env_type_0 import TestDetailResponseEnvType0

        d = dict(src_dict)
        expired = d.pop("expired", UNSET)

        def _parse_source(data: object) -> None | TestDetailResponseSourceType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                source_type_0 = check_test_detail_response_source_type_0(data)

                return source_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TestDetailResponseSourceType0 | Unset, data)

        source = _parse_source(d.pop("source", UNSET))

        def _parse_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_executed_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        executed_at = _parse_executed_at(d.pop("executed_at", UNSET))

        def _parse_exit_code(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        exit_code = _parse_exit_code(d.pop("exit_code", UNSET))

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_stdout(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        stdout = _parse_stdout(d.pop("stdout", UNSET))

        def _parse_stderr(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        stderr = _parse_stderr(d.pop("stderr", UNSET))

        def _parse_env(data: object) -> None | TestDetailResponseEnvType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                env_type_0 = TestDetailResponseEnvType0.from_dict(data)

                return env_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TestDetailResponseEnvType0 | Unset, data)

        env = _parse_env(d.pop("env", UNSET))

        def _parse_rendered_script(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rendered_script = _parse_rendered_script(d.pop("rendered_script", UNSET))

        def _parse_rendered_mime_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rendered_mime_type = _parse_rendered_mime_type(d.pop("rendered_mime_type", UNSET))

        test_detail_response = cls(
            expired=expired,
            source=source,
            status=status,
            executed_at=executed_at,
            exit_code=exit_code,
            error=error,
            stdout=stdout,
            stderr=stderr,
            env=env,
            rendered_script=rendered_script,
            rendered_mime_type=rendered_mime_type,
        )

        test_detail_response.additional_properties = d
        return test_detail_response

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
