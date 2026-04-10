from typing import Literal, cast

DocumentContextEnum = Literal['blog_post', 'customer_statement', 'provider', 'seller', 'seller_invoice', 'service_definition', 'service_listing', 'service_offering', 'user']

DOCUMENT_CONTEXT_ENUM_VALUES: set[DocumentContextEnum] = { 'blog_post', 'customer_statement', 'provider', 'seller', 'seller_invoice', 'service_definition', 'service_listing', 'service_offering', 'user',  }

def check_document_context_enum(value: str) -> DocumentContextEnum:
    if value in DOCUMENT_CONTEXT_ENUM_VALUES:
        return cast(DocumentContextEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DOCUMENT_CONTEXT_ENUM_VALUES!r}")
