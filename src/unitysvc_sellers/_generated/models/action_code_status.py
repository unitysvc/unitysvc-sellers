from typing import Literal, cast

ActionCodeStatus = Literal['active', 'exhausted', 'expired', 'revoked']

ACTION_CODE_STATUS_VALUES: set[ActionCodeStatus] = { 'active', 'exhausted', 'expired', 'revoked',  }

def check_action_code_status(value: str) -> ActionCodeStatus:
    if value in ACTION_CODE_STATUS_VALUES:
        return cast(ActionCodeStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ACTION_CODE_STATUS_VALUES!r}")
