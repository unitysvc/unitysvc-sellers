from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomConnectorUpdate")


@_attrs_define
class RoomConnectorUpdate:
    """Fields left out keep their value; null turns a channel off."""

    notify: None | str | Unset = UNSET
    email: None | str | Unset = UNSET
    default: bool | Unset = False
    """ Ignored. There is no default connector: a post naming no connector goes out through all of them. Kept so
    released SDKs still validate. """
    post: None | str | Unset = UNSET
    """ The inbound converter service; null turns it off (the customer's key for the service stays, for its other
    connectors) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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

        default = self.default

        post: None | str | Unset
        if isinstance(self.post, Unset):
            post = UNSET
        else:
            post = self.post

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if notify is not UNSET:
            field_dict["notify"] = notify
        if email is not UNSET:
            field_dict["email"] = email
        if default is not UNSET:
            field_dict["default"] = default
        if post is not UNSET:
            field_dict["post"] = post

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

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

        default = d.pop("default", UNSET)

        def _parse_post(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        post = _parse_post(d.pop("post", UNSET))

        room_connector_update = cls(
            notify=notify,
            email=email,
            default=default,
            post=post,
        )

        room_connector_update.additional_properties = d
        return room_connector_update

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
