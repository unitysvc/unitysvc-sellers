from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, TextIO, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.account_file_upload_ticket_fields import AccountFileUploadTicketFields


T = TypeVar("T", bound="AccountFileUploadTicket")


@_attrs_define
class AccountFileUploadTicket:
    """Presigned-POST ticket for one direct-to-storage upload.

    POST ``fields`` plus the file (as the last form field, named
    ``file``) as multipart form data to ``url``. The size ceiling and
    exact key are enforced by the signed policy, not by the client.

    """

    key: str
    url: str
    fields: AccountFileUploadTicketFields
    expires_in: int
    max_bytes: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.account_file_upload_ticket_fields import AccountFileUploadTicketFields

        key = self.key

        url = self.url

        fields = self.fields.to_dict()

        expires_in = self.expires_in

        max_bytes = self.max_bytes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "url": url,
                "fields": fields,
                "expires_in": expires_in,
                "max_bytes": max_bytes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.account_file_upload_ticket_fields import AccountFileUploadTicketFields

        d = dict(src_dict)
        key = d.pop("key")

        url = d.pop("url")

        fields = AccountFileUploadTicketFields.from_dict(d.pop("fields"))

        expires_in = d.pop("expires_in")

        max_bytes = d.pop("max_bytes")

        account_file_upload_ticket = cls(
            key=key,
            url=url,
            fields=fields,
            expires_in=expires_in,
            max_bytes=max_bytes,
        )

        account_file_upload_ticket.additional_properties = d
        return account_file_upload_ticket

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
