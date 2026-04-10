from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.matched_rule_notify import MatchedRuleNotify





T = TypeVar("T", bound="MatchedRule")



@_attrs_define
class MatchedRule:
    """ A response rule that matched the upstream response.

     """

    id: str
    """ Rule ID (UUID or slug) """
    name: str
    """ Human-readable rule name """
    priority: int | Unset = 0
    """ Rule priority (higher = more important) """
    notify: MatchedRuleNotify | None | Unset = UNSET
    """ Notify action config """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.matched_rule_notify import MatchedRuleNotify
        id = self.id

        name = self.name

        priority = self.priority

        notify: dict[str, Any] | None | Unset
        if isinstance(self.notify, Unset):
            notify = UNSET
        elif isinstance(self.notify, MatchedRuleNotify):
            notify = self.notify.to_dict()
        else:
            notify = self.notify


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
        })
        if priority is not UNSET:
            field_dict["priority"] = priority
        if notify is not UNSET:
            field_dict["notify"] = notify

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.matched_rule_notify import MatchedRuleNotify
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        priority = d.pop("priority", UNSET)

        def _parse_notify(data: object) -> MatchedRuleNotify | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                notify_type_0 = MatchedRuleNotify.from_dict(data)



                return notify_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MatchedRuleNotify | None | Unset, data)

        notify = _parse_notify(d.pop("notify", UNSET))


        matched_rule = cls(
            id=id,
            name=name,
            priority=priority,
            notify=notify,
        )


        matched_rule.additional_properties = d
        return matched_rule

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
