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

- An **upstream access channel** ("channel") is one named entry in an offering's `upstream_access_config`. Each channel is a complete way for the gateway to reach the upstream: a wire protocol (`access_method`), an endpoint (`base_url`), a credential (`api_key`), a `routing_key`, and quality/restrictions (`rate_limits`). Channel names are free-form (e.g. `"managed"`, `"byok"`, `"managed-eu"`). The gateway selects one channel per request. A channel answers *how the request is fulfilled and billed*, and is gated by **secret** availability.
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

### services_populator Object

Configuration for automatically populating service data, declared in **`templates/config.json`** (not in `provider.json`) and run by `usvc_seller specs populate`.

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
| `upstream_access_config` | dict of AccessInterfaceData | How the gateway reaches the upstream, keyed by **channel name**; each entry is an **upstream access channel** (see [Upstream access channels vs. user access interfaces](#upstream-access-channels-vs-user-access-interfaces)). Supports Jinja2 templates (e.g. `{{ enrollment.code }}`); expanded at gateway routing time using enrollment context. |
| `time_created`               | datetime (ISO 8601)         | Timestamp when offering was created                                                                                                                                               |

### Optional Fields

| Field          | Type                  | Description                                                   |
| -------------- | --------------------- | ------------------------------------------------------------- |
| `display_name` | string                | Human-readable service name for display (e.g., 'GPT-4 Turbo') |
| `description`  | string                | Service description                                           |
| `capabilities` | array of string       | Specific features this service provides (see [Capabilities](#capabilities)) |
| `logo`         | string/URL            | Path to logo or URL (converted to document)                   |
| `tagline`      | string                | Short elevator pitch                                          |
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

The `capabilities` field lists the specific features a service provides. While `service_type` is a single broad category used for UI grouping, `capabilities` is an array that enables discovery and filtering across multiple features.

- `service_type` answers: **"What kind of service is this?"** (e.g., `llm`)
- `capabilities` answers: **"What can this service do?"** (e.g., `["llm", "vision_language_model"]`)

Capabilities are free-form strings. Well-known values include all `ServiceTypeEnum` values above, plus:
`recommendation`, `search`, `classification`, `summarization`, `translation`, `code_generation`, `function_calling`, `fine_tuning`

**Examples:**

| Service | `service_type` | `capabilities` |
|---------|---------------|----------------|
| OpenAI GPT-4 | `llm` | `["llm", "vision_language_model"]` |
| Deepgram Nova | `speech_to_text` | `["speech_to_text", "text_to_speech"]` |
| Gorse Recommender | `undetermined` | `["recommendation"]` |

### Example (TOML)

```toml
name = "gpt-4"
display_name = "GPT-4"
description = "Most capable GPT-4 model for complex reasoning tasks"
service_type = "llm"
capabilities = ["llm", "vision_language_model"]
status = "ready"
time_created = "2024-01-20T14:00:00Z"

[details]
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
| `user_access_interfaces` | dict of AccessInterfaceData | How users access the service, keyed by name |
| `time_created`           | datetime (ISO 8601)         | Timestamp when listing was created          |

### Optional Fields

| Field                       | Type                  | Description                                                                                      |
| --------------------------- | --------------------- | ------------------------------------------------------------------------------------------------ |
| `name`                      | string                | Listing identifier (defaults to filename without extension, max 255 chars)                       |
| `display_name`              | string                | Customer-facing name (max 200 chars)                                                             |
| `status`                    | enum                  | Status: `draft` (skip upload), `ready` (ready for review), `deprecated`                          |
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
| `enrollment`             | object | Per-enrollment configuration — code scope and enrollment limits (see below)    |

**Enrollment configuration (`enrollment`):**

All enrollment-related options live under a single `enrollment` object:

| Key                  | Type    | Description                                                                                                                                                                                              |
| -------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scope`              | string  | Enrollment-code scope: `"customer"` (default) or `"global"`. With `"global"`, each enrollment gets a longer, globally-unique code — use it when the code lands in a **shared upstream namespace** (e.g. a notification topic), where a per-customer-only code could collide across customers. |
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
        "ops_testing_parameters": {
            "api_key": "${ secrets.SERVICE_API_KEY }",
            "region": "us-east-1"
        },
        "enrollment": {
            "scope": "global",
            "limit": 100,
            "limit_per_customer": 5,
            "limit_per_user": 2
        }
    }
}
```

**Example (TOML):**

```toml
[service_options.ops_testing_parameters]
api_key = "${ secrets.SERVICE_API_KEY }"
region = "us-east-1"

[service_options.enrollment]
scope = "global"
limit = 100
limit_per_customer = 5
limit_per_user = 2
```

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

The SDK validates user parameters during `usvc_seller specs validate`:

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

During `usvc_seller specs run-tests`, secret references (either namespace) are
resolved from **environment variables**:

```bash
export COHERE_API_KEY="…your key…"
usvc_seller specs run-tests cohere/command-r
```

The test runner resolves `${ customer_secrets.COHERE_API_KEY }` (or
`${ secrets.… }`) by looking up `COHERE_API_KEY` in the shell environment — for
secrets in any location (access interfaces, `ops_testing_parameters`, request
transformers).

## Data Types

### AccessInterfaceData Object

The `AccessInterfaceData` object defines how to access a service (used in offerings and listings). The interface name is the dict key, not a field in the object.

| Field                 | Type               | Description                                                                                               |
| --------------------- | ------------------ | --------------------------------------------------------------------------------------------------------- |
| `access_method`       | enum               | Access method: `http` (default), `websocket`, `grpc`                                                      |
| `base_url`            | string             | API endpoint URL (max 500 chars)                                                                          |
| `api_key`             | string             | API key using secrets format: `${ secrets.VAR_NAME }` (see [Secrets](#secrets-for-sensitive-information)) |
| `description`         | string             | Interface description (max 500 chars)                                                                     |
| `request_transformer` | object             | Request transformation config (keys: `proxy_rewrite`, `body_transformer`)                                 |
| `routing_key`         | object             | Optional routing key for request matching                                                                 |
| `rate_limits`         | array of RateLimit | Rate limiting rules                                                                                       |
| `constraints`         | ServiceConstraints | Service constraints                                                                                       |
| `is_active`           | boolean            | Whether interface is active (default: true)                                                               |
| `is_primary`          | boolean            | Whether this is primary interface (default: false)                                                        |
| `sort_order`          | integer            | Display order (default: 0)                                                                                |

**Note:** The interface name is specified as the dict key, not as a field within the object.

#### Jinja2 Template Values

String values in `user_access_interfaces` and `upstream_access_config` can use **Jinja2 template syntax** for dynamic rendering at enrollment time. Templates are rendered with an enrollment context that includes enrollment parameters, customer ID, and enrollment ID.

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

Rate limiting rules for services.

| Field         | Type    | Description                                                                                   |
| ------------- | ------- | --------------------------------------------------------------------------------------------- |
| `limit`       | integer | Maximum allowed in time window                                                                |
| `unit`        | enum    | What is limited: `requests`, `tokens`, `input_tokens`, `output_tokens`, `bytes`, `concurrent` |
| `window`      | enum    | Time window: `second`, `minute`, `hour`, `day`, `month`                                       |
| `description` | string  | Human-readable description (max 255 chars)                                                    |
| `burst_limit` | integer | Short-term burst allowance                                                                    |
| `is_active`   | boolean | Whether limit is active (default: true)                                                       |

**Example:**

```json
{
    "limit": 10000,
    "unit": "requests",
    "window": "hour",
    "description": "10K requests per hour limit",
    "burst_limit": 1000
}
```

### ServiceConstraints Object

Comprehensive service constraints and policies. All fields are optional.

**Usage Quotas:**

- `monthly_quota`, `daily_quota` - Usage quotas
- `quota_unit` - Unit for quotas (RateLimitUnitEnum)
- `quota_reset_cycle` - Reset cycle: `daily`, `weekly`, `monthly`, `yearly`
- `overage_policy` - Policy when exceeded: `block`, `throttle`, `charge`, `queue`

**Authentication:**

- `auth_methods` - Supported auth methods (array of AuthMethodEnum)
- `ip_whitelist_required` - IP whitelisting required (boolean)
- `tls_version_min` - Minimum TLS version (string)

**Request/Response:**

- `max_request_size_bytes`, `max_response_size_bytes` - Size limits
- `timeout_seconds` - Request timeout
- `max_batch_size` - Max batch items

**Content:**

- `content_filters` - Content filtering: `adult`, `violence`, `hate_speech`, `profanity`, `pii`
- `input_languages`, `output_languages` - Supported languages (ISO 639-1)
- `max_context_length` - Max context tokens
- `region_restrictions` - Geographic restrictions (ISO country codes)

**Availability:**

- `uptime_sla_percent` - Uptime SLA (e.g., 99.9)
- `response_time_sla_ms` - Response time SLA
- `maintenance_windows` - Scheduled maintenance

**Concurrency:**

- `max_concurrent_requests` - Max concurrent requests
- `connection_timeout_seconds` - Connection timeout
- `max_connections_per_ip` - Max connections per IP

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
usvc_seller specs upload --type groups

# Upload a specific file
usvc_seller specs upload specs/groups/my-llm-services.json

# Dry run (validate without uploading)
usvc_seller specs upload --type groups --dryrun
```

**Validate groups:**
```bash
usvc_seller specs validate specs/groups/
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
