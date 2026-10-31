# File Schemas

Complete reference for all data file schemas used in the UnitySVC Services SDK.

## Overview

A service is described by three files in its `specs/<provider>/<service>/`
folder. A file's **type is its filename** — there is no `schema` field inside
the data. The schemas (with their historical version names) are:

- `provider.json` (`provider_v1`) - Provider metadata and upstream access configuration
- `offering.json` (`offering_v1`) - Service offering details (upstream provider perspective)
- `listing.json` (`listing_v1`) - Service listing (user-facing marketplace perspective)
- `service_group.json` (`service_group_v1`) - Service group definitions for organizing services

### Upstream access channels vs. user access interfaces

Two terms recur throughout these schemas, and they name **orthogonal** axes — don't conflate them:

- An **upstream access channel** ("channel") is one named entry in an offering's `upstream_access_config`. Each channel is a complete way for the gateway to reach the upstream: a protocol (`access_method`: `http`, `smtp`, `s3` or `mcp`), a rank (`sort_order`), the enrollment parameters it asks for (`params`), and one or more typed **servers** holding the connection (`base_url`, `api_key`, `routing_key`, …). Channel names are short identifiers (e.g. `"managed"`, `"byok"`, `"plus"`, `"managed-eu"`). The gateway selects one channel per request. A channel answers *how the request is fulfilled and billed*, and is gated by **secret** availability (and, for an enrollable channel, enrollment). See [Upstream access channels](#upstream-access-config).
- A **user access interface** is one named entry in a listing's `user_access_interfaces`: the service's canonical, customer-facing address on one of the platform gateways. The platform adds the other ways to reach it (`/a/<alias>`, `/g/<group>`, `/e/<CODE>` for an enrollment). An interface answers *how you connect*. See [Canonical user access interfaces](#canonical-user-access-interfaces).

Channel selection happens per request regardless of which interface URL the customer hits, so the two are separable lists, not a matrix.

## Schema: provider_v1

Provider files define the service provider's metadata and access configuration for automated service population.

### Required Fields

| Field           | Type                | Description                                                               |
| --------------- | ------------------- | ------------------------------------------------------------------------- |
| `name`          | string              | Provider identifier (URL-friendly: lowercase, hyphens, underscores, dots) |
| `homepage`      | string (URL)        | Provider website URL                                                      |
| `contact_email` | string (email)      | Contact email address                                                     |
| `time_created`  | datetime (ISO 8601) | Timestamp when the provider was created                                   |

### Optional Fields

| Field                     | Type                 | Description                                                     |
| ------------------------- | -------------------- | --------------------------------------------------------------- |
| `display_name`            | string               | Human-readable provider name (max 200 chars)                    |
| `description`             | string               | Provider description                                            |
| `secondary_contact_email` | string (email)       | Secondary contact email                                         |
| `logo`                    | string/URL           | Path to logo file or URL (converted to document during import)  |
| `terms_of_service`        | string/URL           | Path to terms file or URL (converted to document during import) |
| `documents`               | dict of DocumentData | Documents keyed by title                                        |
| `services_populator`      | object               | Automated service generation configuration                      |
| `status`                  | enum                 | Provider status: `draft` (default), `ready`, or `deprecated`    |
| `rate_limits`             | array of RateLimit   | What this provider grants **your account** — see [RateLimit Object](#ratelimit-object) |

### services_populator Object

Configuration for automatically populating service data, declared in **`templates/config.json`** (not in `provider.json`) and run by `usvc seller specs populate`.

| Field          | Type                   | Description                                                                               |
| -------------- | ---------------------- | ----------------------------------------------------------------------------------------- |
| `command`      | string or list[string] | Command to execute (string or list of arguments). Relative to the repo root.         |
| `requirements` | array of strings       | Python packages to install before executing (e.g., `["httpx", "any-llm-sdk[anthropic]"]`) |
| `envs`         | object                 | Environment variables to set when executing the command (values converted to strings)     |

**Notes:**

- Comment out or omit `command` to disable population for a provider
- `requirements` packages are installed via pip before running the command
- `envs` values are converted to strings and set as environment variables

### Example (TOML)

```toml
name = "openai"
display_name = "OpenAI"
description = "Leading AI research laboratory"
contact_email = "support@openai.com"
homepage = "https://openai.com"
time_created = "2024-01-15T10:00:00Z"
status = "ready"

[services_populator]
command = "populate_services.py"
requirements = ["httpx", "openai"]

[services_populator.envs]
UNITYSVC_API_KEY = "sk-YOUR-API-KEY"
SERVICE_BASE_URL = "https://api.openai.com/v1"
```

### Example (JSON)

```json
{
    "name": "openai",
    "display_name": "OpenAI",
    "description": "Leading AI research laboratory",
    "contact_email": "support@openai.com",
    "homepage": "https://openai.com",
    "time_created": "2024-01-15T10:00:00Z",
    "status": "ready",
    "rate_limits": [
        { "name": "openai_concurrency", "limit": 10, "unit": "concurrent" },
        { "name": "openai_perminute", "limit": 600, "unit": "requests", "window": "minute" }
    ],
    "services_populator": {
        "command": "populate_services.py",
        "requirements": ["httpx", "openai"],
        "envs": {
            "UNITYSVC_API_KEY": "sk-YOUR-API-KEY",
            "SERVICE_BASE_URL": "https://api.openai.com/v1"
        }
    }
}
```

## Schema: offering_v1

Service files define the service offering from the upstream provider's perspective.

### Required Fields

| Field                        | Type                        | Description                                                                                                                                                                       |
| ---------------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                       | string                      | Service identifier (must match directory name, allows slashes for hierarchy)                                                                                                      |
| `summary`                    | string (max 200)            | One-line marketplace summary, shown on collapsed catalog rows and cards (unitysvc#1838)                                                                                          |
| `description`                | string                      | Long-form service description (the summary carries the teaser; no paragraph conventions)                                                                                          |
| `upstream_access_config` | dict of channel objects | How the gateway reaches the upstream, keyed by **channel name**; each entry is a typed **upstream access channel** (see [Upstream access channels](#upstream-access-config)). String values may be templates (`{{ params.X }}`, `{{ enrollment.code }}`, `${ secrets.X }`, …), rendered at gateway routing time. |
| `time_created`               | datetime (ISO 8601)         | Timestamp when offering was created                                                                                                                                               |

### Optional Fields

| Field          | Type                  | Description                                                   |
| -------------- | --------------------- | ------------------------------------------------------------- |
| `service_type` | enum or null | Optional category, with no default; omit it when no category applies. Core 0.3.4 adds `communication` (Commons) and `buy_and_sell`. |
| `display_name` | string                | Human-readable service name for display (e.g., 'GPT-4 Turbo') |
| `capabilities` | array of string       | Specific features this service provides (see [Capabilities](#capabilities)) |
| `logo`         | string/URL            | Path to logo or URL (converted to document)                   |
| `tags`         | array of enum         | Service tags (e.g., `["byok"]` for bring-your-own-provider)   |
| `status`       | enum                  | Offering status: `draft` (default), `ready`, or `deprecated`  |
| `details`      | object                | Service-specific features and information                     |
| `payout_price` | [Pricing](pricing.md) | Seller pricing information (what seller charges UnitySVC)     |
| `documents`    | dict of DocumentData  | Technical specs, documentation, keyed by title                |
| `exports`      | object                | What other services may request from this one: named permissions and a JSON Schema of customization options (see [Exports & Dependencies](exports-and-dependencies.md#exports)) |

### ServiceType Enum Values

`service_type` is optional and has no default. It describes how the platform
handles a service; capabilities describe what it does and tags describe its
industry or audience. Omitting the type does not classify the offering as an LLM.

- Models: `llm`, `embedding`, `image_generation`
- Delivery: `notification`, `email`, `content`, `streaming`
- Infrastructure: `compute`, `proxy`, `gateway`, `mcp`, `database`, `monitoring`, `analytics`
- Applications: `communication`, `buy_and_sell`

### Capabilities

A **capability is a concrete action with a defined input and output**: what your
service does to what the caller sends it. One service may have several.

Each entry in `capabilities` takes one of two forms:

```text
capability := official_id
            | name " | " explanation
```

```json
"capabilities": [
  "chat",
  "seat-availability-watch | Watches the flights and dates you specify until your deadline; reports a matching seat when found. Does not reserve or purchase tickets."
]
```

- A **bare** entry (`"chat"`) refers to an **official capability** from the
  vocabulary below. Its meaning, input/output contract and help topic come from
  the platform. It must match an official id **exactly**; any other bare string
  is rejected when you upload.
- An **annotated** entry (`"name | explanation"`) is your own declaration about
  this one service, for when no official capability fits. See
  [Declaring your own capability](#declaring-your-own-capability).

The marketplace uses capabilities to filter the catalog and to explain your
service to customers, and the gateway uses some of them for routing.

#### Keep the axes separate

This is the mistake to avoid — each of these answers a different question, and
collapsing them is what makes a catalog unsearchable:

| Field | Question it answers | Example |
|---|---|---|
| `service_type` | What *kind* of service is this? (broad category, validated enum) | `llm` |
| `capabilities` | What does it *do* to the input? (this vocabulary) | `["chat"]` |
| `input_formats` | What wire contract must the caller speak? | `openai_chat` |
| `details` | What *qualifies* the service? (attributes, free-form) | `{"context_length": 128000}` |

Concretely: an OpenAI-dialect and an Anthropic-dialect chat service offer the
**same capability** (`chat`) and differ only in `input_formats`. `tools` and
`thinking` are **not capabilities** — they have no contract of their own, they
only qualify a chat call — so they belong in `details`.

A chat model that also accepts images declares **both** `chat` and
`image-text-to-text`. The gateway routes requests containing images only to
services that declare `image-text-to-text`, and `/models` advertises image input
from it. Don't write `vision`: it is not an official id, so it is rejected.

#### The vocabulary

Each capability below links to its topic on the marketplace, which spells out
the full input/output contract customers will see.

**Passthrough** — the platform does not interpret the payload:

| Capability | Input | Output |
|---|---|---|
| [`http-relay`](https://unitysvc.com/topics/capability-http-relay) | an HTTP request of any shape | the upstream's HTTP response, unchanged |
| [`sink`](https://unitysvc.com/topics/capability-sink) | an HTTP request of any shape | a fixed HTTP status, with no upstream involved |
| [`notification-relay`](https://unitysvc.com/topics/capability-notification-relay) | a request in your messaging provider's own format | the provider's response, with the message sent |
| [`smtp-relay`](https://unitysvc.com/topics/capability-smtp-relay) | an SMTP message | the same message, relayed on to an SMTP upstream |
| [`smtp-to-http`](https://unitysvc.com/topics/capability-smtp-to-http) | an SMTP message | an HTTP POST to a configured destination |
| `http-to-smtp` | an HTTP request carrying an email payload or a message envelope | that message delivered to an SMTP server as real mail |
| [`mcp-delegation`](https://unitysvc.com/topics/capability-mcp-delegation) | a discovery request, or a tool call | the upstream server's tool list, or that call's result |
| [`s3-read-proxied`](https://unitysvc.com/topics/capability-s3-read-proxied) | an S3 GET for an object (read only) | the object bytes, streamed through the gateway |
| [`s3-read-redirect`](https://unitysvc.com/topics/capability-s3-read-redirect) | an S3 GET for an object (read only) | a presigned redirect; the client fetches the bytes |

**Messaging and monitoring:**

| Capability | Input | Output |
|---|---|---|
| [`deliver-message`](https://unitysvc.com/topics/capability-deliver-message) | a `msg` envelope (`{title, body, type, format}`) | the message delivered to the channel you configured |
| [`deliver-to-mailbox`](https://unitysvc.com/topics/capability-deliver-to-mailbox) | a `msg` envelope, or an SMTP message | an email in your own verified UnitySVC mailbox |
| [`probe-target`](https://unitysvc.com/topics/capability-probe-target) | a target to check — URL or host, check type, timeout | a verdict, with the measured response time |

**Model inference:**

| Capability | Input | Output |
|---|---|---|
| [`chat`](https://unitysvc.com/topics/capability-chat) | a conversation, optionally with images, tools or a system prompt | generated text, optionally including tool calls |
| [`image-text-to-text`](https://unitysvc.com/topics/capability-image-text-to-text) | one or more images plus a text instruction | generated text answering the instruction |
| [`embed`](https://unitysvc.com/topics/capability-embed) | text, or an image, to be represented as a vector | an embedding vector |
| [`rerank`](https://unitysvc.com/topics/capability-rerank) | a query and a set of candidate documents | the same documents ordered by relevance, with scores |
| [`moderate`](https://unitysvc.com/topics/capability-moderate) | text or an image to be assessed | a safety classification, by category |
| [`image-generate`](https://unitysvc.com/topics/capability-image-generate) | a text prompt | a generated image |
| [`image-edit`](https://unitysvc.com/topics/capability-image-edit) | an existing image and a text instruction | a modified image |
| [`video-generate`](https://unitysvc.com/topics/capability-video-generate) | a text prompt | a generated video |
| [`speech-to-text`](https://unitysvc.com/topics/capability-speech-to-text) | recorded audio | a text transcript |
| [`text-to-speech`](https://unitysvc.com/topics/capability-text-to-speech) | text, and a voice selection | synthesized audio |

`chat` absorbs **every** chat variant — the OpenAI and Anthropic dialects, the
Bedrock Converse and InvokeModel surfaces, provider SDKs, streaming and function
calling. All produce generated text, so all are one capability. Use it instead
of `llm` or `text-generation`, which are rejected.

Ids are hyphenated and case-sensitive: `http_relay`, `Chat` and `speech_to_text`
are not official ids and are rejected.

#### Declaring your own capability

When no official capability describes what your service does, declare your own
as `name | explanation`:

```json
"capabilities": [
  "invoice-extract | Reads an invoice PDF you upload and returns the vendor, date, line items and totals as JSON. Handwritten invoices are not supported."
]
```

- **The name** is a short label shown on the capability pill. Use lower-case,
  hyphenated words, like the official ids.
- **The explanation** is what customers read when they hover over the pill, so
  it is your service's contract. Say what the caller sends, what they get back,
  when (immediately, or after a wait), and what it does *not* do. "AI-powered",
  "fast" or a provider name is not an explanation.
- The marketplace shows it as **described by the seller**: your words, not a
  platform definition and not a verification.
- It never takes on an official meaning, even when the name matches an official
  id: `chat | …` is your own claim, not the official `chat` contract, and the
  gateway does not route on it.
- Customers filter on the **whole** string, so two declarations with the same
  name but different explanations are different capabilities.

Rules checked when you upload:

| Rule | Limit |
|---|---|
| Name | required, at most 64 characters |
| Explanation | required after the separator, at most 500 characters |
| Characters | no tabs, newlines or other control characters |
| Entries | at most 32 capabilities per offering |

The text is split at the **first** `|`; whitespace around the name and the
explanation is trimmed, and any later `|` is part of the explanation.

If your service does something many sellers offer, **open an issue**. A
recurring capability can become official. When it does, your declaration keeps
working unchanged; switch to the bare official id in a normal update once your
service matches the official contract.

**Examples:**

| Service | `service_type` | `capabilities` |
|---------|---------------|----------------|
| OpenAI GPT-4o (accepts images) | `llm` | `["chat", "image-text-to-text"]` |
| Deepgram Nova | `speech_to_text` | `["speech-to-text"]` |
| An SMTP gateway that POSTs to a webhook | `notification` | `["smtp-to-http"]` |

A service with no official capability uses the annotated form instead, as in
the `invoice-extract` example under
[Declaring your own capability](#declaring-your-own-capability).

### Example (TOML)

```toml
name = "gpt-4"
display_name = "GPT-4"
description = "Most capable GPT-4 model for complex reasoning tasks"
service_type = "llm"
capabilities = ["chat", "image-text-to-text"]
status = "ready"
time_created = "2024-01-20T14:00:00Z"

# Attributes that QUALIFY the capability — tool use, context size — belong
# here, not in `capabilities`. Image input is the `image-text-to-text`
# capability above, because the gateway routes image requests on it.
[details]
vision = true
context_window = 128000
max_output_tokens = 4096
supports_function_calling = true
supports_vision = true

[upstream_access_config.managed]
base_url = "https://api.openai.com/v1"
api_key = "${ secrets.OPENAI_API_KEY }"

[payout_price]
currency = "USD"

[payout_price.price_data]
type = "one_million_tokens"
input = "30.00"
output = "60.00"
```

### Upstream access channels (`upstream_access_config`) {#upstream-access-config}

`upstream_access_config` says how the gateway reaches the upstream. It maps a **channel name** to a **channel**; each channel is one complete way to reach the upstream (its protocol, credential, rank, what it asks the enrolling customer for, and its servers), and the gateway picks one channel per request.

Since `unitysvc-core` 0.3.0 (unitysvc-sellers after 0.3.14) channels are typed (`UpstreamAccessConfig` / `ChannelConfig`, unitysvc/unitysvc#2730): `usvc seller specs validate` checks every field below, refuses unknown keys, and refuses [retired keys](#retired-and-unknown-channel-keys) with what to do instead.

```json
"upstream_access_config": {
  "managed": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "${ secrets.OPENAI_API_KEY }"
  }
}
```

#### Channel names

The name is the dict key. It is also the value `<service>@<channel>` selects and the key of [channel-keyed pricing](pricing.md#channel-based-pricing-channel), so it follows the variant-tag grammar (`validate_channel_name`):

- non-empty, and **no `@`** (the `<name>@<channel>` selector delimiter);
- one or more `/`-separated segments, each made of letters, digits, `.`, `-` and `_`, starting with a letter or digit (single-character names are allowed).

`managed`, `byok`, `plus`, `managed-eu`, `s3_upstream` are valid; `OpenAI API` (space), `plus@eu` (`@`) and `-plus` (leading `-`) are refused.

#### Channel keys

These keys describe the channel as a whole. The connection itself lives in [servers](#servers).

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `access_method` | `"http"` \| `"smtp"` \| `"s3"` \| `"mcp"` | `"http"` | The upstream protocol. It selects the server type: [HTTP](#http-servers), [SMTP](#smtp-servers), [S3](#s3-servers) or [MCP](#mcp-servers). Any other value is refused: `access_method must be one of 'http', 'smtp', 's3', 'mcp'`. |
| `type` | `"unbound"` \| `"secret_bound"` \| `"enrollable"` \| `"me_bound"` \| `"external"` | derived | Normally derived by the platform from the channel's configuration; declare `external` (or `enrollable`) to state it. |
| `description` | string | none | Display text. |
| `is_active` | boolean | `true` | Inactive channels are skipped. |
| `sort_order` | integer | none | Channel rank, lowest first. Replaces `is_primary`. |
| `request_formats` | array of string | none | The request formats the channel serves. |
| `applicable_interfaces` | array of string | none | The user access interfaces that reach this channel (display only). |
| `rate_limit_refs` | array of string | none | Names of the provider's rate limits this channel consumes; see [Provider-account rate-limit refs](#provider-account-rate-limit-refs). |
| `customer_access_requests` | array of object | none | What the enrolling customer is asked to approve: named services or platform resources such as `resource:room`. See [Exports & Dependencies](exports-and-dependencies.md#customer-access-requests). Formerly `grants`. |
| `params` | object | none | The enrollment parameters the channel reads. See [Enrollment Parameters](#enrollment-parameters). |
| `servers` | array of server | `[]` | The connection, typed by `access_method`. See [Servers](#servers). |

The channel name is the dict key, never a field.

#### Servers

A channel's connection lives in `servers`, a list of servers of the channel's protocol. The common one-server case writes the connection fields **directly on the channel** instead; they are read as `servers[0]`. These two channels are the same:

```json
"managed": {
  "base_url": "https://api.deepseek.com",
  "api_key": "${ secrets.DEEPSEEK_API_KEY }"
}
```

```json
"managed": {
  "servers": [
    { "base_url": "https://api.deepseek.com", "api_key": "${ secrets.DEEPSEEK_API_KEY }" }
  ]
}
```

When a channel has **both** direct connection fields and `servers`, each server inherits every direct field it does not set itself (the gateway's rule). Write shared values (a `routing_key`, an `api_key`) once on the channel and only what differs on each server. How the gateway spreads load and fails over across servers is described in [Multi-server channels](service-types.md#multi-server-channels-capacity-failover).

Every server, whatever its protocol, may set:

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Server name, unique within the channel |
| `weight` | integer | Relative share of traffic among the channel's servers |
| `acceptable_formats` | array of string | Request formats this server accepts |

Unknown server fields are refused, as on the channel.

##### HTTP servers

`access_method: "http"` (the default). An HTTP upstream, or a platform service named by a scheme such as `notify://` or `me://`.

| Field | Type | Description |
| --- | --- | --- |
| `base_url` | string, **required** | Upstream base URL |
| `api_key` | string | The upstream credential: a secret reference, or one of the dispositions `""`, `"__strip__"`, `"__forward__"`, `"__sigv4__"` (see [api_key values](#api_key-values)) |
| `routing_key` | object | Values the gateway routes on, e.g. `{"model": "gpt-4o"}` |
| `upstream_format` | string | The request format the upstream speaks |
| `request_transformer` | object | How the gateway rewrites a request before sending it upstream (see [request_transformer](#request_transformer)) |
| `access_key`, `secret_key`, `session_token`, `region` | string | AWS SigV4 signing credentials, used with `api_key: "__sigv4__"` |
| `sigv4_service` | string | AWS service name in the SigV4 credential scope, e.g. `"bedrock"` |
| `method` | string | Delivery to an HTTP endpoint (smtp-gateway, notify): the HTTP method |
| `payload_format` | string | Delivery: body format sent upstream, e.g. `msg` |
| `auth_mode` | string | Delivery: `forward`, `static`, `customer_token` or `none` |
| `auth_token` | string | Delivery: the token for `auth_mode` |
| `headers` | object of string | Delivery: extra request headers |
| `max_message_bytes` | integer or string | Delivery: largest message accepted |
| `tls_verify` | boolean or string | Delivery: verify the upstream's TLS certificate |
| `smtp_target`, `smtp_host`, `smtp_username`, `smtp_password`, `mail_from`, `mail_to` | string | `notify://smtp` delivery |
| `smtp_port` | integer or string | `notify://smtp` delivery |
| `smtp_tls` | boolean or string | `notify://smtp` delivery |

###### `api_key` values

On a channel or server, `api_key` is either a credential reference or a **disposition** saying what the gateway does with the customer's UnitySVC key (svcpass) on the way upstream:

| Value | Meaning |
| --- | --- |
| `${ secrets.NAME }` | The seller's credential (a managed channel) |
| `${ customer_secrets.NAME }`, `${ customer_secrets.NAME ?? default }` | The customer's credential (BYOK), optionally with a fallback |
| `${ customer_secrets.{{ params.X }} }` | A customer credential whose secret name the customer gives at enrollment as parameter `X` |
| `""` or `"__strip__"` | Strip the header that carries svcpass; send no credential |
| `"__forward__"` | Forward svcpass verbatim. Only to a trusted platform host: `base_url` must have a literal host that is `svcpass.com`, `unitysvc.com`, or a subdomain of either; a templated, missing or external host is refused |
| `"__sigv4__"` | Strip the client credential and re-sign the finalized request with AWS SigV4. Requires non-empty `access_key`, `secret_key` and `sigv4_service` (usually secret references); `session_token` is optional and `region` defaults to `us-east-1` |

Any other value is refused: a plain-text key never appears in a spec. (A Jinja `{% … %}` conditional that renders to one of the forms above is accepted.) The dispositions are valid only on a channel or server; a parameter value such as `params.testing_defaults.api_key` must be a secret reference.

###### `request_transformer`

| Key | Type | Description |
| --- | --- | --- |
| `llm_translator` | string or object | Translate between LLM request dialects (a preset name or its config) |
| `msg_transformer` | object | Map the standard `msg` envelope |
| `proxy_rewrite` | object | Rewrite the upstream path and headers |
| `body_transformer` | object | Rewrite the request body |
| `set_body` | string | Replace the request body with this template |

Unknown keys are refused.

##### SMTP servers

`access_method: "smtp"`. An SMTP relay.

| Field | Type | Description |
| --- | --- | --- |
| `host` | string, **required** | Relay host |
| `port` | integer or string | Relay port |
| `username` | string | SMTP AUTH username |
| `password` | string | SMTP AUTH password (a secret reference) |
| `tls` | boolean or string | Use TLS |
| `to` | string | Recipient that replaces the message's own |

##### S3 servers

`access_method: "s3"`. An S3-compatible bucket. (This replaces the retired `storage_type: "s3"` on an `http` channel.)

| Field | Type | Description |
| --- | --- | --- |
| `bucket` | string, **required** | Bucket name |
| `region` | string | Bucket region |
| `s3_endpoint` | string | Endpoint of an S3-compatible store (R2, MinIO, …) |
| `access_key`, `secret_key`, `session_token` | string | Credentials (secret references) |
| `base_path` | string | Key prefix inside the bucket |
| `addressing_style` | `"path"` \| `"virtual"` | Path-style or virtual-hosted-style bucket addressing |
| `proxy_mode` | `"proxy"` \| `"redirect"` | Stream objects through the gateway (`proxy`), or answer with a presigned redirect the client follows (`redirect`, the default) |

##### MCP servers

`access_method: "mcp"`. A remote MCP server (streamable HTTP). An offering with an MCP channel must have `service_type: "mcp"`, and an `mcp` service must have at least one MCP channel.

| Field | Type | Description |
| --- | --- | --- |
| `base_url` | string, **required** | The MCP server's URL |
| `auth_mode` | string | `customer_token`, `forward`, `static` or `none` |
| `api_key` | string | Credential (a secret reference) |
| `credential` | string | Credential (a secret reference) |
| `headers` | object of string | Extra request headers |
| `allowed_hosts` | array of string | Hosts the server may be reached on |

#### Templates in channel values

Any string in a channel or server may be a template. The platform renders it **per request, at gateway routing time**, for the enrollment (if any) the request belongs to:

| Form | Value |
| --- | --- |
| `{{ params.X }}` | The enrollment's parameter `X`, declared in this channel's [`params`](#enrollment-parameters) |
| `{{ enrollment.code }}`, `{{ enrollment.id }}` | The enrollment's 4-character code and its id |
| `{{ routing_vars.X }}` | The listing's `service_options.routing_vars.X` |
| `${ secrets.X }` | The seller's secret `X` |
| `${ customer_secrets.X }` | The customer's secret `X` |
| `${ customer_secrets.X ?? default }` | The customer's secret `X`, or `default` when they have none |
| `${ customer_secrets.{{ params.X }} }` | The customer's secret named by parameter `X` |

Because any connection field may be a template, the numeric and boolean connection fields (`port`, `smtp_port`, `max_message_bytes`, `tls`, `smtp_tls`, `tls_verify`) also accept strings, such as `"port": "{{ params.port }}"`.

A secret reference must render to `${ secrets.NAME }` / `${ customer_secrets.NAME }` with a plain identifier (letters, digits, `_`), optionally with `?? default`. Bracket lookup and composite expressions are refused. `specs validate` renders `{{ params.X }}` with the channel's `params.testing_defaults` and `{{ routing_vars.X }}` with the listing's `service_options.routing_vars`, so an undefined name is an error.

The gateway renders these templates across the **whole** channel, `request_transformer` included, and a channel with any `{{ … }}` left unresolved is unroutable. A transformer's own per-request template must therefore use `{* … *}` rather than `{{ … }}`. See [Templates inside transformers](tech-notes/user-access-interface-template.md#templates-inside-transformers).

#### Retired and unknown channel keys

A channel refuses any key not listed above (or, for the one-server shorthand, in its server table). These retired keys are refused with an error of the form `'<key>' is not supported: <what to do instead>`:

| Key | What to do instead |
| --- | --- |
| `raw` | move its keys onto the channel (or server) itself |
| `is_primary` | channels rank by `sort_order` (lowest first); remove `is_primary` |
| `user_parameters_schema` | declare the channel's parameters as `params.schema` |
| `user_parameters_ui_schema` | move it to `params.ui_schema` |
| `ops_testing_parameters` | move it to `params.testing_defaults` |
| `grants` | renamed to `customer_access_requests` |
| `rate_limits` | nothing reads a channel's `rate_limits`; declare limits on the provider and name them in `rate_limit_refs`, or remove it |
| `storage_type` | set `access_method` `s3` instead |
| `response_rules` | no gateway reads it; remove it |
| `timeout_ms` | no gateway reads it; remove it |
| `transport` | no gateway reads it; remove it |
| `customer_secrets_required` | the platform derives it at upload; remove it |
| `customer_secrets_optional` | the platform derives it at upload; remove it |

Other keys that older docs or specs used, such as `ops_rate_limit_refs` and `depends_on` (now `customer_access_requests`), are simply unknown and refused. See [Migrating to unitysvc-core 0.3.0](#migrating-to-unitysvc-core-030).

#### Examples

**An LLM with a managed channel and a BYOK channel.** One-server shorthand: the connection fields sit on the channel. The managed channel ranks first and spends the seller's provider quota; the BYOK channel uses the customer's own key.

```json
"upstream_access_config": {
  "managed": {
    "base_url": "https://api.fireworks.ai/inference/v1",
    "api_key": "${ secrets.FIREWORKS_API_KEY }",
    "routing_key": { "model": "accounts/fireworks/models/glm-5" },
    "rate_limit_refs": ["fireworks_concurrency", "fireworks_perminute"],
    "sort_order": 0
  },
  "byok": {
    "base_url": "https://api.fireworks.ai/inference/v1",
    "api_key": "${ customer_secrets.FIREWORKS_API_KEY }",
    "routing_key": { "model": "accounts/fireworks/models/glm-5" },
    "sort_order": 1
  }
}
```

**A multi-server channel.** The `routing_key` is written once on the channel and inherited by both servers.

```json
"upstream_access_config": {
  "managed": {
    "routing_key": { "model": "deepseek-v4-pro" },
    "servers": [
      { "name": "primary", "base_url": "https://api.deepseek.com", "api_key": "${ secrets.DEEPSEEK_KEY_A }", "weight": 3 },
      { "name": "backup", "base_url": "https://api-backup.deepseek.com", "api_key": "${ secrets.DEEPSEEK_KEY_B }", "weight": 1 }
    ]
  }
}
```

**An enrollable `plus` channel beside a free channel.** The `plus` channel reads two enrollment parameters and declares them in its own `params`; a request to the canonical address is served by `byok`, and each `plus` enrollment is reached at `/e/<CODE>`.

```json
"upstream_access_config": {
  "byok": {
    "base_url": "${ customer_secrets.HTTP_RELAY_BASE_URL }",
    "api_key": "${ customer_secrets.HTTP_RELAY_API_KEY }"
  },
  "plus": {
    "base_url": "{{ params.base_url }}",
    "api_key": "${ customer_secrets.{{ params.api_key_secret }} }",
    "params": {
      "schema": {
        "type": "object",
        "properties": {
          "base_url": { "type": "string", "title": "Upstream URL" },
          "api_key_secret": { "type": "string", "title": "Secret holding your API key", "default": "HTTP_RELAY_API_KEY" }
        },
        "required": ["base_url", "api_key_secret"]
      },
      "ui_schema": { "base_url": { "ui:placeholder": "https://api.example.com" } },
      "testing_defaults": {
        "base_url": "https://mock.unitysvc.dev/http",
        "api_key_secret": "HTTP_RELAY_API_KEY"
      }
    }
  }
}
```

**An SMTP relay.**

```json
"upstream_access_config": {
  "mail_relay": {
    "access_method": "smtp",
    "host": "smtp.sendgrid.net",
    "port": 587,
    "tls": true,
    "username": "apikey",
    "password": "${ secrets.SENDGRID_API_KEY }"
  }
}
```

**An S3 bucket.**

```json
"upstream_access_config": {
  "s3_upstream": {
    "access_method": "s3",
    "bucket": "demo",
    "region": "us-east-1",
    "s3_endpoint": "https://s3.example.com",
    "base_path": "demo/",
    "access_key": "${ secrets.S3_ACCESS_KEY }",
    "secret_key": "${ secrets.S3_SECRET_KEY }",
    "proxy_mode": "proxy"
  }
}
```

**A remote MCP server** (`service_type: "mcp"`):

```json
"upstream_access_config": {
  "upstream": {
    "access_method": "mcp",
    "base_url": "https://mcp.example.com/mcp",
    "auth_mode": "none"
  }
}
```

#### Provider-account rate-limit refs

Provider-level `rate_limits` define **named seller-scoped buckets**. A channel
opts into those buckets with `rate_limit_refs` (a channel's own `rate_limits`
is retired):

Provider file:

```json
{
  "name": "fireworks",
  "contact_email": "ops@example.com",
  "homepage": "https://fireworks.ai",
  "time_created": "2026-01-01T00:00:00Z",
  "rate_limits": [
    { "name": "fireworks_concurrency", "unit": "concurrent", "limit": 8 },
    { "name": "fireworks_perminute", "unit": "requests", "limit": 60, "window": "minute" }
  ]
}
```

Offering file:

```json
{
  "upstream_access_config": {
    "managed": {
      "base_url": "https://api.fireworks.ai/inference/v1",
      "api_key": "${ secrets.FIREWORKS_API_KEY }",
      "rate_limit_refs": ["fireworks_concurrency", "fireworks_perminute"]
    }
  }
}
```

Any selected channel referencing `fireworks_perminute` consumes the same seller
bucket for that seller, even across services or provider records. Use the same
name when multiple channels spend the same upstream account quota; use different
names when different API keys/accounts have independent quotas. Do not put
`rate_limit_refs` on a BYOK channel: production BYOK traffic spends the
customer's provider quota, not yours.

## Schema: listing_v1

Listing files define how a seller presents/sells a service to end users.

**Relationship by Location**: Listings automatically belong to the single offering in the same directory. The provider is determined by the parent directory structure. No explicit linking fields are needed.

### Required Fields

| Field                    | Type                        | Description                                 |
| ------------------------ | --------------------------- | ------------------------------------------- |
| `user_access_interfaces` | dict of AccessInterfaceData | How users access the service, keyed by name. A **pure routing object** (address + routing key + visibility) — see [User access interface object](#user-access-interface-object). |
| `time_created`           | datetime (ISO 8601)         | Timestamp when listing was created          |

### Optional Fields

| Field                       | Type                  | Description                                                                                      |
| --------------------------- | --------------------- | ------------------------------------------------------------------------------------------------ |
| `name`                      | string                | The service identifier, `<provider>/<service-name>[@variant]` (required in practice; see [Names & Routing](naming-conventions.md)), max 255 chars |
| `display_name`              | string                | Customer-facing name (max 200 chars)                                                             |
| `status`                    | enum                  | Status: `draft` (skip upload), `ready` (ready for review), `deprecated`                          |
| `list_price`                | [Pricing](pricing.md) | Customer-facing pricing (what customer pays)                                                     |
| `documents`                 | dict of DocumentData  | SLAs, documentation, guides, keyed by title                                                      |
| `service_options`           | object                | Service-specific options (see [Service Options](#service-options))                               |

A listing declares **no enrollment parameters**: `user_parameters_schema` and `user_parameters_ui_schema` are refused. Each channel declares the parameters it reads; see [Enrollment Parameters](#enrollment-parameters).
| `audience`                  | array of string       | Who the service is for and what a buyer must know before enrolling (see [Audience](#audience))   |

### Audience

`audience` is an optional list of short, plain-text phrases that tell a buyer
**who the service is for and what they must know before enrolling**:

```json
{
  "audience": [
    "Rice University students (enrollment at Rice required)",
    "US customers only / export restrictions may apply"
  ]
}
```

- The phrases are shown prominently before a customer enrolls (on the service
  page and in the enrollment dialog), and assistants such as unitysvc.ai read
  them, with a customer's own profile, to recommend services.
- They are **informational only**. UnitySVC cannot verify claims like "Rice
  student" or "US resident", so it never blocks an enrollment on them; the
  customer decides, and your own terms govern.
- Rules: at most 8 phrases, each 1-120 characters after trimming, plain text
  only (no URLs, no markup such as `<b>`, `[link](...)` or backticks, no line
  breaks), and no phrase twice. Put details in the description or documents.

`audience` complements [`capabilities`](#capabilities) on the offering:
**capabilities say what the service does; audience says who it is for.**

Validated by `unitysvc-core` 0.2.36 and later. The platform's display of the
phrases is rolling out separately (unitysvc/unitysvc#2717).

### Service Options

The `service_options` field configures backend behavior for service listings. All fields are optional.

| Field                             | Type    | Description                                                                    |
| --------------------------------- | ------- | ------------------------------------------------------------------------------ |
| `default_visibility`              | string  | Visibility applied by upload: `public`, `unlisted` or `private` (see below)    |
| `routing_vars`                    | object  | Seller-managed operational variables, read by channels as `{{ routing_vars.X }}` |
| `enrollment`                      | object  | Per-enrollment configuration: enrollment limits (see below)                    |
| `prompt_recurrence`               | boolean | Prompt for recurrence options during enrollment (see [Recurrent services](service-types.md#recurrent-services)) |
| `recurrence_min_interval_seconds` | integer | Minimum recurrence interval                                                    |
| `recurrence_max_interval_seconds` | integer | Maximum recurrence interval                                                    |
| `recurrence_allow_cron`           | boolean | Allow cron expressions                                                         |

Any other key is refused. `ops_testing_parameters` is retired: the values a channel is tested with are its [`params.testing_defaults`](#enrollment-parameters).

**Enrollment configuration (`enrollment`):**

All enrollment-related options live under a single `enrollment` object:

| Key                  | Type    | Description                                                                                                                                                                                              |
| -------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `limit`              | integer | Maximum total active enrollments for this service (global)                                                                                                                                              |
| `limit_per_customer` | integer | Maximum active enrollments per customer                                                                                                                                                                 |
| `limit_per_user`     | integer | Maximum active enrollments per user (creator)                                                                                                                                                           |
| `required`           | boolean | `true` declares that using the service requires an enrollment even when nothing in its configuration does (required parameters, an enrollable channel), e.g. for MCP services whose gate is enforced outside the routing layer |

> **No `enrollment_vars`.** Every enrollment automatically carries a unique code, available to channel templates as `{{ enrollment.code }}`; the enrollment itself is reached at `/e/<CODE>`. There is no per-enrollment variable to declare; the old `service_options.enrollment_vars` mechanism has been removed.

**Enrollment limits:**

- Limits apply only to **active** enrollments (cancelled/inactive enrollments don't count)
- Invalid values (non-integers, zero, negative, or boolean) are treated as "no limit"
- Limits are checked when creating **new** enrollments (not when updating existing ones)
- Checks are performed in order: per-customer → per-user → global

**Example (JSON):**

```json
{
    "service_options": {
        "default_visibility": "public",
        "routing_vars": {
            "region": "us-east-1"
        },
        "enrollment": {
            "limit": 100,
            "limit_per_customer": 5,
            "limit_per_user": 2
        }
    }
}
```

**Example (TOML):**

```toml
[service_options]
default_visibility = "public"

[service_options.routing_vars]
region = "us-east-1"

[service_options.enrollment]
limit = 100
limit_per_customer = 5
limit_per_user = 2
```

`service_options.default_visibility` controls the service visibility applied by
upload. Omit it for the default `unlisted` behavior, set it to `public` to
publish on activation, or set it to `private` for services that should not be
changed by `services set-visibility`. To move a private service back to
`public` or `unlisted`, update this field and re-upload the service.

### Listing Name Field

- `name` is the service identifier: `<provider>/<service-name>`, matching the folder under `specs/`, with an optional `@variant` (`openai/gpt-4@premium`)
- **Multiple listings**: put each variant in its own file (`listing-premium.json`) and give each its own `@variant` name

### status Values (Listing)

- `draft` - Work in progress, skipped during upload (default)
- `ready` - Ready for admin review and testing
- `deprecated` - No longer offered to new customers

### Canonical user access interfaces

A user access interface is the service's **canonical address**, the same for every caller. Its `base_url` starts with one of the four gateway placeholders, which the platform resolves:

| Gateway | Placeholder | Protocol | Interface shape |
| ------- | ----------- | -------- | --------------- |
| API Gateway | `${API_GATEWAY_BASE_URL}` | HTTP/HTTPS | `${API_GATEWAY_BASE_URL}` plus an optional `/` and path |
| S3 Gateway | `${S3_GATEWAY_BASE_URL}` | S3 API | `${S3_GATEWAY_BASE_URL}/<bucket alias>`; the alias must be a valid S3 bucket name (3-63 lowercase letters, digits or hyphens, starting and ending with a letter or digit) |
| SMTP Gateway | `${SMTP_GATEWAY_BASE_URL}` | SMTP | exactly `${SMTP_GATEWAY_BASE_URL}`, with a non-empty `routing_key.username` |
| MCP Gateway | `${MCP_GATEWAY_BASE_URL}` | MCP | exactly `${MCP_GATEWAY_BASE_URL}`, with `access_method: "mcp"` and a `routing_key.namespace` (lowercase letters, digits and `_`, starting with a letter or digit, at most 24 characters) |

`usvc seller specs validate` (unitysvc-core 0.3.0, `validate_listing_interfaces_are_canonical`) renders `{{ service_name }}` first (to `listing.name`), then requires:

- **A gateway address.** `base_url` is one of the four placeholders above, optionally followed by `/` and a path. Never an external URL (`https://api.example.com/v1`), another `${...}` variable, or a secret reference.
- **No other template.** `{{ service_name }}` is the only value the platform fills in when it stores an interface. Anything else, such as `{{ routing_vars.X }}`, would stay literal and never route.
- **Nothing per-enrollment.** An interface may not read `enrollment.*` or `params.*`: an enrollment is reached at **`/e/<CODE>`** on the API gateway, an address the platform provides, so don't declare an interface for it. The one exception is `{{ enrollment.code }}` as the **whole** SMTP `routing_key.username`, or the **whole** S3 bucket segment (`${S3_GATEWAY_BASE_URL}/{{ enrollment.code }}`), as a reminder of the per-enrollment address on protocols without a path for it.

On the API gateway, the first path segment is free when it has two or more characters (`{{ service_name }}`, a provider path routed by `routing_key`). Single-character first segments are reserved for platform primitives: listings may use only `/a/<alias>` (a movable pointer, see [Names & Routing](naming-conventions.md)). `${API_GATEWAY_BASE_URL}/p/<route>` is reserved for [platform services](guides/publish-platform-services.md).

```json
"user_access_interfaces": {
  "canonical": {
    "access_method": "http",
    "base_url": "${API_GATEWAY_BASE_URL}/{{ service_name }}"
  }
}
```

The other gateways:

```json
// S3
"s3_gateway": { "access_method": "http", "base_url": "${S3_GATEWAY_BASE_URL}/demo-s3" }

// SMTP
"smtp_gateway": {
  "access_method": "smtp",
  "base_url": "${SMTP_GATEWAY_BASE_URL}",
  "routing_key": { "username": "smtp-relay" }
}

// MCP
"mcp_gateway": {
  "access_method": "mcp",
  "base_url": "${MCP_GATEWAY_BASE_URL}",
  "routing_key": { "namespace": "unitysvc" }
}

// Per-enrollment reminders: the only place {{ enrollment.code }} may appear
"smtp_enrollment": {
  "access_method": "smtp",
  "base_url": "${SMTP_GATEWAY_BASE_URL}",
  "routing_key": { "username": "{{ enrollment.code }}" }
}
"s3_enrollment": { "access_method": "http", "base_url": "${S3_GATEWAY_BASE_URL}/{{ enrollment.code }}" }
```

Refused:

```text
https://api.example.com/v1                                   external URL
${API_GATEWAY_BASE_URL}/{{ service_name }}/{{ enrollment.code }}   per-enrollment; use /e/<CODE>
${API_GATEWAY_BASE_URL}/{{ params.endpoint }}                 per-enrollment
${API_GATEWAY_BASE_URL}/{{ routing_vars.region }}             template other than service_name
${API_GATEWAY_BASE_URL}/p/openai                              /p is for platform services
${API_GATEWAY_BASE_URL}/u/{{ service_name }}                  reserved single-letter prefix
${SSH_GATEWAY_BASE_URL}                                       not a gateway
```

### Example (TOML)

```toml
# File: specs/openai/gpt-4/listing-premium.toml
# This listing automatically belongs to the gpt-4 offering in the same directory
# and the openai provider in the parent directory.
name = "openai/gpt-4@premium"
display_name = "GPT-4 Premium Access"
status = "ready"
time_created = "2024-01-25T16:00:00Z"

[user_access_interfaces.canonical]
access_method = "http"
base_url = "${API_GATEWAY_BASE_URL}/{{ service_name }}"

[list_price]
currency = "USD"

[list_price.price_data]
type = "one_million_tokens"
input = "35.00"
output = "70.00"

[documents."Quick Start Guide"]
file_path = "../../docs/quick-start.md"
category = "getting_started"
mime_type = "markdown"
```

## Enrollment Parameters

Enrollment parameters collect **configuration values** from a customer when they enroll: real settings they choose (a folder, a region, their own endpoint URL, the *name* of the secret that holds their key). They are not credentials; a credential is a [secret](#secrets-seller-owned-vs-customer-owned), and a parameter may at most name one.

Since `unitysvc-core` 0.3.0 (unitysvc/unitysvc#2726), **each channel declares the parameters it reads**, in its own `params` object, so each plan of a service asks only for what it needs. A listing declares none.

```json
"upstream_access_config": {
  "plus": {
    "base_url": "https://relay.example.com/{{ params.folder }}",
    "api_key": "${ secrets.RELAY_API_KEY }",
    "params": {
      "schema": {
        "type": "object",
        "properties": {
          "folder": { "type": "string", "title": "Folder", "default": "inbox" }
        },
        "required": ["folder"]
      },
      "ui_schema": { "folder": { "ui:help": "Messages are filed here" } },
      "testing_defaults": { "folder": "ops" }
    }
  }
}
```

### The `params` object

| Key | Type | Description |
| --- | --- | --- |
| `schema` | object, **required** | A [JSON Schema](https://json-schema.org/) of the parameters, rendered as the customer's enrollment form ([react-jsonschema-form](https://rjsf-team.github.io/react-jsonschema-form/)). A property's own `default` pre-fills the form. |
| `ui_schema` | object | Form hints (an rjsf `uiSchema`): `ui:widget`, `ui:placeholder`, `ui:help`, `ui:order`, … |
| `testing_defaults` | object | The values the platform tests the channel with. Every required parameter needs one. |

No other key is accepted in `params`. `testing_defaults` is what the platform's test enrollment uses for gateway tests and what `usvc seller specs run-tests` renders the channel's `{{ params.X }}` with locally; `specs validate` also renders `${ customer_secrets.{{ params.X }} }` with it, so the result must be a valid secret name. A `testing_defaults.api_key` must be a secret reference.

The channel's templates read a parameter as `{{ params.NAME }}` (see [Templates in channel values](#templates-in-channel-values)). A customer reaches their enrollment at `/e/<CODE>` on the API gateway; the listing never declares that address (see [Canonical user access interfaces](#canonical-user-access-interfaces)).

### Rules

`usvc seller specs validate` checks these on every offering, and backend ingest runs the same checks when you upload:

1. **A channel that reads `{{ params.* }}` must declare `params`.** Otherwise: `upstream_access_config.<channel> reads enrollment parameters but declares no params; each channel declares the parameters it uses`.
2. **A channel reads only the parameters it declares** (in `params.schema.properties` or `required`). Another channel's `params` does not count.
3. **Every required parameter has a value in `params.testing_defaults`.** A property's schema `default` pre-fills the customer's form but does not satisfy this rule.
4. **Every required parameter is read**, by its own channel or by document content (a document's inline content, or a `.j2` document's template source). Another channel's use does not count, and neither do metadata fields such as `display_name` or `description`, which are never rendered with `params`. Dynamic access (`params[name]` with a variable, iterating `params`) counts as reading every parameter. A deprecated listing or offering is exempt, so it can still be retired.

Each channel that declares a required parameter also makes the service need an enrollment: the customer fills in the form, and the platform gives the enrollment its `/e/<CODE>` address.

### Migrating to unitysvc-core 0.3.0

`unitysvc-core` 0.3.0 refuses the listing-level parameter fields and the retired channel keys. Update specs before moving to a unitysvc-sellers release that requires it.

**Parameters move from the listing to the channel that reads them:**

| Before (listing) | After (the reading channel) |
| --- | --- |
| `user_parameters_schema` | `upstream_access_config.<channel>.params.schema` |
| `user_parameters_ui_schema` | `upstream_access_config.<channel>.params.ui_schema` |
| `service_options.ops_testing_parameters` | `upstream_access_config.<channel>.params.testing_defaults` |

Before, `listing.json`:

```json
{
  "user_parameters_schema": {
    "type": "object",
    "properties": {
      "base_url": { "type": "string", "title": "Upstream URL" },
      "api_key_secret": { "type": "string", "default": "HTTP_RELAY_API_KEY" }
    },
    "required": ["base_url", "api_key_secret"]
  },
  "user_parameters_ui_schema": { "base_url": { "ui:placeholder": "https://api.example.com" } },
  "service_options": {
    "ops_testing_parameters": {
      "base_url": "https://mock.unitysvc.dev/http",
      "api_key_secret": "HTTP_RELAY_API_KEY"
    }
  }
}
```

and `offering.json`:

```json
"upstream_access_config": {
  "plus": {
    "access_method": "http",
    "base_url": "{{ params.base_url }}",
    "api_key": "${ customer_secrets.{{ params.api_key_secret }} }",
    "is_primary": true
  }
}
```

After, the listing has none of the three, and `offering.json` holds them on the `plus` channel:

```json
"upstream_access_config": {
  "plus": {
    "base_url": "{{ params.base_url }}",
    "api_key": "${ customer_secrets.{{ params.api_key_secret }} }",
    "sort_order": 0,
    "params": {
      "schema": {
        "type": "object",
        "properties": {
          "base_url": { "type": "string", "title": "Upstream URL" },
          "api_key_secret": { "type": "string", "default": "HTTP_RELAY_API_KEY" }
        },
        "required": ["base_url", "api_key_secret"]
      },
      "ui_schema": { "base_url": { "ui:placeholder": "https://api.example.com" } },
      "testing_defaults": {
        "base_url": "https://mock.unitysvc.dev/http",
        "api_key_secret": "HTTP_RELAY_API_KEY"
      }
    }
  }
}
```

When several channels read the same parameter, each declares it. A required parameter that relied on its schema `default` for testing now also needs a `testing_defaults` value. The old fields are refused with:

- listing `user_parameters_schema`: `Enrollment parameters are declared on the listing (user_parameters_schema); declare them in the params of the channel that reads them instead (unitysvc/unitysvc#2726).`
- listing `user_parameters_ui_schema`: refused as an unknown field.
- `service_options.ops_testing_parameters`: `service_options.ops_testing_parameters is not supported: enrollment parameters are declared per channel; move the values to upstream_access_config.<channel>.params.testing_defaults (unitysvc/unitysvc#2726)`.

**Other channel keys:**

| Before | After |
| --- | --- |
| `"rate_limits": [...]` on a channel | Remove it. Declare limits on the provider (`provider.json` `rate_limits`) and name them in the channel's `rate_limit_refs`. |
| `"ops_rate_limit_refs": [...]` | Remove it (unknown key). |
| `"access_method": "http", "storage_type": "s3"` | `"access_method": "s3"`; the bucket fields stay as they are. |
| `"is_primary": true` | `"sort_order": 0` (lowest first; give the other channels higher numbers). |
| `timeout_ms`, `transport`, `response_rules` | Remove them; no gateway reads them. |
| `"raw": {...}` | Move its keys onto the channel (or server) itself. |
| `grants` / `depends_on` | Rename to `customer_access_requests`. |
| `customer_secrets_required`, `customer_secrets_optional` | Remove them; the platform derives them at upload. |
| A channel name with a space or `@` (`"OpenAI API"`) | Rename to a valid [channel name](#channel-names) (`managed`); update channel-keyed `list_price` keys to match. |

For example, an S3 channel:

```json
// Before
"s3_upstream": {
  "access_method": "http",
  "storage_type": "s3",
  "bucket": "demo",
  "region": "us-east-1",
  "access_key": "${ secrets.S3_ACCESS_KEY }",
  "secret_key": "${ secrets.S3_SECRET_KEY }"
}

// After
"s3_upstream": {
  "access_method": "s3",
  "bucket": "demo",
  "region": "us-east-1",
  "access_key": "${ secrets.S3_ACCESS_KEY }",
  "secret_key": "${ secrets.S3_SECRET_KEY }"
}
```

And an MCP channel:

```json
// Before
"unitysvc": { "access_method": "mcp", "base_url": "https://mcp.example.com/mcp", "auth_mode": "none", "timeout_ms": 30000, "transport": "streamable_http" }

// After
"unitysvc": { "access_method": "mcp", "base_url": "https://mcp.example.com/mcp", "auth_mode": "none" }
```

Listings also change: a user access interface must be a [canonical gateway address](#canonical-user-access-interfaces), so an interface that read `{{ enrollment.code }}`, `{{ params.X }}` or `{{ routing_vars.X }}` (other than the SMTP and S3 exceptions), or pointed at an external URL, must be removed or rewritten.

### Resources

- [react-jsonschema-form Documentation](https://rjsf-team.github.io/react-jsonschema-form/)
- [JSON Schema Specification](https://json-schema.org/)

## Secrets: seller-owned vs customer-owned

API keys never appear as literal values in a spec — they're **secret
references**, and the **namespace declares who owns the secret**:

| Reference | Owner | Stored in | Used for |
|-----------|-------|-----------|----------|
| `${ secrets.NAME }` | **Seller** | the seller's secret store | Managed services (seller pays the upstream) |
| `${ customer_secrets.NAME }` | **Customer** | the customer's secret store | BYOK (customer brings their own key) |
| `${ customer_secrets.{{ params.X }} }` | **Customer** | the customer's secret store | BYOE (key name given per enrollment as parameter `X`) |

A reference is valid in any channel or server string, typically
`upstream_access_config.<channel>.api_key` (the upstream call), but also
`params.testing_defaults` and `request_transformer` values. The
**namespace**, not the location, is what determines ownership.

## BYOK Services (Bring Your Own Key)

A BYOK service calls the upstream with the **customer's own key**. You reference
it from the offering's `upstream_access_config` using the `customer_secrets`
namespace:

```json
// specs/cohere/command-r/offering.json
{
    "name": "command-r",
    "service_type": "llm",
    "summary": "Cohere's Command R conversational model, via your own API key.",
    "upstream_access_config": {
        "byok": {
            "base_url": "https://api.cohere.com/v2",
            "api_key": "${ customer_secrets.COHERE_API_KEY }",
            "routing_key": { "model": "command-r" }
        }
    }
}
```

That's it: no enrollment parameter for the key. The
`${ customer_secrets.COHERE_API_KEY }` reference **is** the declaration: the
platform auto-detects that the customer must store a secret named
`COHERE_API_KEY`, shows a "Bring your own key" badge, resolves the secret from
the customer's store at routing time, and returns a clear error if it's missing.
Because the customer just stores a secret (no enrollment record), a BYOK service
needs **no enrollment** unless a channel *also* declares required
[enrollment parameters](#enrollment-parameters).

A **Managed** service is identical except it uses the seller's own key —
`"api_key": "${ secrets.COHERE_API_KEY }"` — so the seller, not the customer,
provides the credential.

### Local testing

During `usvc seller specs run-tests`, secret references (either namespace) are
resolved from **environment variables**:

```bash
export COHERE_API_KEY="…your key…"
usvc seller specs run-tests cohere/command-r
```

The test runner resolves `${ customer_secrets.COHERE_API_KEY }` (or
`${ secrets.… }`) by looking up `COHERE_API_KEY` in the shell environment — for
secrets in any location (channels, servers, `params.testing_defaults`, request
transformers).

## Data Types

Access is described by **two different objects** — a customer-facing routing
object and an upstream channel object. They were once a single shared shape;
they are now separate. In both, the name is the **dict key**, not a field.

### User access interface object

One named entry in a listing's `user_access_interfaces`. A **pure
routing-resolution object**: it says *which candidate a request addresses* and
*whether the customer may reach it* — nothing about the upstream. It carries no
credentials or transformers (those are the channel's job).

| Field           | Type    | Description                                                          |
| --------------- | ------- | ------------------------------------------------------------------- |
| `access_method` | enum    | Access method: `http` (default), `websocket`, `grpc`, `smtp`, `mcp` |
| `base_url`      | string  | Canonical gateway address (max 500 chars); see [Canonical user access interfaces](#canonical-user-access-interfaces) |
| `description`   | string  | Interface description (max 500 chars)                               |
| `routing_key`   | object  | Optional routing key for request matching                           |
| `is_active`     | boolean | Whether interface is active (default: true)                         |
| `is_primary`    | boolean | Whether this is the primary interface (default: false)             |
| `sort_order`    | integer | Display order (default: 0)                                          |

> `rate_limits`, `constraints`, and `response_rules` are **no longer accepted**
> on a user access interface (unitysvc/unitysvc#1717). `constraints` was never
> enforced and was dropped. Unlike a channel, an interface keeps `is_primary`.

### Upstream access channel object

One named entry in an offering's `upstream_access_config`. Channels are typed:
see [Upstream access channels](#upstream-access-config) for every key, the
server types, templating, and the retired keys.

#### Jinja2 Template Values

Templates are rendered in two places, differently:

- **Channels** (`upstream_access_config`): any string may be a template, rendered **per request at gateway routing time** with the enrollment's `params`, `enrollment.code` / `enrollment.id`, and the listing's `routing_vars`. See [Templates in channel values](#templates-in-channel-values). No per-enrollment record is created.
- **User access interfaces** (`user_access_interfaces`): only `{{ service_name }}`, rendered to `listing.name` when the platform stores the interface. An interface is canonical, so it never reads `params`, `routing_vars` or `enrollment` (except `{{ enrollment.code }}` as the whole SMTP username or S3 bucket segment). See [Canonical user access interfaces](#canonical-user-access-interfaces).

Every enrollment has a unique, stable **4-character code** (Crockford base32, e.g. `CEFF`), available to channel templates as `{{ enrollment.code }}`. It is also the enrollment's address: **every enrollment is reachable at `/e/<CODE>`** on the API gateway, which the platform provides. `/e/` is reserved; do not use it in `base_url`.

> **Migration:** `enrollment.code` replaces the old `enrollment_code()` function. Use `{{ enrollment.code }}` instead of `{{ enrollment_code(6) }}` (the code is always 4 characters).

**Example: a per-enrollment upstream.** The channel routes each enrollment to its own upstream topic; the customer calls `${API_GATEWAY_BASE_URL}/e/<CODE>`, and the listing declares only the canonical interface.

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

#### Routing Key

The `routing_key` field enables fine-grained request routing when multiple service listings share the same endpoint. The gateway extracts routing information from incoming requests and uses exact matching to find the correct service listing.

**How it works:**

- Gateway extracts routing key from request body (currently the `model` field: `{"model": "value"}`)
- Performs exact JSON equality match against `routing_key` in access interfaces
- Only interfaces with matching `routing_key` handle the request
- If `routing_key` is `null`, matches requests without a routing key

**Example use case:** Multiple GPT models on same endpoint:

```json
{
    "user_access_interfaces": {
        "GPT-4 API": {
            "base_url": "${API_GATEWAY_BASE_URL}/openai",
            "routing_key": { "model": "gpt-4" }
        }
    }
}
```

When a request arrives at `/openai` with `{"model": "gpt-4", "messages": [...]}`, the gateway extracts `{"model": "gpt-4"}` and routes to the matching listing.

### Pricing Object

Flexible pricing structure for both upstream (`payout_price`) and user-facing (`list_price`) prices.

> **Full documentation:** See [Pricing Specification](pricing.md) for complete details on pricing types, validation rules, and examples.

| Field         | Type         | Description                                                                      |
| ------------- | ------------ | -------------------------------------------------------------------------------- |
| `currency`    | string       | ISO currency code (e.g., "USD", "EUR")                                           |
| `price_data`  | object       | Type-specific price structure (see [Pricing Types](pricing.md#per-request-pricing-types)) |
| `description` | string       | Pricing model description                                                        |
| `reference`   | string (URL) | Reference URL to upstream pricing page                                           |

**price_data types:**

| Type                 | Description                                       | Example Fields              |
| -------------------- | ------------------------------------------------- | --------------------------- |
| `one_million_tokens` | Per million tokens (for LLMs)                     | `price` or `input`/`output` |
| `one_second`         | Per second of usage                               | `price`                     |
| `image`              | Per image generated                               | `price`                     |
| `step`               | Per step/iteration                                | `price`                     |
| `revenue_share`      | Percentage of customer charge (payout_price only) | `percentage`                |

**Quick examples:**

```json
// Unified token pricing
{"price_data": {"type": "one_million_tokens", "price": "2.50"}}

// Separate input/output pricing (LLM)
{"price_data": {"type": "one_million_tokens", "input": "10.00", "output": "30.00"}}

// Image generation pricing
{"price_data": {"type": "image", "price": "0.04"}}
```

> **Note:** Use string values for prices (e.g., `"2.50"`) to avoid floating-point precision issues.

See [Pricing Specification](pricing.md) for TOML examples, validation rules, and cost calculation details.

### DocumentData Object

Documents associated with entities (providers, offerings, listings). The document title is the dict key, not a field in the object.

| Field          | Type    | Description                                                                                               |
| -------------- | ------- | --------------------------------------------------------------------------------------------------------- |
| `mime_type`    | enum    | MIME type: `markdown`, `python`, `javascript`, `bash`, `html`, `text`, `pdf`, `jpeg`, `png`, `svg`, `url` |
| `category`     | enum    | Document category (see [DocumentCategory values](#documentcategory-enum-values))                          |
| `description`  | string  | Document description (max 500 chars)                                                                      |
| `version`      | string  | Document version (max 50 chars)                                                                           |
| `file_path`    | string  | Relative path to file (max 1000 chars, mutually exclusive with external_url)                              |
| `external_url` | string  | External URL (max 1000 chars, mutually exclusive with file_path)                                          |
| `meta`         | object  | Additional metadata (e.g., test results, requirements)                                                    |
| `sort_order`   | integer | Sort order within category (default: 0)                                                                   |
| `is_active`    | boolean | Whether document is active (default: true)                                                                |
| `is_public`    | boolean | Publicly accessible without auth (default: false)                                                         |

**Note:** The document title is specified as the dict key (5-255 chars), not as a field within the object.

### DocumentCategory Enum Values

- `getting_started` - Getting started guides
- `api_reference` - API reference documentation
- `tutorial` - Step-by-step tutorials
- `code_example` - Code examples (visible to users)
- `code_example_output` - Expected output from code examples
- `connectivity_test` - Connectivity and performance tests (not visible to users, `is_public: false`)
- `request_template` - Default request body for the playground (JSON, pre-fills the test request editor)
- `use_case` - Use case descriptions
- `troubleshooting` - Troubleshooting guides
- `changelog` - Version changelogs
- `best_practice` - Best practices
- `specification` - Technical specifications
- `service_level_agreement` - SLAs
- `terms_of_service` - Terms of service
- `invoice` - Invoices/receipts
- `logo` - Logo images
- `avatar` - Avatar images
- `other` - Other documents

### RateLimit Object

One ceiling your provider grants **your account**, declared in
[`provider.json`](#schema-provider_v1) under `rate_limits`.

| Field         | Type    | Description                                                                                   |
| ------------- | ------- | --------------------------------------------------------------------------------------------- |
| `name`        | string  | Seller-scoped bucket name referenced by channel `rate_limit_refs`                         |
| `limit`       | integer | Maximum allowed — in flight for `concurrent`, per window otherwise                            |
| `unit`        | enum    | What is limited: `requests`, `tokens`, `input_tokens`, `output_tokens`, `bytes`, `concurrent` |
| `window`      | enum    | Time window: `second`, `minute`, `hour`, `day`, `month`. Required for every unit **except** `concurrent`, which takes none. |
| `description` | string  | Where the number came from, e.g. the provider's published limit for your tier (max 255 chars) |

**Example** — a provider granting 10 in-flight requests, 600 requests a minute
and 60K input tokens a minute:

```json
"rate_limits": [
    { "name": "fireworks_concurrency", "limit": 10, "unit": "concurrent", "description": "engine capacity" },
    { "name": "fireworks_perminute", "limit": 600, "unit": "requests", "window": "minute" },
    { "name": "fireworks_input_tokens", "limit": 60000, "unit": "input_tokens", "window": "minute" }
]
```

#### Why `concurrent` takes no window

`concurrent` is a **gauge** — a count of requests in flight right now. A slot is
returned the moment a request finishes, so it has nothing to reset. Every other
unit is a **counter** accumulated over a window and reset when the window rolls.
Declaring a window on `concurrent`, or omitting one elsewhere, is rejected at
validation: the two are enforced by different mechanisms and a limit that mixes
them cannot be honoured as written.

#### What to put here, and what not to

Declare **what your provider actually granted the account behind your
credential** — the org, workspace or account limit from your provider dashboard.
Each limit needs a stable `name`; that name is the live gateway bucket that
channels reference. It is shared by every service and every customer routed
through a channel that references it, which is why the definition belongs to the
provider record and the reference belongs to the upstream channel.

The `name` is scoped to you as the seller, not to one provider file. If two
provider records or channels spend the same upstream quota, point them at the
same name. If two API keys have independent quota, give them different names.

Do **not** try to express a per-customer allowance. How much any one customer may
use depends on how many others are active at that moment, which you cannot know
when authoring a file. The gateway derives each customer's share from the ceiling
you declare here.

Omitting `rate_limits` means "not declared", and no limit is applied.

### ServiceConstraints Object (removed)

The `constraints` field and the `ServiceConstraints` object have been **removed**
(unitysvc/unitysvc#1717). They described a planned SLA/quota surface that was
never enforced by the gateway or backend, and were authored in no seller data.
Do not add a `constraints` block — it is now rejected on validation. If
SLA/quota enforcement is introduced later it will get a purpose-built home
(likely on the upstream channel).

## Secrets for Sensitive Information

API keys and other sensitive credentials must **never** be stored as plain text in data files. Instead, use the secrets reference format to specify credentials that will be securely retrieved at runtime.

### Creating Secrets

Before referencing secrets in your data files, you must create them in the UnitySVC platform:

1. Log in to the UnitySVC website
2. Navigate to **Seller Dashboard** → **Secrets**
3. Click **Create Secret**
4. Enter a name (e.g., `OPENAI_API_KEY`) and the secret value
5. Save the secret

Secret names must:

- Start with a letter or underscore
- Contain only letters, numbers, and underscores
- Be unique within your seller account

### Referencing Secrets in Data Files

Use the `${ secrets.VAR_NAME }` format to reference secrets. Spaces around the variable name are optional.

**Valid formats:**

```
${ secrets.OPENAI_API_KEY }
${secrets.OPENAI_API_KEY}
${ secrets.MY_PROVIDER_KEY }
```

### API Key Fields

The following fields require secrets references (plain text API keys are not allowed):

- `upstream_access_config.<channel>.api_key` and each `servers[].api_key`: API keys for upstream provider access (or one of the [dispositions](#api_key-values))
- `upstream_access_config.<channel>.params.testing_defaults.api_key`: a test value for an `api_key` parameter

A user access interface carries no credentials.

### Example Usage

**TOML:**

```toml
[upstream_access_config.managed]
base_url = "https://api.openai.com/v1"
api_key = "${ secrets.OPENAI_API_KEY }"
```

**JSON:**

```json
{
    "upstream_access_config": {
        "managed": {
            "base_url": "https://api.openai.com/v1",
            "api_key": "${ secrets.OPENAI_API_KEY }"
        }
    }
}
```

### How Secrets Work

1. **Upload**: When you upload data files, the `${ secrets.VAR_NAME }` references are validated for correct format and the secret's existence is verified by the backend
2. **Storage**: The reference string is stored as-is in the database (secrets are NOT expanded during upload)
3. **Runtime**: When the API key is actually needed, the platform retrieves the decrypted value from the secure secrets storage

This approach ensures that:

- Sensitive credentials are never exposed in version-controlled files
- Secrets can be rotated without re-uploading data files
- Access to secrets is controlled through the seller dashboard

## Validation Rules

The SDK enforces these validation rules:

1. **File role by name**: each service folder must hold `provider`, `offering`, and `listing` files (type determined by filename — no `schema` field)
2. **Required fields**: all required fields must be present
3. **Name format**: names must be URL-friendly (lowercase, hyphens, underscores, dots)
    - Provider: no slashes allowed
    - Service/Listing: slashes allowed for hierarchical names
5. **Time created**: Must be valid ISO 8601 datetime
6. **Email validation**: Email fields must be valid email addresses
7. **URL validation**: URL fields must be valid URLs
8. **File paths**: Document paths must be relative and exist
9. **Enum values**: Must use valid enum values
10. **Mutual exclusivity**: Some fields are mutually exclusive (e.g., `file_path` and `external_url` in documents)

## Format Support

Both JSON and TOML formats are supported for all schemas:

### JSON

- Uses 2-space indentation
- Keys sorted alphabetically
- Files end with single newline

### TOML

- Standard TOML syntax
- Sections use `[header]` notation
- Arrays of objects use `[[header]]` notation

The SDK preserves the original format when updating files.

## See Also

- [Service Options](#service-options) - Configure enrollment limits and backend behavior
- [Upstream access channels](#upstream-access-config) - Channels, servers, templates and retired keys
- [Enrollment Parameters](#enrollment-parameters) - Parameters a channel asks the enrolling customer for
- [Service Groups](#schema-service_group_v1) - Organize services with rule-based membership
- [Pricing Specification](pricing.md) - Complete pricing documentation
- [Author & Upload Specs](guides/author-specs.md) - File organization & upload
- [CLI Reference](cli-reference.md) - Command reference
- [Getting Started](getting-started.md) - Create your first files

---

## Schema: service_group_v1

Service group files define collections of services for organization and
promotion targeting. Groups use rule-based membership to automatically
include/exclude services based on their properties.

> **Note:** Seller-defined service groups are currently used primarily for
> promotion targeting (see [Promotions, Groups & Secrets](guides/catalog-extras.md#promotions)).
> Groups created by sellers are nested under an auto-created root group
> (`seller:{seller_name}`).

### Required Fields

| Field          | Type   | Description                                                      |
| -------------- | ------ | ---------------------------------------------------------------- |
| `name`         | string | URL-friendly slug (max 100 chars, lowercase with hyphens/colons) |
| `display_name` | string | Human-readable name (max 200 chars)                              |

### Optional Fields

| Field              | Type   | Default   | Description                                              |
| ------------------ | ------ | --------- | -------------------------------------------------------- |
| `description`      | string | `null`    | Detailed description (max 2000 chars)                    |
| `status`           | string | `"draft"` | Lifecycle status: `draft`, `active`, `private`, `archived` |
| `parent_group_name`| string | `null`    | Parent group name for hierarchy                          |
| `membership_rules` | object | `null`    | Rule-based membership (see below)                        |
| `sort_order`       | int    | `0`       | Display order within parent level                        |

### Status Values

| Status     | Description                                          |
| ---------- | ---------------------------------------------------- |
| `draft`    | Being configured, not active                         |
| `active`   | Live and visible in marketplace                      |
| `private`  | Live but hidden from marketplace (for promotions)    |
| `archived` | No longer available                                  |

### Membership Rules

Membership rules automatically include services based on their properties.
The `expression` field is a Python expression evaluated against each service.

**Available variables:**

| Variable        | Type   | Description                                 |
| --------------- | ------ | ------------------------------------------- |
| `service_id`    | string | Service UUID                                |
| `seller_id`     | string | Seller UUID                                 |
| `provider_id`   | string | Provider UUID                               |
| `seller_name`   | string | Seller name                                 |
| `provider_name` | string | Provider name (e.g., `"openai"`)            |
| `name`          | string | Service name                                |
| `display_name`  | string | Service display name                        |
| `service_type`  | string | Type: `"llm"`, `"embedding"`, `"tts"`, etc. |
| `status`        | string | Service status                              |
| `listing_type`  | string | `"regular"`, `"byok"`, `"self_hosted"`      |
| `tags`          | list   | List of tag strings                         |
| `is_featured`   | bool   | Whether service is featured                 |

**Example expressions:**

```python
# All LLM services
"service_type == 'llm'"

# Services from a specific provider
"provider_name == 'openai'"

# Multiple types
"service_type in ('llm', 'embedding', 'tts')"

# Combined conditions
"provider_name == 'fireworks' and service_type == 'llm'"

# Tag-based
"'premium' in tags"
```

### Example Files

**Basic group with membership rules:**
```json
{
    "name": "my-llm-services",
    "display_name": "My LLM Services",
    "description": "All LLM services for targeted promotions",
    "membership_rules": {
        "expression": "service_type == 'llm'"
    },
    "status": "private"
}
```

**Group targeting a specific provider:**
```json
{
    "name": "openai-models",
    "display_name": "OpenAI Models",
    "description": "All services from OpenAI",
    "membership_rules": {
        "expression": "provider_name == 'openai'"
    },
    "status": "active"
}
```

### CLI Commands

**Upload groups:**
```bash
# Upload all group files in directory
usvc seller specs upload --type groups

# Upload a specific file
usvc seller specs upload specs/groups/my-llm-services.json

# Dry run (validate without uploading)
usvc seller specs upload --type groups --dryrun
```

**Validate groups:**
```bash
usvc seller specs validate specs/groups/
```

### File Organization

Place group files in a `groups/` directory within your data directory:

```
data/
├── providers/
│   └── my-provider/
│       ├── provider.toml
│       └── services/
│           └── ...
├── promotions/
│   └── summer-sale.json
└── groups/
    ├── my-llm-services.json
    └── premium-models.json
```

### Using Groups with Promotions

Groups are referenced in promotion scope to target services:

```json
{
    "name": "LLM Discount",
    "pricing": {"type": "multiply", "factor": "0.80"},
    "scope": {
        "services": ["my-llm-services"]
    }
}
```

This applies the 20% discount to all services in the `my-llm-services` group.
As services join or leave the group (based on membership rules), the promotion
automatically applies to the current members.
