from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.gateway_log_level import check_gateway_log_level
from ..models.gateway_log_level import GatewayLogLevel
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.gateway_log_entry_context_type_0 import GatewayLogEntryContextType0





T = TypeVar("T", bound="GatewayLogEntry")



@_attrs_define
class GatewayLogEntry:
    """ Log entry from APISIX gateway.

     """

    level: GatewayLogLevel
    """ Log levels from APISIX gateway. """
    message: str
    source: str | Unset = 'apisix'
    plugin: None | str | Unset = UNSET
    context: GatewayLogEntryContextType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.gateway_log_entry_context_type_0 import GatewayLogEntryContextType0
        level: str = self.level

        message = self.message

        source = self.source

        plugin: None | str | Unset
        if isinstance(self.plugin, Unset):
            plugin = UNSET
        else:
            plugin = self.plugin

        context: dict[str, Any] | None | Unset
        if isinstance(self.context, Unset):
            context = UNSET
        elif isinstance(self.context, GatewayLogEntryContextType0):
            context = self.context.to_dict()
        else:
            context = self.context


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "level": level,
            "message": message,
        })
        if source is not UNSET:
            field_dict["source"] = source
        if plugin is not UNSET:
            field_dict["plugin"] = plugin
        if context is not UNSET:
            field_dict["context"] = context

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.gateway_log_entry_context_type_0 import GatewayLogEntryContextType0
        d = dict(src_dict)
        level = check_gateway_log_level(d.pop("level"))




        message = d.pop("message")

        source = d.pop("source", UNSET)

        def _parse_plugin(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        plugin = _parse_plugin(d.pop("plugin", UNSET))


        def _parse_context(data: object) -> GatewayLogEntryContextType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                context_type_0 = GatewayLogEntryContextType0.from_dict(data)



                return context_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GatewayLogEntryContextType0 | None | Unset, data)

        context = _parse_context(d.pop("context", UNSET))


        gateway_log_entry = cls(
            level=level,
            message=message,
            source=source,
            plugin=plugin,
            context=context,
        )


        gateway_log_entry.additional_properties = d
        return gateway_log_entry

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
