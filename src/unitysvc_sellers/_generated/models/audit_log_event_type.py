from typing import Literal, cast

AuditLogEventType = Literal['admin_adjustment', 'api_key_created', 'api_key_deleted', 'api_key_updated', 'chargeback', 'credit_limit_change', 'customer_created', 'customer_deleted', 'customer_updated', 'manual_risk_override', 'payment_failure', 'payment_success', 'payout_completed', 'payout_failed', 'payout_processing', 'resource_created', 'resource_deleted', 'resource_updated', 'service_suspended', 'spending_limit_exceeded', 'suspicious_activity', 'user_created', 'user_deleted', 'user_updated', 'wallet_created', 'wallet_deduction', 'wallet_settings_updated', 'wallet_status_changed', 'wallet_topoff']

AUDIT_LOG_EVENT_TYPE_VALUES: set[AuditLogEventType] = { 'admin_adjustment', 'api_key_created', 'api_key_deleted', 'api_key_updated', 'chargeback', 'credit_limit_change', 'customer_created', 'customer_deleted', 'customer_updated', 'manual_risk_override', 'payment_failure', 'payment_success', 'payout_completed', 'payout_failed', 'payout_processing', 'resource_created', 'resource_deleted', 'resource_updated', 'service_suspended', 'spending_limit_exceeded', 'suspicious_activity', 'user_created', 'user_deleted', 'user_updated', 'wallet_created', 'wallet_deduction', 'wallet_settings_updated', 'wallet_status_changed', 'wallet_topoff',  }

def check_audit_log_event_type(value: str) -> AuditLogEventType:
    if value in AUDIT_LOG_EVENT_TYPE_VALUES:
        return cast(AuditLogEventType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {AUDIT_LOG_EVENT_TYPE_VALUES!r}")
