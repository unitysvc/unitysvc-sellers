from typing import Literal, cast

AggregationPeriod = Literal['daily', 'hourly', 'monthly']

AGGREGATION_PERIOD_VALUES: set[AggregationPeriod] = { 'daily', 'hourly', 'monthly',  }

def check_aggregation_period(value: str) -> AggregationPeriod:
    if value in AGGREGATION_PERIOD_VALUES:
        return cast(AggregationPeriod, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {AGGREGATION_PERIOD_VALUES!r}")
