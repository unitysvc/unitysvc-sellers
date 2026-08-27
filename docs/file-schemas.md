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

- An **upstream access channel** ("channel") is one named entry in an offering's `upstream_access_config`. Each channel is a complete way for the gateway to reach the upstream: a wire protocol (`access_method`), an endpoint (`base_url`), a credential (`api_key`), and a `routing_key`. Channel entries are **free-form objects** — the platform reads them as opaque config, so protocol-specific shapes (SMTP host/port, S3 bucket/region, a `raw` passthrough block) live here too. Channel names are free-form (e.g. `"managed"`, `"byok"`, `"managed-eu"`). The gateway selects one channel per request. A channel answers *how the request is fulfilled and billed*, and is gated by **secret** availability. A channel may optionally replace its flat `base_url` / `api_key` with a list of interchangeable **`servers`** (same `channel_type`) for capacity and failover — see [Multi-server channels](service-types.md#multi-server-channels-capacity-failover) (planned).
- A **user access interface** is one named entry in a listing's `user_access_interfaces` — the downstream, customer-facing endpoint the customer connects *to* (canonical, `/g/<group>`, `/p/<pool>`, `/e/<code>`). An interface answers *how you connect, and whether you may*, and is gated by **enrollment** / group membership.

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
| `service_type`               | enum                        | Service category (see [ServiceTypeEnum values](#servicetype-enum-values))                                                                                                         |
| `summary`                    | string (max 200)            | One-line marketplace summary, shown on collapsed catalog rows and cards (unitysvc#1838)                                                                                          |
| `description`                | string                      | Long-form service description (the summary carries the teaser; no paragraph conventions)                                                                                          |
| `upstream_access_config` | dict of channel objects | How the gateway reaches the upstream, keyed by **channel name**; each entry is an **upstream access channel** (a free-form object — see [Upstream access channel object](#upstream-access-channel-object)) (see [Upstream access channels vs. user access interfaces](#upstream-access-channels-vs-user-access-interfaces)). Supports Jinja2 templates (e.g. `{{ enrollment.code }}`); expanded at gateway routing time using enrollment context. |
| `time_created`               | datetime (ISO 8601)         | Timestamp when offering was created                                                                                                                                               |

### Optional Fields

| Field          | Type                  | Description                                                   |
| -------------- | --------------------- | ------------------------------------------------------------- |
| `display_name` | string                | Human-readable service name for display (e.g., 'GPT-4 Turbo') |
| `capabilities` | array of string       | Specific features this service provides (see [Capabilities](#capabilities)) |
| `logo`         | string/URL            | Path to logo or URL (converted to document)                   |
| `tags`         | array of enum         | Service tags (e.g., `["byok"]` for bring-your-own-provider)   |
| `status`       | enum                  | Offering status: `draft` (default), `ready`, or `deprecated`  |
| `details`      | object                | Service-specific features and information                     |
| `payout_price` | [Pricing](pricing.md) | Seller pricing information (what seller charges UnitySVC)     |
| `documents`    | dict of DocumentData  | Technical specs, documentation, keyed by title                |

### ServiceType Enum Values

- `llm` - Large Language Model
- `embedding` - Text embedding generation
- `image_generation` - Image generation from prompts
- `text_to_image` - Text to image conversion
- `vision_language_model` - Image description/analysis
- `speech_to_text` - Audio transcription
- `text_to_speech` - Voice synthesis
- `video_generation` - Video generation
- `text_to_3d` - 3D model generation
- `streaming_transcription` - Real-time audio transcription
- `prerecorded_transcription` - Batch audio transcription
- `prerecorded_translation` - Batch audio translation
- `undetermined` - Type not yet determined

### Capabilities

A **capability is a concrete action with a defined input and output**: what your
service does to what the caller sends it. One service may have several.

Capabilities come from a **platform vocabulary**, not from your imagination. The
marketplace uses them to filter the catalog and to explain your service to
customers, so a capability only works if it means the same thing on every
service that declares it.

#### Keep the axes separate

This is the mistake to avoid — each of these answers a different question, and
collapsing them is what makes a catalog unsearchable:

| Field | Question it answers | Example |
|---|---|---|
| `service_type` | What *kind* of service is this? (broad category, validated enum) | `llm` |
| `capabilities` | What does it *do* to the input? (this vocabulary) | `["chat"]` |
| `input_formats` | What wire contract must the caller speak? | `openai_chat` |
| `details` | What *qualifies* the service? (attributes, free-form) | `{"vision": true}` |

Concretely: an OpenAI-dialect and an Anthropic-dialect chat service offer the
**same capability** (`chat`) and differ only in `input_formats`. And `vision`,
`tools` and `thinking` are **not capabilities** — they have no contract of their
own, they only qualify a chat call by changing what may appear in the request.
They belong in `details`.

#### The vocabulary

Each capability below links to its topic on the marketplace, which spells out
the full input/output contract customers will see.

**Passthrough** — the platform does not interpret the payload:

| Capability | Input | Output |
|---|---|---|
| [`http-relay`](https://unitysvc.com/topics/capability-http-relay) | an HTTP request of any shape | the upstream's HTTP response, unchanged |
| [`notification-relay`](https://unitysvc.com/topics/capability-notification-relay) | a request in your messaging provider's own format | the provider's response, with the message sent |
| [`smtp-relay`](https://unitysvc.com/topics/capability-smtp-relay) | an SMTP message | the same message, relayed on to an SMTP upstream |
| [`smtp-to-http`](https://unitysvc.com/topics/capability-smtp-to-http) | an SMTP message | an HTTP POST to a configured destination |
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
| [`embed`](https://unitysvc.com/topics/capability-embed) | text, or an image, to be represented as a vector | an embedding vector |
| [`rerank`](https://unitysvc.com/topics/capability-rerank) | a query and a set of candidate documents | the same documents ordered by relevance, with scores |
| [`moderate`](https://unitysvc.com/topics/capability-moderate) | text or an image to be assessed | a safety classification, by category |
| [`image-generate`](https://unitysvc.com/topics/capability-image-generate) | a text prompt | a generated image |
| [`image-edit`](https://unitysvc.com/topics/capability-image-edit) | an existing image and a text instruction | a modified image |
| [`video-generate`](https://unitysvc.com/topics/capability-video-generate) | a text prompt | a generated video |
| [`speech-transcribe`](https://unitysvc.com/topics/capability-speech-transcribe) | recorded audio | a text transcript |
| [`speech-synthesize`](https://unitysvc.com/topics/capability-speech-synthesize) | text, and a voice selection | synthesized audio |

`chat` absorbs **every** chat variant — the OpenAI and Anthropic dialects, the
Bedrock Converse and InvokeModel surfaces, provider SDKs, streaming, function
calling and vision. All produce generated text, so all are one capability. Use
it instead of `llm` or `text-generation`.

#### If nothing fits

The field still accepts any string, so an unrecognised value will validate and
display. But it buys you nothing: it has no topic, no explanation in the
catalog, and it fragments the capability filter — two spellings of the same idea
(`http_relay` and `http-relay`) become two separate filter entries that split
your services between them.

So prefer an existing capability, and **open an issue** if your service genuinely
does something this list does not cover. New capabilities are added
deliberately.

**Examples:**

| Service | `service_type` | `capabilities` |
|---------|---------------|----------------|
| OpenAI GPT-4 (vision-capable) | `llm` | `["chat"]` — vision goes in `details` |
| Deepgram Nova | `speech_to_text` | `["speech-transcribe"]` |
| An SMTP gateway that POSTs to a webhook | `notification` | `["smtp-to-http"]` |

### Example (TOML)

```toml
name = "gpt-4"
display_name = "GPT-4"
description = "Most capable GPT-4 model for complex reasoning tasks"
service_type = "llm"
capabilities = ["chat"]
status = "ready"
time_created = "2024-01-20T14:00:00Z"

# Attributes that QUALIFY the capability — vision, tool use, context size —
# belong here, not in `capabilities`.
[details]
vision = true
context_window = 128000
max_output_tokens = 4096
supports_function_calling = true
supports_vision = true

[upstream_access_config."OpenAI API"]
access_method = "http"
base_url = "https://api.openai.com/v1"

[payout_price]
currency = "USD"

[payout_price.price_data]
type = "one_million_tokens"
input = "30.00"
output = "60.00"
```

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
| `name`                      | string                | Listing identifier (defaults to filename without extension, max 255 chars)                       |
| `display_name`              | string                | Customer-facing name (max 200 chars)                                                             |
| `status`                    | enum                  | Status: `draft` (skip upload), `ready` (ready for review), `deprecated`                          |
| `service_options`           | object                | Service lifecycle and testing options, including `default_visibility` and `ops_testing_parameters` |
| `list_price`                | [Pricing](pricing.md) | Customer-facing pricing (what customer pays)                                                     |
| `documents`                 | dict of DocumentData  | SLAs, documentation, guides, keyed by title                                                      |
| `user_parameters_schema`    | object                | JSON schema defining user parameters for subscriptions (see [User Parameters](#user-parameters)) |
| `user_parameters_ui_schema` | object                | UI schema for user parameter form rendering (see [User Parameters](#user-parameters))            |
| `service_options`           | object                | Service-specific options (see [Service Options](#service-options))                               |

### Service Options

The `service_options` field configures backend behavior for service listings. All fields are optional.

| Field                    | Type   | Description                                                                    |
| ------------------------ | ------ | ------------------------------------------------------------------------------ |
| `ops_testing_parameters` | object | Default parameter values for testing (see [User Parameters](#user-parameters)) |
| `routing_vars`           | object | Seller-managed operational variables, referenced as `{{ routing_vars.X }}`     |
| `enrollment`             | object | Per-enrollment configuration — enrollment limits (see below)    |

**Enrollment configuration (`enrollment`):**

All enrollment-related options live under a single `enrollment` object:

| Key                  | Type    | Description                                                                                                                                                                                              |
| -------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `limit`              | integer | Maximum total active enrollments for this service (global)                                                                                                                                              |
| `limit_per_customer` | integer | Maximum active enrollments per customer                                                                                                                                                                 |
| `limit_per_user`     | integer | Maximum active enrollments per user (creator)                                                                                                                                                           |

> **No `enrollment_vars`.** Every enrollment automatically carries a unique code, available in any template as `{{ enrollment.code }}` (also reachable at `/e/<code>`). Reference it **directly** in `user_access_interfaces` / `upstream_access_config` — there is no per-enrollment variable to declare. The old `service_options.enrollment_vars` mechanism has been removed.

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
        "ops_testing_parameters": {
            "api_key": "${ secrets.SERVICE_API_KEY }",
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

[service_options.ops_testing_parameters]
api_key = "${ secrets.SERVICE_API_KEY }"
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

- **Automatic naming**: If `name` is omitted, uses filename (without extension)
- **Multiple listings**: Use descriptive filenames for different tiers/marketplaces
- **Example**: `listing-premium.json` → `name = "listing-premium"`

### status Values (Listing)

- `draft` - Work in progress, skipped during upload (default)
- `ready` - Ready for admin review and testing
- `deprecated` - No longer offered to new customers

### Gateway Base URL

The `base_url` field in `user_access_interfaces` uses a `${..._GATEWAY_BASE_URL}` placeholder that the platform resolves at runtime. UnitySVC provides multiple protocol-specific gateways, each with its own base URL:

| Gateway | Placeholder | Protocol | Example URL |
| ------- | ----------- | -------- | ----------- |
| API Gateway (APISIX) | `${API_GATEWAY_BASE_URL}` | HTTP/HTTPS | `https://api.unitysvc.com` |
| S3 Gateway | `${S3_GATEWAY_BASE_URL}` | S3 API | `https://s3.unitysvc.com` |
| SMTP Gateway | `${SMTP_GATEWAY_BASE_URL}` | SMTP | `smtp://smtp.unitysvc.com:587` |
| SSH Gateway | `${SSH_GATEWAY_BASE_URL}` | SSH | `ssh://ssh.unitysvc.com:22` |

Use the placeholder that matches the `access_method` of your service. Most services use the HTTP API gateway (`${API_GATEWAY_BASE_URL}`).

### Example (TOML)

```toml
# File: specs/openai/gpt-4/listing-premium.toml
# This listing automatically belongs to the gpt-4 offering in the same directory
# and the openai provider in the parent directory.
name = "listing-premium"
display_name = "GPT-4 Premium Access"
status = "ready"
time_created = "2024-01-25T16:00:00Z"

[user_access_interfaces."OpenAI API Access"]
access_method = "http"
base_url = "${API_GATEWAY_BASE_URL}/p/openai"

[user_access_interfaces."OpenAI API Access".routing_key]
model = "gpt-4"

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

## User Parameters

User parameters collect **configuration values** from customers during enrollment. These are real settings the customer chooses (model preferences, regions, feature flags) — not API keys or credentials.

> **Note**: API keys and credentials are handled separately through [Secrets](#secrets-for-sensitive-information), not through user parameters. See [BYOK Services](#byok-services-bring-your-own-key) for how to set up services that require a customer's API key.

### Overview

User parameters enable dynamic service configuration through:

1. **`user_parameters_schema`** - JSON Schema defining parameters, validation rules, and UI components
2. **`user_parameters_ui_schema`** - UI customization for form rendering
3. **`service_options.ops_testing_parameters`** - Default values for testing parameters before deployment

Services that define `user_parameters_schema` **require enrollment** — the customer must provide their configuration before using the service.

### user_parameters_schema

Defines the parameters users must provide when enrolling in a service. Uses [JSON Schema](https://json-schema.org/) format with extensions from [react-jsonschema-form](https://rjsf-team.github.io/react-jsonschema-form/).

**Common properties:**

- `type` - Data type: `"string"`, `"number"`, `"boolean"`, `"object"`, `"array"`
- `title` - Human-readable field label
- `description` - Help text shown to users
- `default` - Default value for the field
- `enum` - List of allowed values (creates dropdown)
- `required` - Array of required field names

**Example:**

```json
{
    "type": "object",
    "title": "Service Configuration",
    "properties": {
        "model": {
            "type": "string",
            "title": "Model",
            "description": "Model to use",
            "enum": ["gpt-4", "gpt-3.5-turbo"],
            "default": "gpt-4"
        },
        "temperature": {
            "type": "number",
            "title": "Temperature",
            "description": "Sampling temperature (0-2)",
            "default": 0.7,
            "minimum": 0,
            "maximum": 2
        }
    },
    "required": ["model"]
}
```

### user_parameters_ui_schema

Customizes how the form is rendered. Controls field order, visibility, widgets, and presentation.

**Common UI options:**

- `ui:widget` - Widget type: `"textarea"`, `"password"`, `"select"`, `"radio"`, `"checkbox"`
- `ui:placeholder` - Placeholder text
- `ui:help` - Additional help text
- `ui:description` - Field description text
- `ui:disabled` - Disable field
- `ui:order` - Field display order

**Example:**

```json
{
    "model": {
        "ui:widget": "select"
    },
    "temperature": {
        "ui:widget": "range"
    },
    "ui:order": ["model", "temperature"]
}
```

### service_options.ops_testing_parameters

Provides default parameter values for testing services before deployment. Required when `user_parameters_schema` defines required parameters without default values.

**Key requirements:**

1. **All required parameters must have defaults** - Each parameter in `user_parameters_schema.required` must have either a `default` in the schema OR a value in `ops_testing_parameters`
2. **Must be testable** - Values must allow the service to be tested successfully

**Example:**

```json
{
    "service_options": {
        "ops_testing_parameters": {
            "model": "gpt-4",
            "temperature": 0.7
        }
    }
}
```

### Complete Example (JSON)

A service with user-configurable parameters (model, token limits, streaming):

```json
{
    "display_name": "Custom AI Service",
    "status": "ready",
    "user_parameters_schema": {
        "type": "object",
        "title": "Service Configuration",
        "properties": {
            "model": {
                "type": "string",
                "title": "Model",
                "enum": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "default": "gpt-4"
            },
            "max_tokens": {
                "type": "integer",
                "title": "Max Tokens",
                "default": 1000,
                "minimum": 1,
                "maximum": 4096
            },
            "enable_streaming": {
                "type": "boolean",
                "title": "Enable Streaming",
                "default": false
            }
        },
        "required": ["model"]
    },
    "user_parameters_ui_schema": {
        "model": { "ui:widget": "select" },
        "max_tokens": { "ui:widget": "range" },
        "enable_streaming": { "ui:widget": "checkbox" },
        "ui:order": ["model", "max_tokens", "enable_streaming"]
    },
    "service_options": {
        "ops_testing_parameters": {
            "model": "gpt-4",
            "max_tokens": 1000,
            "enable_streaming": false
        }
    },
    "user_access_interfaces": {
        "API Access": {
            "access_method": "http",
            "base_url": "${API_GATEWAY_BASE_URL}/p/my-service"
        }
    }
}
```

### Validation Rules

The SDK validates user parameters during `usvc seller specs validate`:

1. All parameters in `user_parameters_schema.required` must have either a `default` in the schema or a value in `ops_testing_parameters`
2. If required parameters exist without defaults, `service_options.ops_testing_parameters` must be defined

```
✗ Required parameters missing default values in service_options.ops_testing_parameters: ['model']
```

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
| `${ customer_secrets.{{ param }} }` | **Customer** | the customer's secret store | BYOE (key name resolved per-enrollment) |

A reference is valid in any `api_key` field — typically
`upstream_access_config.*.api_key` (the upstream call), but also
`service_options.ops_testing_parameters` and `request_transformer` values. The
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
        "Cohere API": {
            "access_method": "http",
            "base_url": "https://api.cohere.com/v2",
            "api_key": "${ customer_secrets.COHERE_API_KEY }",
            "routing_key": { "model": "command-r" }
        }
    }
}
```

That's it — no `user_parameters_schema` for the key. The
`${ customer_secrets.COHERE_API_KEY }` reference **is** the declaration: the
platform auto-detects that the customer must store a secret named
`COHERE_API_KEY`, shows a "Bring your own key" badge, resolves the secret from
the customer's store at routing time, and returns a clear error if it's missing.
Because the customer just stores a secret (no enrollment record), a BYOK service
needs **no enrollment** unless it *also* has a `user_parameters_schema`.

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
secrets in any location (access interfaces, `ops_testing_parameters`, request
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
| `access_method` | enum    | Access method: `http` (default), `websocket`, `grpc`                |
| `base_url`      | string  | Customer-facing endpoint URL (max 500 chars)                        |
| `description`   | string  | Interface description (max 500 chars)                               |
| `routing_key`   | object  | Optional routing key for request matching                           |
| `is_active`     | boolean | Whether interface is active (default: true)                         |
| `is_primary`    | boolean | Whether this is the primary interface (default: false)             |
| `sort_order`    | integer | Display order (default: 0)                                          |

> `rate_limits`, `constraints`, and `response_rules` are **no longer accepted**
> on a user access interface (unitysvc/unitysvc#1717). `constraints` was never
> enforced and was dropped.

### Upstream access channel object

One named entry in an offering's `upstream_access_config`. **Free-form** — the
platform reads it as an opaque object, so nothing is required across channels
(an `http` channel has `base_url`; `smtp` has host/port; `s3` has bucket/region;
a `raw` channel wraps arbitrary passthrough fields). The keys the gateway
recognizes:

| Field                 | Type               | Description                                                                                               |
| --------------------- | ------------------ | --------------------------------------------------------------------------------------------------------- |
| `access_method`       | enum               | Wire protocol: `http` (default), `websocket`, `grpc`, `smtp`                                              |
| `base_url`            | string             | Upstream endpoint URL (optional — absent for `smtp`/`s3` and other non-HTTP channels)                     |
| `api_key`             | string             | Upstream credential / svcpass disposition: `${ secrets.VAR }` (see [Secrets](#secrets-for-sensitive-information)) |
| `routing_key`         | object             | Optional routing key for request matching                                                                 |
| `rate_limit_refs`    | array of string    | Seller-scoped provider-account buckets to consume whenever this channel is selected. Names must come from provider `rate_limits[].name`. |
| `ops_rate_limit_refs` | array of string   | Buckets to consume only during UnitySVC seller/ops testing when customer-secret refs are satisfied from seller secrets. |
| `request_transformer` | object             | Request transformation config (keys: `proxy_rewrite`, `body_transformer`)                                 |
| `response_rules`      | object             | Per-status-code triggers → `log` / `flag` / `notify`. See [Response rules](#response-rules).               |
| `is_active`           | boolean            | Whether the channel is active (default: true)                                                             |
| `is_primary`          | boolean            | Whether this is the primary channel (default: false)                                                     |
| `sort_order`          | integer            | Channel selection order (default: 0)                                                                      |

**Note:** The channel name is specified as the dict key, not as a field within the object.

#### Provider-account rate-limit refs

Provider-level `rate_limits` define **named seller-scoped buckets**. A channel
opts into those buckets with `rate_limit_refs`:

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
      "access_method": "http",
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
names when different API keys/accounts have independent quotas.

`ops_rate_limit_refs` is for seller testing of BYOK-shaped channels. During
UnitySVC ops tests, the synthetic ops customer may not have customer-owned
secrets, so the gateway can satisfy `${ customer_secrets.NAME }` from the
seller's secret store. In that case the request is spending seller quota during
testing, but production BYOK customers still spend their own provider quota.

```json
{
  "upstream_access_config": {
    "byok": {
      "access_method": "http",
      "base_url": "https://api.fireworks.ai/inference/v1",
      "api_key": "${ customer_secrets.FIREWORKS_API_KEY }",
      "ops_rate_limit_refs": ["fireworks_concurrency", "fireworks_perminute"]
    }
  }
}
```

Do not put normal `rate_limit_refs` on a true production BYOK channel unless the
channel should always consume seller-owned upstream quota.

#### Response rules

`response_rules` on an access interface (typically the offering's `upstream_access_config` channel) tells the gateway what to do based on the **upstream HTTP status code** of each proxied request: record it, flag it, or send a notification. It's a dict keyed by a rule id; each rule has a `priority`, a `status_code` condition, and one or more `actions`.

```json
"response_rules": {
  "on_server_error": {
    "name": "Upstream 5xx",
    "priority": 100,
    "conditions": { "status_code": { "op": "gte", "value": 500 } },
    "actions": {
      "log": true,
      "flag": true,
      "notify": {
        "title": "Upstream error",
        "message": "{{ method }} {{ path }} returned {{ status_code }}",
        "type": "error"
      }
    }
  }
}
```

**Rule fields**

| Field | Description |
| --- | --- |
| `name` | Human-readable label (shown on notifications). |
| `priority` | Integer; higher is evaluated first. Among matching `notify` rules, the **highest-priority one** is the notification that fires. |
| `enabled` | Optional boolean, default `true`. Set `false` to keep a rule without evaluating it. |
| `conditions.status_code` | `{ "op": <operator>, "value": <v> }` — the only supported condition (see below). |
| `conditions.match` | Optional, `"all"` (default) or `"any"` — how multiple conditions combine. Only `status_code` exists today, so this rarely matters. |
| `actions.log` | `true` → the request appears in the customer's request logs. |
| `actions.flag` | `true` → the request is flagged (surfaced in dashboards/alerts). |
| `actions.notify` | Object → send a notification (see below). |

**`status_code` operators:** `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `between` (`value` is `[low, high]`, inclusive), `in` / `not_in` (`value` is a list), `exists`, `not_exists`.

**`notify` action**

| Field | Description |
| --- | --- |
| `title` | Notification title. |
| `message` | Notification body. |
| `type` | Optional: `info` (default), `success`, `warning`, `error`. |
| `category` | Optional: `service` (default), `wallet`, `security`, `billing`. |
| `link` | Optional URL. |

A notify rule delivers an **in-app notification** to the requesting user and, if that customer has configured a `/b/notification` broadcast group, fans out to its targets (email, Discord, …). Repeated identical alerts for the same `(user, service, rule, status)` are de-duplicated over a short window, so a flapping upstream won't spam.

**Template variables** — `title`, `message`, and `link` support simple `{{ var }}` substitution over a fixed set:

`{{ status_code }}`, `{{ method }}`, `{{ path }}`, `{{ response_time_ms }}`, `{{ rule_id }}`, `{{ rule_name }}`.

> Only these variables, and only plain `{{ var }}` substitution — no conditionals or loops, and **no response-body fields**. Matching and templating are status-code based because at evaluation time the gateway only has a truncated/streamed view of the response body, so body-based rules were unreliable and have been removed.

**Platform defaults.** Every service already has sensible defaults that your rules are **merged over** (a rule you define under the same key replaces the default):

- **Production:** `log` + `flag` on `5xx`, on `429`, and `log` on `4xx`. No notifications by default.
- **Dev/test** (an unpublished service tested via the ops account): additionally `log` everything and `notify` on errors, for visibility while you iterate.

So you usually only add a rule when you want a **notification** on a specific status, or to change the default log/flag behavior.

#### Jinja2 Template Values

String values in `user_access_interfaces` and `upstream_access_config` can use **Jinja2 template syntax** for dynamic rendering at enrollment time. Templates are rendered with an enrollment context that includes enrollment parameters, customer ID, and enrollment ID.

> A `raw` block inside an `upstream_access_config` channel is **not** Jinja2-expanded — its contents are passed through verbatim and merged into the channel — for values carrying their own templates (e.g. request/response transformers). `${ … }` secrets inside `raw` are still resolved. See [Deferring expansion: the `raw` block](tech-notes/user-access-interface-template.md#deferring-expansion-the-raw-block).

**Template context variables:**

| Variable                 | Type   | Description                                          |
| ------------------------ | ------ | --------------------------------------------------- |
| `enrollment.code`        | string | The enrollment's unique **4-character** reference code |
| `enrollment.id`          | string | Enrollment UUID                                     |
| `enrollment.customer_id` | string | Customer UUID                                       |
| `enrollment.parameters`  | dict   | All enrollment parameters                           |

Every enrollment has a unique, stable **4-character code** (Crockford base32, e.g. `CEFF`), available as `{{ enrollment.code }}` and identical across `user_access_interfaces` and `upstream_access_config`. The same code is a built-in routing handle: **every enrollment is reachable at `/e/<code>`** regardless of its `base_url`. `/e/` is reserved — do not use it in `base_url`.

> **Migration:** `enrollment.code` replaces the old `enrollment_code()` function. Use `{{ enrollment.code }}` instead of `{{ enrollment_code(6) }}` (the length argument is gone — the code is always 4 characters).

**Behavior:**

- `user_access_interfaces`: templates are rendered at **enrollment time**, creating enrollment-scoped `AccessInterface` records
- `upstream_access_config`: templates are rendered at **gateway routing time**, using the enrollment context to resolve the upstream target per-request (no enrollment-scoped records are created)
- Interfaces without template syntax are treated as static and shared across enrollments (listing-scoped)
- On template rendering errors, the original string value is preserved

**Example — user access interface (TOML):**

```toml
[user_access_interfaces.ntfy-gateway]
access_method = "http"
base_url = "${API_GATEWAY_BASE_URL}/ntfy/{{ enrollment.code }}"
description = "Your ntfy notification endpoint"
```

**Example (JSON):**

```json
{
    "user_access_interfaces": {
        "ntfy-gateway": {
            "access_method": "http",
            "base_url": "${API_GATEWAY_BASE_URL}/ntfy/{{ enrollment.code }}",
            "description": "Your ntfy notification endpoint"
        }
    }
}
```

After enrollment, the `base_url` is rendered with the generated code (e.g., `${API_GATEWAY_BASE_URL}/ntfy/VTXBNM`), creating an enrollment-scoped access interface visible only to that enrollment.

**Example — upstream access interface with template:**

The corresponding upstream interface in the offering can reference the same `{{ enrollment.code }}` to route requests to the correct upstream target:

```json
{
    "upstream_access_config": {
        "ntfy-upstream": {
            "access_method": "http",
            "base_url": "https://ntfy.svcpass.com/{{ enrollment.code }}",
            "description": "Private ntfy instance"
        }
    }
}
```

Unlike user interfaces, upstream templates are **not** materialized at enrollment time. They are rendered at gateway routing time — the gateway identifies the enrollment from the inbound request, then expands the upstream template with the enrollment's `enrollment.code` to determine the final upstream URL.

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
            "base_url": "${API_GATEWAY_BASE_URL}/p/openai",
            "routing_key": { "model": "gpt-4" }
        }
    }
}
```

When a request arrives at `/p/openai` with `{"model": "gpt-4", "messages": [...]}`, the gateway extracts `{"model": "gpt-4"}` and routes to the matching listing.

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
| `name`        | string  | Seller-scoped bucket name referenced by channel `rate_limit_refs` / `ops_rate_limit_refs` |
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

- `upstream_access_config.<name>.api_key` - API keys for upstream provider access
- `user_access_interfaces.<name>.api_key` - API keys for user-facing interfaces
- `service_options.ops_testing_parameters.api_key` - Ops testing API key parameters

### Example Usage

**TOML:**

```toml
[upstream_access_config."OpenAI API"]
access_method = "http"
base_url = "https://api.openai.com/v1"
api_key = "${ secrets.OPENAI_API_KEY }"
```

**JSON:**

```json
{
    "upstream_access_config": {
        "OpenAI API": {
            "access_method": "http",
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

- [Service Options](#service-options) - Configure subscription limits and backend behavior
- [User Parameters](#user-parameters) - Define and collect subscription configuration
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
