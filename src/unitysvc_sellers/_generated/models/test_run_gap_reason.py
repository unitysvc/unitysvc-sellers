from typing import Literal, cast

TestRunGapReason = Literal["missing", "stale"]

TEST_RUN_GAP_REASON_VALUES: set[TestRunGapReason] = {
    "missing",
    "stale",
}


def check_test_run_gap_reason(value: str) -> TestRunGapReason:
    if value in TEST_RUN_GAP_REASON_VALUES:
        return cast(TestRunGapReason, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TEST_RUN_GAP_REASON_VALUES!r}")
