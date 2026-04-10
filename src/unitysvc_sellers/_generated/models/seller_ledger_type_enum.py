from typing import Literal, cast

SellerLedgerTypeEnum = Literal['adjustment', 'funds_released', 'payout', 'payout_fee', 'refund_clawback']

SELLER_LEDGER_TYPE_ENUM_VALUES: set[SellerLedgerTypeEnum] = { 'adjustment', 'funds_released', 'payout', 'payout_fee', 'refund_clawback',  }

def check_seller_ledger_type_enum(value: str) -> SellerLedgerTypeEnum:
    if value in SELLER_LEDGER_TYPE_ENUM_VALUES:
        return cast(SellerLedgerTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SELLER_LEDGER_TYPE_ENUM_VALUES!r}")
