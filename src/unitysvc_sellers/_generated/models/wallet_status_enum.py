from typing import Literal, cast

WalletStatusEnum = Literal['active', 'blocked', 'suspended']

WALLET_STATUS_ENUM_VALUES: set[WalletStatusEnum] = { 'active', 'blocked', 'suspended',  }

def check_wallet_status_enum(value: str) -> WalletStatusEnum:
    if value in WALLET_STATUS_ENUM_VALUES:
        return cast(WalletStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {WALLET_STATUS_ENUM_VALUES!r}")
