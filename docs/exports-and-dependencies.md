# Exports & Dependencies

How a service declares what other services may ask of it (`exports`), and how a
service asks the enrolling customer for access to other services
(`customer_access_requests`). It is the
`export` / `import` pattern of a programming language, applied to services: a
service that depends on others is a *composite* service, and the customer
approves each dependency when they enroll.

The seller CLI uses `unitysvc-core>=0.3.4` to validate explicit access
contracts and resource-only apps. Service capabilities come from published
exports; room resources use the platform registry. Room provisioning during
enrollment is tracked in [unitysvc#2830](https://github.com/unitysvc/unitysvc/issues/2830).

## The model

- **Exports** live in your service's own `offering.json`. They say which
  permissions and which customization options other services may request.
  Most services declare nothing: a service that declares no `permissions`
  exports one, `invoke` (calling it, on every route). A service that declares
  `permissions` exports exactly those, and `invoke` only if it declares it
  too; a data service such as `me` exports `read` / `write` and no `invoke`.
- **Customer access requests** live on a channel in `upstream_access_config`,
  as `customer_access_requests`. Each entry names a service or platform resource and what
  your service needs from it — for example an uptime monitor that writes to the customer's
  `log` and alerts through `notify`.
- **The customer decides.** When a customer enrolls in your service, they see
  each dependency with your justification, approve required items, select optional ones, add options the request does not
  fix, and set limits. What they approve becomes a *policy* on the API key your
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

Without `permissions`, your service exports one permission, `invoke`, covering
every route (`"* /*"`); that is what `service:<name>` and the `service:*`
wildcard grant. Declare named permissions only when callers should be able to
get *less* than full access — for example read-only. A service that declares
`permissions` exports exactly those, and `invoke` only if it declares it too. Each permission lists the routes it covers as
`"<METHOD> /<path>"`, with `*` for any method or as a glob in the path.
Permissions are never inferred from HTTP methods: `POST /chat/completions`
reads nothing and modifies nothing, so method alone says nothing about intent.

### `options`

The customizations your service accepts from callers, as a **JSON Schema**
object — the same format as a channel's
[`params.schema`](file-schemas.md#enrollment-parameters), with an
optional `options_ui_schema` for form hints. The customer's enrollment form is
rendered from it.

A customer sets options when approving a dependency, and a grant records
them in query-string syntax (`"log_level=warn"`), so each option must be a
single value. That syntax is only how a grant stores them, not how they reach
a service (see [How options reach your service](#how-options-reach-your-service)):

- **Names**: lowercase letters, digits and `_`.
- **Types**: `string`, `integer`, `number`, `boolean`, or an `array` of strings
  (written comma-joined: `profile=contact.email,location`, the OpenAPI
  `style: form, explode: false` convention). Nested objects are refused.
- **All options are optional**: no `required`, and only declared properties are
  accepted.
- **Self-contained**: no `$ref`. The schema is validated as written and never
  fetches anything.
- **`default`** is what applies when the customer's policy doesn't set the
  option. It is shown to the customer.

Options are for customizing what *your* service does for a caller —
including limits only your service can apply, such as a message size. They
are not for limiting how often or how much a caller uses you: the platform
does that for every service (see [Limits](#limits)).

## Customer access requests

On any channel of `upstream_access_config`:

```json
{
  "upstream_access_config": {
    "default": {
      "base_url": "https://checks.example.com/run",
      "customer_access_requests": [
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
| `object` | yes | A named service (`service:<name>`), a registered resource (`resource:room`), or `apikey`. No wildcards. |
| `permissions` | yes | Explicit permissions from the target's exports or resource registry. An approved item keeps this exact set. |
| `justification` | yes | Why your service needs it, in words the customer reads before approving. |
| `required` | yes | `true` if your service cannot work without it; `false` lets the customer decline the item. |
| `options` | no | Fixed option values, e.g. `"log_level=warn&max_size=2000"`. The customer cannot override them. |
| `limits` | no | Suggested usage limits, e.g. `{"count_per_day": 1000}` (see [Limits](#limits)). |

A selected item keeps its declared object, full permission set and every
specified option. The policy builder copies the fixed options into the policy;
omission does not unset them, and a conflicting value is refused. Customers may
add options the request does not declare, within the target's schema, and set
valid limits. Required items must be selected; optional items may be omitted.
Only `limits` are suggestions that pre-fill the form.

For `service:ai`, omit the `service` option to let the customer choose their AI
service. Declare `options="service=labs/llm-balanced"` to require that service.
Customers cannot add undeclared policy items, except their own limits-only
`enrollment` entry.

A longer-lived key for your service's work is requested with one `apikey`
entry: `{"object": "apikey", "required": false, "limits": {"api_key_lifespan": 14400}, "justification": "Batch runs take up to four hours"}`.
It takes only `limits` (exactly `api_key_lifespan`, whole seconds from 1 to
86400) and a `justification`, and grants nothing. Without it, a key leased for
the enrollment lives one hour.

Each channel declares its own `customer_access_requests`, so different plans of one service
can depend on different things — for example a channel that uses the
customer's own `ai` (and is priced lower) beside a managed channel that uses
yours.

## Resource-only apps (Commons)

With `unitysvc-core>=0.3.4`, a channel can request a platform room without an
upstream server, access method or user access interface:

```json
{
  "upstream_access_config": {
    "free": {
      "customer_access_requests": [{
        "object": "resource:room",
        "permissions": ["create"],
        "required": true,
        "justification": "Creates your group room during enrollment",
        "options": "kind=chat&max_members=100"
      }]
    }
  }
}
```

The kind and member cap are fixed. Owners edit the room's name and Markdown
description after creation. Other supported kinds are private enrollment
`support` rooms and service-wide `announcement` / `discussion` rooms. Their
admissions are automatic; only `chat` rooms allow invitation-code joining.
Resource requests are validated by the platform registry, without a catalog
service named `rooms`. The provisioning step is tracked in
[unitysvc#2830](https://github.com/unitysvc/unitysvc/issues/2830).

Use `service_type: "communication"` for Commons, or omit `service_type` when no
category applies. Run `usvc seller specs validate` before uploading. The CLI
keeps the resource-only channel and its fixed options in the upload payload.

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

**Not through your upstream URL.** The gateway never changes your channel's
`base_url` or query to carry options, and never sends a customer's policy to
your upstream: the options a customer chose are their private decision.

How an option takes effect depends on how the target service is implemented:

- **Services implemented in the gateway** (`me`, `log`, `ai`, `notify`,
  `email`, `bill`) read the calling key's policy directly and apply its
  options themselves. For example, `me` returns only the profile paths a
  grant's `profile` option lists.
- **A service proxied to an upstream**, such as yours, can only be influenced
  through that upstream's own interface. An option would take effect only
  where your channel's configuration maps it into the upstream request in a
  form your upstream understands (for example a request transformer setting
  a body field). That mapping isn't available yet, so options you declare on
  your own service are shown to customers but not enforced for now.

Enrollment parameters keep working alongside (`{{ params.X }}` in your channel
config, declared in the channel's `params`).

## Validation

`usvc_seller specs validate` checks:

- **`exports`**: permissions and their routes; that `options` is a valid JSON
  Schema object within the restrictions above.
- **`customer_access_requests`**: every field's shape, the `options` query string, and the
  limit keys and values.

Once the catalog check is available, every dependency is also checked against
the target's published exports: each permission must be one the target
exports (`invoke` included, since a service that declares permissions may not
export it), each option must be exported, and each value must satisfy its
schema. Limits never need that lookup. Backend ingest runs the same checks
when you upload.

## See also

- [File Schemas](file-schemas.md) — the `offering_v1` fields and the
  upstream access channel object
- [Enrollment Parameters](file-schemas.md#enrollment-parameters) — enrollment parameters,
  the other way a customer customizes a service
- [Secrets & Variables](secrets-and-variables.md) — customer and seller secrets
