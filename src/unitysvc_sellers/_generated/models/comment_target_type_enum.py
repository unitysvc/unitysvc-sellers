from typing import Literal, cast

CommentTargetTypeEnum = Literal['blog_post', 'seller', 'service_listing']

COMMENT_TARGET_TYPE_ENUM_VALUES: set[CommentTargetTypeEnum] = { 'blog_post', 'seller', 'service_listing',  }

def check_comment_target_type_enum(value: str) -> CommentTargetTypeEnum:
    if value in COMMENT_TARGET_TYPE_ENUM_VALUES:
        return cast(CommentTargetTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {COMMENT_TARGET_TYPE_ENUM_VALUES!r}")
