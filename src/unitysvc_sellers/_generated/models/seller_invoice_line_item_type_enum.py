from typing import Literal, cast

SellerInvoiceLineItemTypeEnum = Literal['adjustment', 'earning', 'payout', 'payout_fee', 'platform_fee', 'refund_clawback', 'seller_incentive']

SELLER_INVOICE_LINE_ITEM_TYPE_ENUM_VALUES: set[SellerInvoiceLineItemTypeEnum] = { 'adjustment', 'earning', 'payout', 'payout_fee', 'platform_fee', 'refund_clawback', 'seller_incentive',  }

def check_seller_invoice_line_item_type_enum(value: str) -> SellerInvoiceLineItemTypeEnum:
    if value in SELLER_INVOICE_LINE_ITEM_TYPE_ENUM_VALUES:
        return cast(SellerInvoiceLineItemTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SELLER_INVOICE_LINE_ITEM_TYPE_ENUM_VALUES!r}")
