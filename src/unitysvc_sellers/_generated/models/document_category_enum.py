from typing import Literal, cast

DocumentCategoryEnum = Literal['api_reference', 'attachment', 'avatar', 'best_practice', 'blog_banner', 'blog_content', 'changelog', 'code_example', 'code_example_output', 'connectivity_test', 'getting_started', 'invoice', 'logo', 'other', 'request_template', 'service_level_agreement', 'specification', 'statement', 'terms_of_service', 'troubleshooting', 'tutorial', 'use_case']

DOCUMENT_CATEGORY_ENUM_VALUES: set[DocumentCategoryEnum] = { 'api_reference', 'attachment', 'avatar', 'best_practice', 'blog_banner', 'blog_content', 'changelog', 'code_example', 'code_example_output', 'connectivity_test', 'getting_started', 'invoice', 'logo', 'other', 'request_template', 'service_level_agreement', 'specification', 'statement', 'terms_of_service', 'troubleshooting', 'tutorial', 'use_case',  }

def check_document_category_enum(value: str) -> DocumentCategoryEnum:
    if value in DOCUMENT_CATEGORY_ENUM_VALUES:
        return cast(DocumentCategoryEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DOCUMENT_CATEGORY_ENUM_VALUES!r}")
