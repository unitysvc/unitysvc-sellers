from typing import Literal, cast

GatewayLogLevel = Literal['ALERT', 'CRIT', 'DEBUG', 'EMERG', 'ERROR', 'INFO', 'NOTICE', 'WARN']

GATEWAY_LOG_LEVEL_VALUES: set[GatewayLogLevel] = { 'ALERT', 'CRIT', 'DEBUG', 'EMERG', 'ERROR', 'INFO', 'NOTICE', 'WARN',  }

def check_gateway_log_level(value: str) -> GatewayLogLevel:
    if value in GATEWAY_LOG_LEVEL_VALUES:
        return cast(GatewayLogLevel, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GATEWAY_LOG_LEVEL_VALUES!r}")
