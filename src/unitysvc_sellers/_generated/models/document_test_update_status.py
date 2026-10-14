from typing import Literal, cast

DocumentTestUpdateStatus = Literal["pending", "skip"]

DOCUMENT_TEST_UPDATE_STATUS_VALUES: set[DocumentTestUpdateStatus] = {
    "pending",
    "skip",
}


def check_document_test_update_status(value: str) -> DocumentTestUpdateStatus:
    if value in DOCUMENT_TEST_UPDATE_STATUS_VALUES:
        return cast(DocumentTestUpdateStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DOCUMENT_TEST_UPDATE_STATUS_VALUES!r}")
