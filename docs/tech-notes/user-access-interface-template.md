# User Access Interface Templates

> **Issues**: [unitysvc-bridge-ntfy#1 — Restrict users to enrollment-specific topics](https://github.com/unitysvc/unitysvc-bridge-ntfy/issues/1), [unitysvc#2726 — parameters on channels, canonical interfaces](https://github.com/unitysvc/unitysvc/issues/2726)
> **Status**: Updated for `unitysvc-core` 0.3.0

## Overview

Templates appear on both of the orthogonal axes, but they mean different things:

- An **upstream access channel** (`upstream_access_config`) is rendered **per request, at gateway routing time**, with the context of the enrollment the request belongs to. This is where per-enrollment values belong: an enrollment's parameters, its code, the listing's routing variables, and secrets.
- A **user access interface** (`user_access_interfaces`) is the service's **canonical address**, the same for every caller. The only template it may use is `{{ service_name }}`, which the platform fills in (with `listing.name`) when it stores the interface.

Before `unitysvc-core` 0.3.0, an interface could read `{{ enrollment.code }}` and the backend created an enrollment-scoped interface record per enrollment. That is no longer accepted: an enrollment is reached at `/e/<CODE>`, which the platform provides for every enrollment.

## Channel template context

| Form | Value |
| --- | --- |
| `{{ params.X }}` | The enrollment's parameter `X`, declared in the channel's `params` |
| `{{ enrollment.code }}` | The enrollment's unique **4-character** code (Crockford base32, e.g. `CEFF`) |
| `{{ enrollment.id }}` | The enrollment's id |
| `{{ routing_vars.X }}` | The listing's `service_options.routing_vars.X` |
| `${ secrets.X }`, `${ customer_secrets.X ?? default }` | Seller and customer secrets, resolved after the Jinja pass |

See [Upstream access channels](../file-schemas.md#upstream-access-config) and [Enrollment Parameters](../file-schemas.md#enrollment-parameters) for the full rules.

## `enrollment.code` and the `/e/<CODE>` address

**Every enrollment is assigned a unique, stable 4-character code** at creation. It is a built-in routing handle: **every enrollment is reachable at `/e/<CODE>`** on the API gateway (e.g. `${API_GATEWAY_BASE_URL}/e/CEFF`), which the gateway resolves to that enrollment and its channel. You don't declare `/e/...` in a listing, and `/e/` is reserved (you cannot use it in `base_url`).

A channel template reads the code as `{{ enrollment.code }}`, for example to give each enrollment its own upstream:

```json
{
    "upstream_access_config": {
        "plus": {
            "base_url": "https://ntfy.svcpass.com/{{ enrollment.code }}",
            "description": "Private ntfy topic per enrollment"
        }
    }
}
```

At routing time a request to `/e/CEFF` resolves the enrollment, renders the channel, and forwards to `https://ntfy.svcpass.com/CEFF`. No per-enrollment record is created.

> **Migration:** `enrollment.code` replaces the old `enrollment_code()` template function. Use `{{ enrollment.code }}` instead of `{{ enrollment_code(6) }}`; the code is always 4 characters.

## What an interface may contain

`validate_listing_interfaces_are_canonical` renders `{{ service_name }}` and then requires:

- a `base_url` that is one of `${API_GATEWAY_BASE_URL}`, `${S3_GATEWAY_BASE_URL}`, `${SMTP_GATEWAY_BASE_URL}` or `${MCP_GATEWAY_BASE_URL}`, optionally followed by `/` and a path; never an external URL, another variable, or a secret reference;
- no template left over (`{{ routing_vars.X }}` would stay literal and never route);
- nothing per-enrollment (`enrollment.*`, `params.*`).

The one exception is `{{ enrollment.code }}` as the **whole** SMTP `routing_key.username`, or the **whole** S3 bucket segment, a reminder of the per-enrollment address on protocols that have no `/e/` path:

```json
{
    "user_access_interfaces": {
        "smtp_enrollment": {
            "access_method": "smtp",
            "base_url": "${SMTP_GATEWAY_BASE_URL}",
            "routing_key": { "username": "{{ enrollment.code }}" }
        },
        "s3_enrollment": {
            "access_method": "http",
            "base_url": "${S3_GATEWAY_BASE_URL}/{{ enrollment.code }}"
        }
    }
}
```

See [Canonical user access interfaces](../file-schemas.md#canonical-user-access-interfaces).

## Templates inside transformers

The gateway renders `{{ params.* }}`, `{{ enrollment.* }}`, `{{ routing_vars.* }}`, `{{ path.* }}` and `{{ service_name }}` across the **whole** selected channel at request time, `request_transformer` included. After rendering, any `{{ … }}` left in the channel makes it unroutable: the gateway treats it as an unsatisfied template rather than forward it.

So a transformer that needs its own per-request template (a `body_transformer` reading `_body`, for example) must not use `{{ … }}` for it. Use the transformer engine's raw-output tags `{* … *}` instead, with `_escape_json(...)` where the value lands inside a JSON string:

```json
{
    "upstream_access_config": {
        "default": {
            "access_method": "http",
            "base_url": "https://api.example.com/{{ enrollment.code }}",
            "api_key": "${ secrets.UPSTREAM_KEY }",
            "request_transformer": {
                "body_transformer": {
                    "request": {
                        "input_format": "json",
                        "template": "{\"title\":{* _escape_json(_body.title or \"\") *}}"
                    }
                }
            }
        }
    }
}
```

Here the gateway renders `{{ enrollment.code }}` in `base_url` and leaves the `{* … *}` tags for the transformer engine.

## The retired `raw` block

Channels used to wrap values carrying their own templates (such as request transformers) in a `raw` block, which the backend skipped during Jinja expansion and then hoisted into the channel. `raw` is retired: a channel refuses it with `'raw' is not supported: move its keys onto the channel (or server) itself`. Write its keys, such as `request_transformer`, directly on the channel or server.
