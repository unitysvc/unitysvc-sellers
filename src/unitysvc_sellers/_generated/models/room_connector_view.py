from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomConnectorView")


@_attrs_define
class RoomConnectorView:
    """One named connector (#2896): its ``notify``, ``email`` and ``post``
    services, null for off. A channel's own name (``notify``, ``email``,
    ``post``) is the account's Me service.

    """

    id: UUID
    name: str
    notify: None | str | Unset = UNSET
    email: None | str | Unset = UNSET
    post: None | str | Unset = UNSET
    """ The service a sender's posts through this connector are converted by (unitysvc#2918); null = the msg format
    as posted """
    inbound_url: None | str | Unset = UNSET
    """ Where a sender that sets no headers posts through ``post``: ``<gateway>/webhook/<KEY>/<service>/<connector
    id>``, built from the paying customer's inbound key for that service when the response is made (never stored).
    Only for callers who may edit the delivery, in a browser session. It contains the key: keep it secret. """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        notify: None | str | Unset
        if isinstance(self.notify, Unset):
            notify = UNSET
        else:
            notify = self.notify

        email: None | str | Unset
        if isinstance(self.email, Unset):
            email = UNSET
        else:
            email = self.email

        post: None | str | Unset
        if isinstance(self.post, Unset):
            post = UNSET
        else:
            post = self.post

        inbound_url: None | str | Unset
        if isinstance(self.inbound_url, Unset):
            inbound_url = UNSET
        else:
            inbound_url = self.inbound_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if notify is not UNSET:
            field_dict["notify"] = notify
        if email is not UNSET:
            field_dict["email"] = email
        if post is not UNSET:
            field_dict["post"] = post
        if inbound_url is not UNSET:
            field_dict["inbound_url"] = inbound_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        def _parse_notify(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notify = _parse_notify(d.pop("notify", UNSET))

        def _parse_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        email = _parse_email(d.pop("email", UNSET))

        def _parse_post(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        post = _parse_post(d.pop("post", UNSET))

        def _parse_inbound_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        inbound_url = _parse_inbound_url(d.pop("inbound_url", UNSET))

        room_connector_view = cls(
            id=id,
            name=name,
            notify=notify,
            email=email,
            post=post,
            inbound_url=inbound_url,
        )

        room_connector_view.additional_properties = d
        return room_connector_view

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
