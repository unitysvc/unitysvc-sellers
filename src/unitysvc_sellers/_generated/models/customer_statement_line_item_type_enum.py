from typing import Literal, cast

CustomerStatementLineItemTypeEnum = Literal['adjustment', 'fee', 'refund', 'subscription', 'topoff', 'usage']

CUSTOMER_STATEMENT_LINE_ITEM_TYPE_ENUM_VALUES: set[CustomerStatementLineItemTypeEnum] = { 'adjustment', 'fee', 'refund', 'subscription', 'topoff', 'usage',  }

def check_customer_statement_line_item_type_enum(value: str) -> CustomerStatementLineItemTypeEnum:
    if value in CUSTOMER_STATEMENT_LINE_ITEM_TYPE_ENUM_VALUES:
        return cast(CustomerStatementLineItemTypeEnum, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CUSTOMER_STATEMENT_LINE_ITEM_TYPE_ENUM_VALUES!r}")
