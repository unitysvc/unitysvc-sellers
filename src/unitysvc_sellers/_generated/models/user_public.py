from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from uuid import UUID






T = TypeVar("T", bound="UserPublic")



@_attrs_define
class UserPublic:
    """ For API response

     """

    id: UUID
    email: str
    is_superuser: bool | Unset = False
    full_name: None | str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        email = self.email

        is_superuser = self.is_superuser

        full_name: None | str | Unset
        if isinstance(self.full_name, Unset):
            full_name = UNSET
        else:
            full_name = self.full_name


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "id": id,
            "email": email,
        })
        if is_superuser is not UNSET:
            field_dict["is_superuser"] = is_superuser
        if full_name is not UNSET:
            field_dict["full_name"] = full_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        email = d.pop("email")

        is_superuser = d.pop("is_superuser", UNSET)

        def _parse_full_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        full_name = _parse_full_name(d.pop("full_name", UNSET))


        user_public = cls(
            id=id,
            email=email,
            is_superuser=is_superuser,
            full_name=full_name,
        )

        return user_public

