from typing import Literal, cast

CommentStatusEnum = Literal['approved', 'deleted', 'flagged', 'hidden', 'pending']

COMMENT_STATUS_ENUM_VALUES: set[CommentStatusEnum] = { 'approved', 'deleted', 'flagged', 'hidden', 'pending',  }

def check_comment_status_enum(value: str) -> CommentStatusEnum:
    if value in COMMENT_STATUS_ENUM_VALUES:
        return cast(CommentStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {COMMENT_STATUS_ENUM_VALUES!r}")
