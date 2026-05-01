from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_render_response_test_type_0 import DocumentRenderResponseTestType0


T = TypeVar("T", bound="DocumentRenderResponse")


@_attrs_define
class DocumentRenderResponse:
    """GET /seller/documents/{id}/render — rendered code-example / connectivity-test.

    Returns the document's ``file_content`` after Jinja2 expansion against a
    render context derived from the document's service.  Two modes selected
    by the ``interface`` query param:

    - ``interface=<uuid>`` → gateway / e2e mode (``local_testing=False``).
      Context is built from the named :class:`AccessInterface` (gateway URL,
      routing_key) plus the listing's ``enrollment_vars`` / ``params`` /
      ``routing_vars``.  This is what ``usvc_seller services run-tests``
      consumes per-interface.
    - ``interface`` omitted → upstream mode (``local_testing=True``).
      Context is built from the offering's ``upstream_access_config`` (first
      interface).  Output matches ``usvc_seller data run-tests`` byte-for-byte.

    ``filename`` has the ``.j2`` suffix stripped when the document was a
    template (e.g. ``connectivity-v1.sh.j2`` → ``connectivity-v1.sh``).

    """

    document_id: str
    filename: str
    content: str
    local_testing: bool
    mime_type: None | str | Unset = UNSET
    test: DocumentRenderResponseTestType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.document_render_response_test_type_0 import DocumentRenderResponseTestType0

        document_id = self.document_id

        filename = self.filename

        content = self.content

        local_testing = self.local_testing

        mime_type: None | str | Unset
        if isinstance(self.mime_type, Unset):
            mime_type = UNSET
        else:
            mime_type = self.mime_type

        test: dict[str, Any] | None | Unset
        if isinstance(self.test, Unset):
            test = UNSET
        elif isinstance(self.test, DocumentRenderResponseTestType0):
            test = self.test.to_dict()
        else:
            test = self.test

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document_id": document_id,
                "filename": filename,
                "content": content,
                "local_testing": local_testing,
            }
        )
        if mime_type is not UNSET:
            field_dict["mime_type"] = mime_type
        if test is not UNSET:
            field_dict["test"] = test

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_render_response_test_type_0 import DocumentRenderResponseTestType0

        d = dict(src_dict)
        document_id = d.pop("document_id")

        filename = d.pop("filename")

        content = d.pop("content")

        local_testing = d.pop("local_testing")

        def _parse_mime_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mime_type = _parse_mime_type(d.pop("mime_type", UNSET))

        def _parse_test(data: object) -> DocumentRenderResponseTestType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                test_type_0 = DocumentRenderResponseTestType0.from_dict(data)

                return test_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentRenderResponseTestType0 | None | Unset, data)

        test = _parse_test(d.pop("test", UNSET))

        document_render_response = cls(
            document_id=document_id,
            filename=filename,
            content=content,
            local_testing=local_testing,
            mime_type=mime_type,
            test=test,
        )

        document_render_response.additional_properties = d
        return document_render_response

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
