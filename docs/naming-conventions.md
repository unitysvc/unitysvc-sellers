# Service Names & `base_url` Naming Conventions

This page documents how the platform names services and how the
`user_access_interfaces[].base_url` field must reference that name. The
rules exist so customers can predict how to reach your services, so the
gateway can resolve every published URL unambiguously, and so future
platform features can reserve URL namespaces (memoization, request logs,
async fan-out, etc.) without breaking existing seller catalogs.

The validator that enforces these rules lives in
[`unitysvc-core`](https://pypi.org/project/unitysvc-core/) and runs on
every `usvc_seller data validate` invocation. CI / upload pipelines
reject non-conformant catalogs before they reach the platform.

## `service_name` = `listing.name`

The platform service identifier is **`service_name`, and it is exactly
`listing.name`** — written verbatim by the seller. There is no
composition and no fallback: `listing.name` is the single source of
truth. It is:

- **Required.** Every `listing.{json,toml}` must declare `name`.
- **The routable, customer-facing identifier** — the value the gateway
  routes by, the value `usvc_seller … --name` selects on, and the value
  `{{ service_name }}` renders to in a `base_url`.

### `listing.name` vs `offering.name`

These are two different names with two different jobs — do not confuse
them:

| Field | Role | Faces | Example |
|---|---|---|---|
| **`listing.name`** | **`service_name`** — the platform service identifier | **Customers** | `cohere/command-r-plus` |
| **`offering.name`** | the **upstream name**, kept in sync with the upstream provider's own service id | The upstream provider | `command-r-plus` |

`offering.name` describes the thing you are reselling as the *upstream*
calls it (e.g. the model id at the provider's API). `listing.name` is
what *your customers* see and route to. `offering.name` **never**
becomes `service_name` — only `listing.name` does.

```toml
# offering.{json,toml} — the upstream's name for the service
name = "command-r-plus"

# listing.{json,toml} — the customer-facing service identifier (service_name)
name = "cohere/command-r-plus"
```

### Namespaced vs top-level names

Whether a name is namespaced or top-level is **purely syntactic — does
the name part contain a `/`?**

- **Has `/` ⇒ namespaced** (`cohere/command-r-plus`): self-service. The
  **first segment must equal your provider slug** (`provider_v1.name`),
  so you cannot register `otherprovider/…` under your own provider.
- **No `/` ⇒ top-level** (`ntfy`, `http-relay`): a request that an
  **admin must accept** (reserved-name allowlist). Sellers cannot
  self-register top-level names; `usvc_seller data validate` accepts the
  grammar locally, but the backend gates the name at registration.

```toml
# Namespaced — first segment is the provider slug (self-service)
name = "cohere/command-r-plus"
name = "huggingface/Qwen/Qwen2.5-Coder-7B-Instruct"   # hierarchical
name = "cohere/command-r-plus@byok"                   # with variant tag

# Top-level — admin-gated (e.g. a canonical open protocol or gateway-native service)
name = "ntfy"
```

## `base_url` must route by `{{ service_name }}`

A `user_access_interfaces[].base_url` does **not** hard-code the service
path. It references the service identifier through the
`{{ service_name }}` Jinja variable, which the platform renders to
`listing.name` when the access interface is materialized. This keeps the
routable path bound to the name automatically.

```toml
# The canonical form — service_name leads the path
base_url = "${API_GATEWAY_BASE_URL}/{{ service_name }}"

# With a static or dynamic suffix
base_url = "${API_GATEWAY_BASE_URL}/{{ service_name }}/v1/chat/completions"
base_url = "${API_GATEWAY_BASE_URL}/{{ service_name }}/{{ enrollment_vars.code }}"

# Wrapper-stack primitive prefixes may precede it
base_url = "${API_GATEWAY_BASE_URL}/u/{{ service_name }}"

# The /a/ movable-pointer convention (#1139)
base_url = "${API_GATEWAY_BASE_URL}/a/cohere-latest"
```

**Rejected:**

```toml
# Literal <provider>/<service> path — use {{ service_name }} instead
base_url = "${API_GATEWAY_BASE_URL}/cohere/command-r-plus"

# The removed /p/ route primitive
base_url = "${API_GATEWAY_BASE_URL}/p/cohere"
```

A `base_url` is accepted when, after `${API_GATEWAY_BASE_URL}`, it
**references `{{ service_name }}`**, is an **`/a/<alias>`** movable
pointer, is the **gateway root** (`${API_GATEWAY_BASE_URL}` alone), or is
**entirely dynamic** from its first segment (e.g. a BYOE
`${API_GATEWAY_BASE_URL}/{{ enrollment_vars.endpoint }}`).

## The name grammar

`listing.name` (and the alias after `/a/`) is validated per-segment.
The identifier has the form `<name>[@<variant>]`; each `/`-separated
piece of `<name>` is a **segment**:

| Rule | Detail |
|---|---|
| Minimum length | Every segment must be **2 or more characters**. Single-character segments are reserved (see below). |
| Allowed characters | Letters (`A-Z`, `a-z`), digits (`0-9`), `.`, `-`, `_`. |
| First character | Must be alphanumeric. Leading `-`, `_`, `.` are rejected. |
| `@` variant tag | At most **one** `@` separates the name part from an optional seller-defined variant suffix (`@byok`, `@premium-eu`, etc.). The variant has the same per-segment character rules but no minimum-length requirement. |
| Hierarchical names | Multi-segment names like HuggingFace's `huggingface/Qwen/Qwen2.5-Coder-7B-Instruct` are accepted; each segment is validated individually. |

```toml
# Accepted
name = "cohere/command-r-plus"
name = "cohere/command-r-plus@byok"
name = "huggingface/Qwen/Qwen2.5-Coder-7B-Instruct"

# Rejected
name = "co/x"          # single-char segment
name = "a@b@c"         # multiple '@'
name = "/leading"      # leading '/'
name = "trailing/"     # trailing '/'
name = "with space"    # space not allowed
name = "-leading-dash" # must start alphanumeric
```

## Reserved single-letter prefixes

Single-character first segments are reserved to keep the gateway's
**wrapper / primitive** namespace free of collisions with seller paths.
The platform uses these prefixes to layer behavior on top of any service
URL without changing the seller's published path:

| Prefix | Reserved for | Purpose |
|---|---|---|
| `a/` | **Aliases** | Customer-defined URL aliases and seller "movable pointer" naming (see below). |
| `b/` | **Broadcast** | Fan-out a single request to multiple services. |
| `c/` | **Chain** | Sequence two or more services. |
| `d/` | **Delayed dispatch** | Register a one-shot future call. |
| `f/` | **Failover** | Secondary path if the primary fails. |
| `g/` | **Groups** | Address a service group rather than a single listing. |
| `l/` | **Logging** | Force a request to be captured in the customer's call log. |
| `m/` | **Memoize** | Cache the response in the gateway. |
| `p/` | (removed) | Was the explicit `/p/<provider>` prefix; superseded by `{{ service_name }}` (#1138). |
| `r/` | **Recurrent** | Register a recurring scheduled call. |
| `t/` | **Tee** | Fire-and-forget mirror of a request to a second service. |

## The `a/` movable-pointer convention (#1139)

`/a/<alias>` is a customer-facing **movable pointer**: *"this URL is a
movable pointer — the publisher reserves the right to re-point the
underlying target at a newer listing later."* It carries no special
routing behavior at the listing layer; gateway-side, `a/<rest>` resolves
like any other listing path. The benefit is social: customers see which
URLs are stable (`{{ service_name }}` → a sticky listing identifier) and
which are intentionally mutable (`a/cohere-latest`).

```toml
base_url = "${API_GATEWAY_BASE_URL}/a/cohere-latest"
base_url = "${API_GATEWAY_BASE_URL}/a/anthropic/claude-opus-latest"
base_url = "${API_GATEWAY_BASE_URL}/a/cohere-latest/{{ enrollment_vars.code }}"
```

After the leading `a/` is stripped, the remaining alias is validated
under the normal grammar: bare `a/` is rejected, `a/x` is rejected
(single-char), and other primitive prefixes are not part of the
carve-out. Use `/a/` only when you intend to re-point the URL over time;
for the common case — a stable, sticky service — use
`${API_GATEWAY_BASE_URL}/{{ service_name }}`.

## Selecting services by name on the CLI

The CLI selects services by `service_name` (= `listing.name`). The
**`--name`** option is an **fnmatch pattern**: a literal name matches one
service, while wildcards (`cohere/*`, `*llama*`) match a set. `*` spans
`/`, and matching is case-sensitive.

```bash
# Local data commands — exact name (one service) or a pattern (a set)
usvc_seller data run-tests  --name cohere/command-r-plus
usvc_seller data list-tests --name 'cohere/*'
usvc_seller data upload     --name 'cohere/*'
usvc_seller data show-test  cohere/command-r-plus

# Remote service commands — every backend row whose service_name matches
# (a name can also map to several rows, e.g. an active service + its
# pending revision)
usvc_seller services submit        --name 'cohere/*'
usvc_seller services set-visibility public --name cohere/command-r-plus
```

`--provider` remains a separate axis: it scopes by the provider slug and
is the only way to select a provider's **top-level** services (whose
`service_name` is bare, with no `provider/` prefix, so a `provider/*`
pattern can't reach them).

## Validating locally

Before uploading, run:

```bash
usvc_seller data validate          # schema + naming validation
usvc_seller data format --check    # CI-style formatting check
```

Both run the same validators the platform uses on upload; catching
issues locally avoids a round-trip through `usvc_seller data upload` just
to see the rejection.

## Related

- Naming convention & `/p/` removal — [`unitysvc/unitysvc#1138`](https://github.com/unitysvc/unitysvc/issues/1138).
- `/a/` movable-pointer umbrella — [`unitysvc/unitysvc#1139`](https://github.com/unitysvc/unitysvc/issues/1139).
- Validator implementation — [`unitysvc-core`](https://github.com/unitysvc/unitysvc-core)
  (`validate_listing_gateway_base_urls`, `validate_service_identifier`).
