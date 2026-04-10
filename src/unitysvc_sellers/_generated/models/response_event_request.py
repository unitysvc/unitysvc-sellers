from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.matched_rule import MatchedRule
  from ..models.request_summary import RequestSummary





T = TypeVar("T", bound="ResponseEventRequest")



@_attrs_define
class ResponseEventRequest:
    """ Request body for the response-event endpoint.

     """

    customer_id: UUID
    user_id: UUID
    service_id: UUID
    service_enrollment_id: UUID
    request_summary: RequestSummary
    """ Summary of the proxied request for template interpolation. """
    matched_rules: list[MatchedRule]
    response_body: None | str | Unset = UNSET
    """ Raw upstream response body (JSON string) for field extraction """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.matched_rule import MatchedRule
        from ..models.request_summary import RequestSummary
        customer_id = str(self.customer_id)

        user_id = str(self.user_id)

        service_id = str(self.service_id)

        service_enrollment_id = str(self.service_enrollment_id)

        request_summary = self.request_summary.to_dict()

        matched_rules = []
        for matched_rules_item_data in self.matched_rules:
            matched_rules_item = matched_rules_item_data.to_dict()
            matched_rules.append(matched_rules_item)



        response_body: None | str | Unset
        if isinstance(self.response_body, Unset):
            response_body = UNSET
        else:
            response_body = self.response_body


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "customer_id": customer_id,
            "user_id": user_id,
            "service_id": service_id,
            "service_enrollment_id": service_enrollment_id,
            "request_summary": request_summary,
            "matched_rules": matched_rules,
        })
        if response_body is not UNSET:
            field_dict["response_body"] = response_body

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.matched_rule import MatchedRule
        from ..models.request_summary import RequestSummary
        d = dict(src_dict)
        customer_id = UUID(d.pop("customer_id"))




        user_id = UUID(d.pop("user_id"))




        service_id = UUID(d.pop("service_id"))




        service_enrollment_id = UUID(d.pop("service_enrollment_id"))




        request_summary = RequestSummary.from_dict(d.pop("request_summary"))




        matched_rules = []
        _matched_rules = d.pop("matched_rules")
        for matched_rules_item_data in (_matched_rules):
            matched_rules_item = MatchedRule.from_dict(matched_rules_item_data)



            matched_rules.append(matched_rules_item)


        def _parse_response_body(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        response_body = _parse_response_body(d.pop("response_body", UNSET))


        response_event_request = cls(
            customer_id=customer_id,
            user_id=user_id,
            service_id=service_id,
            service_enrollment_id=service_enrollment_id,
            request_summary=request_summary,
            matched_rules=matched_rules,
            response_body=response_body,
        )


        response_event_request.additional_properties = d
        return response_event_request

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
