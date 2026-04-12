from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.service_status_enum import check_service_status_enum
from ..models.service_status_enum import ServiceStatusEnum
from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="ServiceStatusUpdate")



@_attrs_define
class ServiceStatusUpdate:
    """ Request model for updating service status.

     """

    status: ServiceStatusEnum
    """ Status of a Service (identity layer).

    Workflow:
    - draft: Not yet submitted for review (default, seller still editing)
    - pending: Tests running (transient, after seller publishes)
    - review: Tests passed, awaiting admin approval
    - active: Approved and operational, accepting requests
    - rejected: Admin rejected (seller can revise and republish)
    - suspended: Admin suspended due to issues/violations
    - deprecated: Service ending """
    run_tests: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        status: str = self.status

        run_tests = self.run_tests


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "status": status,
        })
        if run_tests is not UNSET:
            field_dict["run_tests"] = run_tests

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = check_service_status_enum(d.pop("status"))




        run_tests = d.pop("run_tests", UNSET)

        service_status_update = cls(
            status=status,
            run_tests=run_tests,
        )


        service_status_update.additional_properties = d
        return service_status_update

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
