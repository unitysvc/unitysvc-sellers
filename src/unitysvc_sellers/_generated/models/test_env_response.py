from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.vars_ import Vars


T = TypeVar("T", bound="TestEnvResponse")


@_attrs_define
class TestEnvResponse:
    """GET /seller/services/{id}/test-env — rendered enrollment_vars.

    Values are Jinja2-rendered strings suitable for injection as
    environment variables into test scripts.

    """

    vars_: Vars
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.vars_ import Vars

        vars_ = self.vars_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "vars": vars_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vars_ import Vars

        d = dict(src_dict)
        vars_ = Vars.from_dict(d.pop("vars"))

        test_env_response = cls(
            vars_=vars_,
        )

        test_env_response.additional_properties = d
        return test_env_response

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
