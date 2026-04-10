from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.dispute_reason_enum import check_dispute_reason_enum
from ..models.dispute_reason_enum import DisputeReasonEnum
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.escalate_request_evidence_type_0 import EscalateRequestEvidenceType0





T = TypeVar("T", bound="EscalateRequest")



@_attrs_define
class EscalateRequest:
    """ Request body for escalating to dispute.

     """

    reason: DisputeReasonEnum
    """ Reason for filing a dispute. """
    evidence: EscalateRequestEvidenceType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.escalate_request_evidence_type_0 import EscalateRequestEvidenceType0
        reason: str = self.reason

        evidence: dict[str, Any] | None | Unset
        if isinstance(self.evidence, Unset):
            evidence = UNSET
        elif isinstance(self.evidence, EscalateRequestEvidenceType0):
            evidence = self.evidence.to_dict()
        else:
            evidence = self.evidence


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "reason": reason,
        })
        if evidence is not UNSET:
            field_dict["evidence"] = evidence

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.escalate_request_evidence_type_0 import EscalateRequestEvidenceType0
        d = dict(src_dict)
        reason = check_dispute_reason_enum(d.pop("reason"))




        def _parse_evidence(data: object) -> EscalateRequestEvidenceType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                evidence_type_0 = EscalateRequestEvidenceType0.from_dict(data)



                return evidence_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EscalateRequestEvidenceType0 | None | Unset, data)

        evidence = _parse_evidence(d.pop("evidence", UNSET))


        escalate_request = cls(
            reason=reason,
            evidence=evidence,
        )


        escalate_request.additional_properties = d
        return escalate_request

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
