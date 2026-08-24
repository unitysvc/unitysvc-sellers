from typing import Literal, cast

TestDetailResponseSourceType0 = Literal["blob", "inline"]

TEST_DETAIL_RESPONSE_SOURCE_TYPE_0_VALUES: set[TestDetailResponseSourceType0] = {
    "blob",
    "inline",
}


def check_test_detail_response_source_type_0(value: str) -> TestDetailResponseSourceType0:
    if value in TEST_DETAIL_RESPONSE_SOURCE_TYPE_0_VALUES:
        return cast(TestDetailResponseSourceType0, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TEST_DETAIL_RESPONSE_SOURCE_TYPE_0_VALUES!r}")
