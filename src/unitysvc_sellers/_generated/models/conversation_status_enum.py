from typing import Literal, cast

ConversationStatusEnum = Literal['closed', 'open', 'resolved']

CONVERSATION_STATUS_ENUM_VALUES: set[ConversationStatusEnum] = { 'closed', 'open', 'resolved',  }

def check_conversation_status_enum(value: str) -> ConversationStatusEnum:
    if value in CONVERSATION_STATUS_ENUM_VALUES:
        return cast(ConversationStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CONVERSATION_STATUS_ENUM_VALUES!r}")
