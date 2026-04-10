from typing import Literal, cast

ActionCodeType = Literal['enrollment', 'pricing_code', 'team']

ACTION_CODE_TYPE_VALUES: set[ActionCodeType] = { 'enrollment', 'pricing_code', 'team',  }

def check_action_code_type(value: str) -> ActionCodeType:
    if value in ACTION_CODE_TYPE_VALUES:
        return cast(ActionCodeType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ACTION_CODE_TYPE_VALUES!r}")
