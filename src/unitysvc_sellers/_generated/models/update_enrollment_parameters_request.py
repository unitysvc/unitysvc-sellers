from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.update_enrollment_parameters_request_parameters import UpdateEnrollmentParametersRequestParameters





T = TypeVar("T", bound="UpdateEnrollmentParametersRequest")



@_attrs_define
class UpdateEnrollmentParametersRequest:
    """ Request body for updating enrollment parameters.

     """

    parameters: UpdateEnrollmentParametersRequestParameters | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.update_enrollment_parameters_request_parameters import UpdateEnrollmentParametersRequestParameters
        parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if parameters is not UNSET:
            field_dict["parameters"] = parameters

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_enrollment_parameters_request_parameters import UpdateEnrollmentParametersRequestParameters
        d = dict(src_dict)
        _parameters = d.pop("parameters", UNSET)
        parameters: UpdateEnrollmentParametersRequestParameters | Unset
        if isinstance(_parameters,  Unset):
            parameters = UNSET
        else:
            parameters = UpdateEnrollmentParametersRequestParameters.from_dict(_parameters)




        update_enrollment_parameters_request = cls(
            parameters=parameters,
        )


        update_enrollment_parameters_request.additional_properties = d
        return update_enrollment_parameters_request

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
