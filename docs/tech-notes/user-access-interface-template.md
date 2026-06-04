# User Access Interface Templates

> **Issue**: [unitysvc-bridge-ntfy#1 — Restrict users to enrollment-specific topics](https://github.com/unitysvc/unitysvc-bridge-ntfy/issues/1)
> **Related PR**: [unitysvc#437 — ntfy service integration](https://github.com/unitysvc/unitysvc/pull/437)
> **Date**: 2026-02-10
> **Status**: Implemented

## Overview

String values in `user_access_interfaces` (and `upstream_access_config`) support **Jinja2 template syntax** for dynamic rendering at enrollment time. This enables per-enrollment access interfaces — for example, generating unique endpoint URLs or routing keys for each subscriber.

Interfaces containing template syntax (`{{` or `{%`) are rendered per-enrollment and create enrollment-scoped `AccessInterface` records. Static interfaces (no template syntax) are shared across all enrollments at the listing level.

## Template Context

Templates are rendered with these variables:

| Variable                     | Type   | Description                                          |
| ---------------------------- | ------ | --------------------------------------------------- |
| `enrollment.code`            | string | The enrollment's unique **4-character** reference code |
| `enrollment.id`              | string | Enrollment UUID                                     |
| `enrollment.customer_id`     | string | Customer UUID                                       |
| `enrollment.parameters`      | dict   | All enrollment parameters                           |

## `enrollment.code` and the `/e/<code>` primitive

**Every enrollment is assigned a unique, stable 4-character code** (Crockford base32, e.g. `CEFF`) at creation. Reference it in any template with `{{ enrollment.code }}` — both `user_access_interfaces` and `upstream_access_config` see the same value for a given enrollment.

The code is also a built-in routing handle: **every enrollment is reachable at `/e/<code>`** (e.g. `${API_GATEWAY_BASE_URL}/e/CEFF`), which the gateway resolves to that enrollment's endpoint — regardless of the `base_url` you define. You don't build `/e/...` yourself, and `/e/` is **reserved** (you cannot use it in `base_url`); it is always available for free, as a short, unique handle to the enrollment.

```jinja2
{{ enrollment.code }}      {# 4-character code, e.g. CEFF #}
```

> **Migration:** `enrollment.code` replaces the old `enrollment_code()` template function. Use `{{ enrollment.code }}` instead of `{{ enrollment_code(6) }}`. The code is now a fixed 4 characters — the length argument is gone.

## Example: ntfy Service

The ntfy service exposes a notification gateway where each enrollment gets a unique topic code.

### Configuration

```toml
# listing.toml — user-facing endpoint with per-enrollment topic
[user_access_interfaces.ntfy-gateway]
access_method = "http"
base_url = "${API_GATEWAY_BASE_URL}/ntfy/{{ enrollment.code }}"
description = "Your ntfy notification endpoint"
```

```toml
# offering.toml — upstream endpoint with same enrollment code
[upstream_access_config.ntfy-upstream]
access_method = "http"
base_url = "https://ntfy.svcpass.com/{{ enrollment.code }}"
description = "Private ntfy instance"
```

Both templates reference `{{ enrollment.code }}` and resolve to the same code (e.g. `CEFF`) for a given enrollment.

### After Enrollment

- The enrollment's code (e.g. `CEFF`) is generated at enrollment creation
- An enrollment-scoped `AccessInterface` is created with `base_url = "${API_GATEWAY_BASE_URL}/ntfy/CEFF"`
- The user sees their complete, personalized endpoint
- At gateway routing time, the upstream template resolves to `https://ntfy.svcpass.com/CEFF`
- Gateway forwards the request to the correct upstream topic

### Access Control

Enrollment-scoped `AccessInterface` records are only visible to the enrollment that generated them:

| `AccessInterface` scope | Who can access | Linked via |
|-------------------------|----------------|------------|
| Listing-level (no template) | All enrolled customers | ServiceEnrollment |
| Group-scoped (`group_id` set) | Customers with GroupEnrollment | GroupEnrollment |
| Enrollment-scoped (from template) | Only that specific enrollment | enrollment_id match |

## How It Works

### User access interfaces (enrollment time)

1. During enrollment creation or activation, the backend checks `listing.user_access_interfaces`
2. Each interface is classified:
   - **Template** (contains `{{` or `{%`): rendered per-enrollment, creates enrollment-scoped `AccessInterface`
   - **Static** (no template syntax): shared listing-scoped `AccessInterface` (idempotent)
3. Template rendering substitutes `{{ enrollment.code }}` (and the other `enrollment.*` context values) with the enrollment's data
4. Rendered values are validated as `AccessInterfaceData` and persisted via upsert

### Upstream access interfaces (gateway routing time)

1. When a request arrives, the gateway identifies the enrollment from the user access interface match
2. If the offering's `upstream_access_config` contain template syntax, they are rendered using the enrollment context
3. `{{ enrollment.code }}` resolves to the enrollment's 4-character code (assigned at enrollment creation)
4. The resolved upstream URL is used to forward the request — no upstream `AccessInterface` records are created per enrollment

## Consistency with Service Groups

This mechanism mirrors the existing service group template pattern:

| Aspect | Service Groups | Enrollment Templates |
|--------|---------------|---------------------|
| Template language | Jinja2 | Jinja2 |
| Trigger | Service joins group | User enrolls in service |
| Context | Service metadata | Enrollment + parameters |
| Output | `AccessInterfaceData` | `AccessInterfaceData` |
| Scope link | `AccessInterface.group_id` | `AccessInterface.entity_id` (enrollment) |
