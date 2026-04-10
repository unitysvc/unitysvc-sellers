from typing import Literal, cast

WalletTransactionTypeEnum = Literal['adjustment', 'chargeback', 'deduction', 'fee', 'refund', 'subscription', 'topoff']

WALLET_TRANSACTION_TYPE_ENUM_VALUES: set[WalletTransactionTypeEnum] = { 'adjustment', 'chargeback', 'deduction', 'fee', 'refund', 'subscription', 'topoff',  }

def check_wallet_transaction_type_enum(value: str) -> WalletTransactionTypeEnum:
    if value in WALLET_TRANSACTION_TYPE_ENUM_VALUES:
        return cast(WalletTransactionTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {WALLET_TRANSACTION_TYPE_ENUM_VALUES!r}")
