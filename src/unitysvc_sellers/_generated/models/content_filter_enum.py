from typing import Literal, cast

ContentFilterEnum = Literal['adult', 'hate_speech', 'pii', 'profanity', 'violence']

CONTENT_FILTER_ENUM_VALUES: set[ContentFilterEnum] = { 'adult', 'hate_speech', 'pii', 'profanity', 'violence',  }

def check_content_filter_enum(value: str) -> ContentFilterEnum:
    if value in CONTENT_FILTER_ENUM_VALUES:
        return cast(ContentFilterEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CONTENT_FILTER_ENUM_VALUES!r}")
