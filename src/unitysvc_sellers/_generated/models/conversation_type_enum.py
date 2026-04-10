from typing import Literal, cast

ConversationTypeEnum = Literal['dispute', 'inquiry', 'support']

CONVERSATION_TYPE_ENUM_VALUES: set[ConversationTypeEnum] = { 'dispute', 'inquiry', 'support',  }

def check_conversation_type_enum(value: str) -> ConversationTypeEnum:
    if value in CONVERSATION_TYPE_ENUM_VALUES:
        return cast(ConversationTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CONVERSATION_TYPE_ENUM_VALUES!r}")
