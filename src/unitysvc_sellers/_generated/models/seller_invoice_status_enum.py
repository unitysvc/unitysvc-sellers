from typing import Literal, cast

SellerInvoiceStatusEnum = Literal['disputed', 'finalized', 'funds_released', 'pro_forma', 'voided']

SELLER_INVOICE_STATUS_ENUM_VALUES: set[SellerInvoiceStatusEnum] = { 'disputed', 'finalized', 'funds_released', 'pro_forma', 'voided',  }

def check_seller_invoice_status_enum(value: str) -> SellerInvoiceStatusEnum:
    if value in SELLER_INVOICE_STATUS_ENUM_VALUES:
        return cast(SellerInvoiceStatusEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SELLER_INVOICE_STATUS_ENUM_VALUES!r}")
