from typing import Literal, cast

ServiceProbeResultOutcome = Literal["healthy", "platform_fault", "upstream_fault"]

SERVICE_PROBE_RESULT_OUTCOME_VALUES: set[ServiceProbeResultOutcome] = {
    "healthy",
    "platform_fault",
    "upstream_fault",
}


def check_service_probe_result_outcome(value: str) -> ServiceProbeResultOutcome:
    if value in SERVICE_PROBE_RESULT_OUTCOME_VALUES:
        return cast(ServiceProbeResultOutcome, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SERVICE_PROBE_RESULT_OUTCOME_VALUES!r}")
