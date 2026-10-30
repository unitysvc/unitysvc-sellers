from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.test_run_output_response_env_type_0 import TestRunOutputResponseEnvType0


T = TypeVar("T", bound="TestRunOutputResponse")


@_attrs_define
class TestRunOutputResponse:
    """GET /seller/services/{id}/test-results/{run_id}/output.

    The run's stdout, stderr, rendered script and masked env. ``expired``
    means the run is recorded but (some of) its output aged out of
    ``TEST_DETAIL_RETENTION_DAYS`` — re-run the tests to reproduce it.

    """

    status: str
    expired: bool | Unset = False
    executed_at: datetime.datetime | None | Unset = UNSET
    exit_code: int | None | Unset = UNSET
    error: None | str | Unset = UNSET
    stdout: None | str | Unset = UNSET
    stderr: None | str | Unset = UNSET
    env: None | TestRunOutputResponseEnvType0 | Unset = UNSET
    rendered_script: None | str | Unset = UNSET
    rendered_mime_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.test_run_output_response_env_type_0 import TestRunOutputResponseEnvType0

        status = self.status

        expired = self.expired

        executed_at: None | str | Unset
        if isinstance(self.executed_at, Unset):
            executed_at = UNSET
        elif isinstance(self.executed_at, datetime.datetime):
            executed_at = self.executed_at.isoformat()
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
        elif isinstance(self.env, TestRunOutputResponseEnvType0):
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
        field_dict.update(
            {
                "status": status,
            }
        )
        if expired is not UNSET:
            field_dict["expired"] = expired
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
        from ..models.test_run_output_response_env_type_0 import TestRunOutputResponseEnvType0

        d = dict(src_dict)
        status = d.pop("status")

        expired = d.pop("expired", UNSET)

        def _parse_executed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                executed_at_type_0 = isoparse(data)

                return executed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

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

        def _parse_env(data: object) -> None | TestRunOutputResponseEnvType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                env_type_0 = TestRunOutputResponseEnvType0.from_dict(data)

                return env_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TestRunOutputResponseEnvType0 | Unset, data)

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

        test_run_output_response = cls(
            status=status,
            expired=expired,
            executed_at=executed_at,
            exit_code=exit_code,
            error=error,
            stdout=stdout,
            stderr=stderr,
            env=env,
            rendered_script=rendered_script,
            rendered_mime_type=rendered_mime_type,
        )

        test_run_output_response.additional_properties = d
        return test_run_output_response

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
