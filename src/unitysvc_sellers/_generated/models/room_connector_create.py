from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomConnectorCreate")


@_attrs_define
class RoomConnectorCreate:
    name: str
    """ Unique within this membership: lowercase letters, digits and hyphens; it names the connector and routes
    email replies """
    notify: None | str | Unset = UNSET
    """ A service, such as notify (your Me notify service), labs/msg-to-discord or e/<code>; null = off """
    email: None | str | Unset = UNSET
    """ A service, such as email (your Me email service), smtp-relay or e/<code>; null = off """
    post: None | str | Unset = UNSET
    """ The service a keyless sender posts through, such as post (your Me post service) or labs/discord-to-msg; null
    = off. The paying customer's inbound key for it is made on first use (unitysvc#2918) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if notify is not UNSET:
            field_dict["notify"] = notify
        if email is not UNSET:
            field_dict["email"] = email
        if post is not UNSET:
            field_dict["post"] = post

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
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

        room_connector_create = cls(
            name=name,
            notify=notify,
            email=email,
            post=post,
        )

        room_connector_create.additional_properties = d
        return room_connector_create

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
