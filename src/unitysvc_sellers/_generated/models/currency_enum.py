from typing import Literal, cast

CurrencyEnum = Literal[
    "AUD", "BTC", "CAD", "CHF", "CNY", "CREDITS", "ETH", "EUR", "GBP", "INR", "JPY", "KRW", "TAO", "USD", "USDC", "USDT"
]

CURRENCY_ENUM_VALUES: set[CurrencyEnum] = {
    "AUD",
    "BTC",
    "CAD",
    "CHF",
    "CNY",
    "CREDITS",
    "ETH",
    "EUR",
    "GBP",
    "INR",
    "JPY",
    "KRW",
    "TAO",
    "USD",
    "USDC",
    "USDT",
}


def check_currency_enum(value: str) -> CurrencyEnum:
    if value in CURRENCY_ENUM_VALUES:
        return cast(CurrencyEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CURRENCY_ENUM_VALUES!r}")
