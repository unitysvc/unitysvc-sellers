# Exports & Dependencies

How a service declares what other services may ask of it (`exports`), and how a
service declares what it needs from other services (`depends_on`). It is the
`export` / `import` pattern of a programming language, applied to services: a
service that depends on others is a *composite* service, and the customer
approves each dependency when they enroll.

> **Status.** The formats below are defined and validated by `unitysvc-core`
> (0.2.36 and later), so `usvc_seller specs validate` checks them today. The
> platform side is rolling out (unitysvc/unitysvc#2720): publishing exports in
> the catalog, the enrollment consent form, and enforcement at the gateway.
> Until then, declaring them is safe but has no effect on routing.

## The model

- **Exports** live in your service's own `offering.json`. They say which
  permissions and which customization options other services may request.
  Most services declare nothing: every service exports `invoke` (calling it,
  on every route) by default.
- **Dependencies** live on a channel in `upstream_access_config`, as
  `depends_on`. Each entry names another service and what your service needs
  from it — for example an uptime monitor that writes to the customer's
  `log` and alerts through `notify`.
- **The customer decides.** When a customer enrolls in your service, they see
  each dependency with your justification, confirm or change its options,
  and set limits. What they approve becomes a *policy* on the API key your
  service uses on their behalf.

There is no central list of services or permissions: a dependency is checked
against the target service's own `exports`, read from the published catalog.

## Exports

Top level of `offering.json`:

```json
{
  "exports": {
    "permissions": {
      "read": ["GET /records/*"],
      "write": ["POST /records", "PUT /records/*"]
    },
    "options": {
      "type": "object",
      "properties": {
        "log_level": {
          "type": "string",
          "enum": ["debug", "info", "warn", "error"],
          "default": "info",
          "title": "Lowest level recorded",
          "description": "Entries below this level are dropped"
        },
        "max_size": {
          "type": "integer",
          "minimum": 1,
          "maximum": 10000,
          "description": "Largest message accepted, in characters"
        }
      }
    },
    "options_ui_schema": {
      "log_level": { "ui:widget": "radio" }
    }
  }
}
```

### `permissions`

`invoke` is always exported and covers every route; don't declare it. Declare
a named permission only when callers should be able to get *less* than full
access — for example read-only. Each permission lists the routes it covers as
`"<METHOD> /<path>"`, with `*` for any method or as a glob in the path.
Permissions are never inferred from HTTP methods: `POST /chat/completions`
reads nothing and modifies nothing, so method alone says nothing about intent.

### `options`

The customizations your service accepts from callers, as a **JSON Schema**
object — the same format as a listing's
[`user_parameters_schema`](file-schemas.md#user_parameters_schema), with an
optional `options_ui_schema` for form hints. The customer's enrollment form is
rendered from it.

Options are delivered to your service as **query arguments on the upstream
URL** (see [How options reach your service](#how-options-reach-your-service)),
so each option must be a single query value:

- **Names**: lowercase letters, digits and `_`.
- **Types**: `string`, `integer`, `number`, `boolean`, or an `array` of strings
  (sent comma-joined: `fields=contact.email,location`, the OpenAPI
  `style: form, explode: false` convention). Nested objects are refused.
- **All options are optional**: no `required`, and only declared properties are
  accepted.
- **Self-contained**: no `$ref`. The schema is validated as written and never
  fetches anything.
- **`default`** is what your service does when the option is not sent. It is
  shown to the customer; the gateway does not send it.

Options are for customizing what *your* service does for a caller —
including limits only your service can apply, such as a message size. They
are not for limiting how often or how much a caller uses you: the platform
does that for every service (see [Limits](#limits)).

## Dependencies

On any channel of `upstream_access_config`:

```json
{
  "upstream_access_config": {
    "default": {
      "base_url": "https://checks.example.com/run",
      "depends_on": [
        {
          "object": "service:log",
          "permissions": ["invoke"],
          "required": true,
          "justification": "Records the result of each check you run",
          "options": "log_level=warn",
          "limits": { "count_per_day": 1000 }
        },
        {
          "object": "service:notify",
          "permissions": ["invoke"],
          "required": false,
          "justification": "Alerts you when a check fails",
          "limits": { "count_per_day": 20 }
        }
      ]
    }
  }
}
```

| Field | Required | Description |
| --- | --- | --- |
| `object` | yes | The service depended on: `service:<name>`. No wildcards. |
| `permissions` | yes | Permissions from the target's exports: `invoke`, or a named one it declares. |
| `justification` | yes | Why your service needs it, in words the customer reads before approving. |
| `required` | no | `true` if your service can't work without it; the customer may decline the others. Default `false`. |
| `options` | no | A query string of the target's options, e.g. `"log_level=warn&max_size=2000"`. |
| `limits` | no | Suggested usage limits, e.g. `{"count_per_day": 1000}` (see [Limits](#limits)). |

`options` and `limits` here are **suggestions that pre-fill the enrollment
form**. The customer confirms or changes the options within what the target
exports, sets the limits, and may add limits of their own. What they approve
becomes the policy on the key your service uses for them.

Each channel declares its own `depends_on`, so different plans of one service
can depend on different things — for example a channel that uses the
customer's own `ai` (and is priced lower) beside a managed channel that uses
yours.

## Limits

Any service can be limited — the platform meters every call — so limits need
nothing from the target's exports. Keys:

| Key | Value |
| --- | --- |
| `count_per_hour`, `count_per_day`, `count_per_month`, `count_total` | positive integer: number of calls |
| `amount_per_hour`, `amount_per_day`, `amount_per_month`, `amount_total` | positive decimal (as a number or string): money spent |

Limits are counted per policy entry — this customer's enrollment's calls to that
service — and the gateway refuses further calls once one is reached.
Enforcement follows the usage stream, so a burst can slightly overshoot.

## How options reach your service

When a call is made with a key whose policy sets options for your service, the gateway appends them to
your upstream URL as query arguments:

```
https://your-service.example.com/endpoint?log_level=warn&max_size=2000
```

What your service can rely on:

- The values come from the customer's policy. The gateway strips any query
  argument the caller sent under one of your exported option names before
  appending the policy's, so a caller cannot override its own policy.
- An option the policy doesn't set is not sent: apply your `default`.
- Enrollment parameters keep working as before (`{{ params.X }}` in your
  channel config).

Read options as ordinary query arguments. For an SMTP channel there is no
query string, so options don't apply there.

## Validation

`usvc_seller specs validate` checks:

- **`exports`**: permissions and their routes; that `options` is a valid JSON
  Schema object within the restrictions above.
- **`depends_on`**: every field's shape, the `options` query string, and the
  limit keys and values.

Once the catalog check is available, a dependency that asks for more than the
default — a permission other than `invoke`, or any option — is also checked
against the target's published exports: the permission must exist, each option
must be exported, and each value must satisfy its schema. An `invoke`-only
dependency, and limits, never need that lookup. Backend ingest runs the same
checks when you upload.

## See also

- [File Schemas](file-schemas.md) — the `offering_v1` fields and the
  upstream access channel object
- [User Parameters](file-schemas.md#user-parameters) — enrollment parameters,
  the other way a customer customizes a service
- [Secrets & Variables](secrets-and-variables.md) — customer and seller secrets
