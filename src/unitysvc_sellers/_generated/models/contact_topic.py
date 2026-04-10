from typing import Literal, cast

ContactTopic = Literal['account', 'billing', 'other', 'request-service', 'seller-inquiry', 'service-issue']

CONTACT_TOPIC_VALUES: set[ContactTopic] = { 'account', 'billing', 'other', 'request-service', 'seller-inquiry', 'service-issue',  }

def check_contact_topic(value: str) -> ContactTopic:
    if value in CONTACT_TOPIC_VALUES:
        return cast(ContactTopic, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CONTACT_TOPIC_VALUES!r}")
