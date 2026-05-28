# Service Names & `base_url` Naming Conventions

This page documents the rules the platform enforces on **service /
listing names** and on the **`user_access_interfaces[].base_url`**
field — the gateway-path portion that comes after
`${API_GATEWAY_BASE_URL}/`. The rules exist so customers can predict
how to reach your services, so the gateway can resolve every published
URL unambiguously, and so future platform features can reserve URL
namespaces (memoization, request logs, async fan-out, etc.) without
breaking existing seller catalogs.

The validator that enforces these rules lives in
[`unitysvc-core`](https://pypi.org/project/unitysvc-core/) and runs on
every `usvc_seller data validate` invocation. CI / upload pipelines
reject non-conformant catalogs before they reach the platform.

## TL;DR

```toml
# user_access_interface base_url — only the path after the placeholder is constrained
base_url = "${API_GATEWAY_BASE_URL}/<provider>[/<service-name>][@<variant>]"

# Examples that pass
base_url = "${API_GATEWAY_BASE_URL}/cohere"
base_url = "${API_GATEWAY_BASE_URL}/cohere/command-r-plus"
base_url = "${API_GATEWAY_BASE_URL}/cohere/command-r-plus@byok"
base_url = "${API_GATEWAY_BASE_URL}/Qwen/Qwen2.5-Coder-7B-Instruct"   # hierarchical
base_url = "${API_GATEWAY_BASE_URL}/cohere/command-r-plus/{{ enrollment_vars.code }}"

# The /a/ movable-pointer convention (#1139)
base_url = "${API_GATEWAY_BASE_URL}/a/cohere-latest"
base_url = "${API_GATEWAY_BASE_URL}/a/anthropic/claude-opus-latest"
```

## The grammar

After `${API_GATEWAY_BASE_URL}/`, the path is structured as:

```
<provider>[/<segment>...][@<variant>]
```

Each `/`-separated piece is a **segment**. Segments are validated
independently:

| Rule | Detail |
|---|---|
| Minimum length | Every segment must be **2 or more characters**. Single-character segments are reserved (see below). |
| Allowed characters | Letters (`A-Z`, `a-z`), digits (`0-9`), `.`, `-`, `_`. |
| First character | Must be alphanumeric. Leading `-`, `_`, `.` are rejected. |
| `@` variant tag | At most **one** `@` separates the name part from an optional seller-defined variant suffix (`@byok`, `@premium-eu`, etc.). The variant has the same per-segment rules as the name but **no minimum-length requirement** — variants don't collide with gateway primitive prefixes because they sit after `@`, not at the start of a path segment. |
| Hierarchical names | Multi-segment names like HuggingFace's `Qwen/Qwen2.5-Coder-7B-Instruct` are accepted; each segment is validated individually. |

### Dynamic substitution is treated specially

Anywhere from the first `{{`, `{%`, or `${` onward is considered
**per-enrollment dynamic content** — the platform substitutes it at
request time, so the validator skips it. The portion **before** the
first dynamic marker is the **static identifier prefix** and is
validated against the grammar above.

```toml
# Static prefix: "cohere/command-r-plus"  (valid)
# Dynamic suffix: "/{{ enrollment_vars.code }}"  (skipped by the validator)
base_url = "${API_GATEWAY_BASE_URL}/cohere/command-r-plus/{{ enrollment_vars.code }}"

# A base_url that is entirely dynamic after the placeholder is also accepted —
# the platform-native interface uses the gateway root.
base_url = "${API_GATEWAY_BASE_URL}/{{ provider_name }}"
```

A static-prefix bug is still caught even when a Jinja block follows.
For example, `${API_GATEWAY_BASE_URL}/u/uptime/{{ code }}` is rejected
because `u` is a single-character segment.

## Reserved single-letter prefixes

Single-character first segments are reserved to keep the gateway's
**wrapper / primitive** namespace free of collisions with seller paths.
The platform uses these prefixes to layer behavior on top of any
service URL without changing the seller's published path:

| Prefix | Reserved for | Purpose |
|---|---|---|
| `a/` | **Aliases** | Customer-defined URL aliases (and seller "movable pointer" naming — see below). |
| `b/` | **Broadcast** | Fan-out a single request to multiple services. |
| `c/` | **Chain** | Sequence two or more services. |
| `d/` | **Delayed dispatch** | Register a one-shot future call. |
| `f/` | **Failover** | Secondary path if the primary fails. |
| `g/` | **Groups** | Address a service group rather than a single listing. |
| `l/` | **Logging** | Force a request to be captured in the customer's call log. |
| `m/` | **Memoize** | Cache the response in the gateway. |
| `p/` | (legacy) | Was the explicit `/p/<provider>` prefix; superseded by bare `<provider>/...` paths. |
| `r/` | **Recurrent** | Register a recurring scheduled call. |
| `t/` | **Tee** | Fire-and-forget mirror of a request to a second service. |

If your `base_url` starts with any of these letters followed by `/`,
the validator rejects it. Pick a different leading segment.

## Exception — the `a/` movable-pointer convention (#1139)

The single-character rule has **one carve-out**: a literal leading
`a/` segment is permitted on seller- and platform-published
`user_access_interface` paths as a customer-facing **movable-pointer
naming convention**.

The convention has a single purpose: signal to customers *"this URL is
a movable pointer — the publisher reserves the right to re-point the
underlying target at a newer listing later."* It carries no special
routing behavior at the listing layer; gateway-side, `a/<rest>`
resolves like any other listing path. The benefit is purely social:
customers reading their dashboard see at a glance which URLs are
stable (`cohere/command-r-plus` — a sticky listing identifier) and
which are intentionally mutable (`a/cohere-latest` — the seller's
"latest" pointer that may point at `command-r-plus-v2` next month).

### What's accepted

```toml
base_url = "${API_GATEWAY_BASE_URL}/a/cohere-latest"
base_url = "${API_GATEWAY_BASE_URL}/a/anthropic/claude-opus-latest"
base_url = "${API_GATEWAY_BASE_URL}/a/cohere-latest@byok"
base_url = "${API_GATEWAY_BASE_URL}/a/cohere-latest/{{ enrollment_vars.code }}"
```

After the leading `a/` is stripped, the remainder is validated under
the normal grammar. So:

- The remainder must be non-empty — bare `a/` is rejected.
- The remainder's segments must still be ≥ 2 characters — `a/x` is rejected.
- Other primitive prefixes are **not** part of the carve-out — `a/m/foo` is rejected because `m/` is still reserved at the second segment slot. Sellers should use plain `<provider>/<service>` form after the `a/` prefix.

### When to use it

Use the `a/` prefix when you intend to re-point the URL over time
without forcing customers to re-configure their integrations:

- **Canonical / latest pointers**: `a/cohere-latest` — points at your
  current flagship listing; you bump it to `command-r-plus-v2` when
  you ship a new generation.
- **Migration aliases**: `a/cohere-legacy` — points at an older
  listing during a sunset window; you remove it after the deprecation
  period.

For URLs that should remain bound to a specific listing forever (the
common case — most of your catalog), use the plain
`<provider>/<service>` form. Listing names are **sticky**: once
published, the platform expects them to remain bound to the same
underlying service.

## Service / listing names

The same per-segment rules apply to the **`name` field** on offerings
and listings (the identifier used in service paths). The `a/`
carve-out does **not** apply here — listing names themselves should
not start with `a/`, since the convention is about how customers
*reach* the listing, not what it is called internally.

```toml
# Listing names — same grammar as base_url segments
name = "command-r-plus"
name = "command-r-plus@byok"
name = "Qwen/Qwen2.5-Coder-7B-Instruct"
name = "Qwen/Qwen2.5-Coder-7B-Instruct@byok"

# Rejected
name = "a"             # single-char
name = "a/foo"         # single-char first segment (no carve-out for names)
name = "a@b@c"         # multiple '@'
name = "/leading"      # leading '/'
name = "trailing/"     # trailing '/'
name = "with space"    # space not allowed
name = "-leading-dash" # must start alphanumeric
```

## Validating locally

Before uploading, run:

```bash
usvc_seller data validate          # schema + naming validation
usvc_seller data format --check    # CI-style formatting check
```

Both run the same validators the platform uses on upload; catching
issues locally avoids a round-trip through `usvc_seller data upload`
just to see the rejection.

## Related

- Backend gateway resolver — [`unitysvc/unitysvc#1147`](https://github.com/unitysvc/unitysvc/pull/1147)
  (the `/a/<name>` fall-through that makes seller-published `a/` paths resolvable end-to-end).
- Validator implementation — [`unitysvc-core`](https://github.com/unitysvc/unitysvc-core)
  (`validate_listing_gateway_base_urls`, `validate_service_identifier`).
- Umbrella discussion — [`unitysvc/unitysvc#1139`](https://github.com/unitysvc/unitysvc/issues/1139).
