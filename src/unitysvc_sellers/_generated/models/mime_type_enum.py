from typing import Literal, cast

MimeTypeEnum = Literal['bash', 'html', 'javascript', 'jpeg', 'json', 'markdown', 'pdf', 'png', 'python', 'svg', 'text', 'url']

MIME_TYPE_ENUM_VALUES: set[MimeTypeEnum] = { 'bash', 'html', 'javascript', 'jpeg', 'json', 'markdown', 'pdf', 'png', 'python', 'svg', 'text', 'url',  }

def check_mime_type_enum(value: str) -> MimeTypeEnum:
    if value in MIME_TYPE_ENUM_VALUES:
        return cast(MimeTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MIME_TYPE_ENUM_VALUES!r}")
