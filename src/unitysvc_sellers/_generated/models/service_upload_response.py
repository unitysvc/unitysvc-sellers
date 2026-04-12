from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.service_upload_response_dryrun_result_type_0 import ServiceUploadResponseDryrunResultType0





T = TypeVar("T", bound="ServiceUploadResponse")



@_attrs_define
class ServiceUploadResponse:
    """ POST /seller/services — unified response for dryrun and real uploads.

    When ``dryrun=True`` the upload runs synchronously inside the request:
    ``dryrun_result`` carries the validation report (provider / offering /
    listing / service sub-results) and ``task_id`` is None.

    When ``dryrun=False`` the upload is queued via Celery and ``task_id``
    is the task id (== Idempotency-Key when one was supplied);
    ``dryrun_result`` is None.

     """

    status: str
    message: str
    task_id: Union[None, Unset, str] = UNSET
    dryrun_result: Union['ServiceUploadResponseDryrunResultType0', None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.service_upload_response_dryrun_result_type_0 import ServiceUploadResponseDryrunResultType0
        status = self.status

        message = self.message

        task_id: Union[None, Unset, str]
        if isinstance(self.task_id, Unset):
            task_id = UNSET
        else:
            task_id = self.task_id

        dryrun_result: Union[None, Unset, dict[str, Any]]
        if isinstance(self.dryrun_result, Unset):
            dryrun_result = UNSET
        elif isinstance(self.dryrun_result, ServiceUploadResponseDryrunResultType0):
            dryrun_result = self.dryrun_result.to_dict()
        else:
            dryrun_result = self.dryrun_result


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "status": status,
            "message": message,
        })
        if task_id is not UNSET:
            field_dict["task_id"] = task_id
        if dryrun_result is not UNSET:
            field_dict["dryrun_result"] = dryrun_result

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_upload_response_dryrun_result_type_0 import ServiceUploadResponseDryrunResultType0
        d = dict(src_dict)
        status = d.pop("status")

        message = d.pop("message")

        def _parse_task_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        task_id = _parse_task_id(d.pop("task_id", UNSET))


        def _parse_dryrun_result(data: object) -> Union['ServiceUploadResponseDryrunResultType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                dryrun_result_type_0 = ServiceUploadResponseDryrunResultType0.from_dict(data)



                return dryrun_result_type_0
            except: # noqa: E722
                pass
            return cast(Union['ServiceUploadResponseDryrunResultType0', None, Unset], data)

        dryrun_result = _parse_dryrun_result(d.pop("dryrun_result", UNSET))


        service_upload_response = cls(
            status=status,
            message=message,
            task_id=task_id,
            dryrun_result=dryrun_result,
        )


        service_upload_response.additional_properties = d
        return service_upload_response

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
