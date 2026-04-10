from typing import Literal, cast

CustomerMembershipStatus = Literal['active', 'left', 'removed']

CUSTOMER_MEMBERSHIP_STATUS_VALUES: set[CustomerMembershipStatus] = { 'active', 'left', 'removed',  }

def check_customer_membership_status(value: str) -> CustomerMembershipStatus:
    if value in CUSTOMER_MEMBERSHIP_STATUS_VALUES:
        return cast(CustomerMembershipStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CUSTOMER_MEMBERSHIP_STATUS_VALUES!r}")
