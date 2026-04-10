from typing import Literal, cast

BlogStatusEnum = Literal['archived', 'draft', 'published']

BLOG_STATUS_ENUM_VALUES: set[BlogStatusEnum] = { 'archived', 'draft', 'published',  }

def check_blog_status_enum(value: str) -> BlogStatusEnum:
    if value in BLOG_STATUS_ENUM_VALUES:
        return cast(BlogStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {BLOG_STATUS_ENUM_VALUES!r}")
