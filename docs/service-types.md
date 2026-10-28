# Service Types

UnitySVC is a multi-protocol service marketplace. Sellers list services, and the platform handles discovery, authentication, routing, metering, and billing. This guide covers what types of services the platform supports and how they are delivered.

## Service Categories

The platform supports services across multiple protocols and use cases:

| Category | Protocol | Gateway | Examples |
|----------|----------|---------|----------|
| **AI / ML** | HTTP | API Gateway | Chat APIs, embeddings, image generation, transcription, translation |
| **Email delivery** | SMTP | SMTP Gateway | Transactional email, bulk email, email verification |
| **Content / media** | HTTP or S3 | API Gateway or S3 Gateway | Stock media, datasets, video courses, software distribution |
| **Compute environments** | SSH / WireGuard | SSH Gateway | GPU instances, licensed software, dev environments |
| **Database access** | SSH tunnel | SSH Gateway | Managed Postgres, Redis, Elasticsearch |
| **Monitoring** | HTTP (platform-triggered) | API Gateway | Uptime checks, SSL monitoring, DNS monitoring |
| **Scheduled tasks** | HTTP (platform-triggered) | API Gateway | Cron-as-a-service, data collection, report generation |
| **Webhook relay** | HTTP | API Gateway | Webhook buffering, retry, fan-out, transformation |
| **Notifications** | HTTP | API Gateway | Push notifications, alerting |

### AI and machine learning

Language models, embeddings, image generators, speech-to-text, and more. Customers access them through a unified HTTP API with the same API key. The platform supports intelligent routing across providers and automatic failover.

**Service types**: `llm`, `embedding`, `rerank`, `image_generation`, `speech_to_text`, `text_to_speech`, `video_generation`, `text_to_image`, `vision_language_model`, `streaming_transcription`, `prerecorded_transcription`, `prerecorded_translation`, `text_to_3d`

### Email delivery

Sellers wrap SMTP providers (SendGrid, Mailgun, SES) as marketplace services. Customers point their app's SMTP settings at `smtp.unitysvc.com` and send. The seller's SMTP credentials are hidden — customers authenticate with their UnitySVC API key.

**Service types**: `smtp_relay`

### Content and media

Sellers host files on S3, GCS, R2, or other storage. Customers browse and download through the S3 gateway (`s3.unitysvc.com`) using standard S3 tools (boto3, aws-cli, rclone). The platform meters downloads and hides the seller's storage credentials.

For video/audio streaming (HLS, DASH), the HTTP API gateway serves manifest files and media segments — standard HTTP, no special infrastructure needed.

**Service types**: `content_delivery`, `video_streaming`, `audio_streaming`, `data_feed`

### Compute environments

Sellers offer on-demand computing environments (GPU instances, licensed software, analysis tools). Customers enroll, connect via SSH tunnel or WireGuard VPN, use the environment, and disconnect. Time-based billing charges only for active usage.

**Service types**: `compute`

### Monitoring and scheduled tasks

The platform triggers actions on a schedule on behalf of customers. Sellers provide the checking/action logic; the platform handles scheduling, alerting, and billing. Uses the existing RecurrentRequest infrastructure.

**Service types**: `uptime_monitoring`, `ssl_monitoring`, `dns_monitoring`, `cron`, `webhook_relay`

## Service Delivery Patterns

Orthogonal to the service category, each service uses one of these delivery patterns. The pattern determines **who provides upstream credentials** and **whether enrollment is required**.

| Pattern | Who pays provider? | Enrollment? | Customer action |
|---------|-------------------|-------------|-----------------|
| **Managed** | Seller | No | None — use immediately |
| **Managed + parameters** | Seller | Yes | Enroll and configure |
| **BYOK** | Customer | No | Store API key as a secret |
| **BYOE** | Customer (self-hosted) | Yes | Enroll with endpoint URL |
| **Recurrent** | Any of the above | Yes | Enroll and configure schedule |
| **Subscription** | Seller | Yes | Enroll; platform charges daily/hourly via heartbeat |

Each delivery pattern corresponds to an **upstream access channel** in the offering's `upstream_access_config` — a complete way for the gateway to reach the upstream. The channel's `channel_type` (`managed` / `byok` / `byoe`) is *derived* from its credential and endpoint, not hand-labelled. A single offering can expose more than one channel — see [Multi-channel services](#multi-channel-services).

### Managed services

A **managed channel** uses the seller's key (`${ secrets.* }`), so the seller provides upstream credentials. All customers share the same upstream endpoint. No enrollment required.

```json
// specs/openai/gpt-4/offering.json — seller's upstream credentials
{
    "upstream_access_config": {
        "managed": {
            "base_url": "https://api.openai.com/v1",
            "api_key": "${ secrets.OPENAI_API_KEY }",
            "rate_limit_refs": ["openai_perminute", "openai_concurrency"]
        }
    }
}
```

```json
// specs/openai/gpt-4/listing.json — customer-facing gateway path
{
    "user_access_interfaces": {
        "canonical": {
            "access_method": "http",
            "base_url": "${API_GATEWAY_BASE_URL}/{{ service_name }}"
        }
    }
}
```

Request flow: `Customer → API key → Gateway → seller's upstream creds → Provider`

Managed channels usually spend quota from your provider account. Define the
quota once in `provider.json` under named `rate_limits`, then reference those
names from seller-owned channels with `rate_limit_refs`. See
[Provider-account rate-limit refs](file-schemas.md#provider-account-rate-limit-refs).

### BYOK (Bring Your Own Key)

A **BYOK channel** uses the customer's key (`${ customer_secrets.* }`), so the customer provides their own upstream API key. No enrollment required — the key lives in the customer's secret store. A BYOK channel references it with the **`customer_secrets`** namespace in `upstream_access_config`:

```json
// specs/groq/llama-3.3-70b/offering.json
{
    "upstream_access_config": {
        "byok": {
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": "${ customer_secrets.GROQ_API_KEY }",
            "routing_key": { "model": "llama-3.3-70b-versatile" }
        }
    }
}
```

The **namespace** of the reference — not its location — declares who owns the secret:

| Reference | Owner | Resolved from |
|-----------|-------|---------------|
| `${ secrets.NAME }` | Seller | Seller's secret store |
| `${ customer_secrets.NAME }` | Customer (BYOK) | Customer's secret store |

A `${ customer_secrets.X }` reference is also its own declaration — the platform auto-detects the customer-required secret by scanning for it; no enrollment parameter is needed. See [File Schemas](file-schemas.md) for the full BYOK model.

True production BYOK traffic spends the customer's provider quota, not yours, so
do not add `rate_limit_refs` to a BYOK channel. (`ops_rate_limit_refs` is not a
channel key; it is refused.)

### BYOE (Bring Your Own Endpoint)

A **BYOE channel** uses the customer's key *and* a customer-templated `base_url`, so the customer provides the URL of their own service instance (e.g., self-hosted Ollama). Enrollment required. The channel declares the [enrollment parameters](file-schemas.md#enrollment-parameters) it reads, and the key name is supplied per enrollment via Jinja indirection inside the `customer_secrets` namespace:

```json
// specs/ollama/byoe/offering.json — templates resolve from enrollment parameters
{
    "upstream_access_config": {
        "byoe": {
            "base_url": "{{ params.base_url }}",
            "api_key": "${ customer_secrets.{{ params.api_key_secret }} }",
            "params": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "base_url": { "type": "string", "title": "Your Ollama URL" },
                        "api_key_secret": { "type": "string", "title": "Secret holding your API key" }
                    },
                    "required": ["base_url", "api_key_secret"]
                },
                "testing_defaults": {
                    "base_url": "https://mock.unitysvc.dev/ollama",
                    "api_key_secret": "OLLAMA_API_KEY"
                }
            }
        }
    }
}
```

Two-phase resolution:
1. **Jinja rendering** (enrollment parameters): `{{ params.base_url }}` → `http://my-server:11434`, `{{ params.api_key_secret }}` → `MY_KEY`
2. **Secret resolution**: `${ customer_secrets.MY_KEY }` → the actual key value from the customer's secret store

### Multi-channel services

A single offering isn't limited to one channel. `upstream_access_config` can hold several **upstream access channels** at once — for example a `managed` channel and a `byok` channel reaching the same upstream — and the gateway picks one per request (by `routing_key` match, or forced with `_channel=<name>`). Each channel can carry its own price via a channel-keyed `list_price`, so the same model can be billed per-token on the seller's key and free on the customer's. See [Channel-based Pricing](pricing.md#channel-based-pricing-channel) for the `upstream_access_config` + `list_price` shape.

### Multi-server channels (capacity & failover)

!!! note "Planned — schema reserved, not yet served"
    The `servers` shape below is reserved and may be authored now, but the gateway does not yet
    distribute or fail over across servers — today a channel uses its own top-level fields.
    Tracked in [unitysvc/unitysvc#1299](https://github.com/unitysvc/unitysvc/issues/1299).

Use multiple **channels** (above) when customers should *choose* between options (managed vs. BYOK).
Use multiple **servers** when *you* are scaling or hardening **one** option. A single channel can be
backed by several interchangeable **servers** — extra endpoints and/or keys for the *same*
`channel_type` — to spread load, survive an upstream outage or rate limit, and migrate endpoints
without downtime. Replace the channel's flat `base_url` / `api_key` with a `servers` list:

```json
{
    "upstream_access_config": {
        "managed": {
            "access_method": "http",
            "routing_key": { "model": "deepseek-v4-pro" },
            "servers": [
                { "base_url": "https://api.deepseek.com",       "api_key": "${ secrets.KEY_A }", "weight": 3 },
                { "base_url": "https://api-backup.deepseek.com", "api_key": "${ secrets.KEY_B }", "weight": 1 }
            ]
        }
    }
}
```

How the gateway resolves a channel:

1. **`servers` present** — pick one server by `weight`, lift its fields onto the channel, then route as usual.
2. **No `servers`** — use the channel's own top-level fields (the single-server case is unchanged).

Server entries are typed by the channel's `access_method` (an `http` server has `base_url` / `api_key`;
an `smtp` server has `host` / `port`; see [Servers](file-schemas.md#servers)), exactly the fields you'd
otherwise place at the channel level, plus optional `name`, `weight` and `acceptable_formats`. When a
channel has both, each server inherits the channel-level connection fields it does not set itself.

- **Capacity** — `weight` spreads steady-state load proportionally (`weight: 3` takes ~3× the traffic
  of `weight: 1`; omitted weights are equal).
- **Failover** — if the chosen server returns a retriable upstream failure (`429`, `502/503/504`,
  connection/timeout) *before any response is sent*, the gateway spills to another server in the same
  channel and retries, up to a bounded number of attempts. A client error (`4xx`) is never retried,
  and once a response has started streaming it cannot fail over.
- **Zero-downtime transition** — add the new server, set the old one's `weight: 0` to drain it (it
  stays a failover target but takes no new traffic), then remove it once traffic has moved.

All servers in a channel must be the **same `channel_type`** — failover never crosses provenance, so a
`byok` server is never swapped for a `managed` one (which would change whose key and bill applies).
Because the servers are interchangeable, the channel keeps **one** name, **one** `channel_type`, and
**one** price: multi-server is invisible to the customer and to
[channel pricing](pricing.md#channel-based-pricing-channel).

### Recurrent services

The platform triggers requests on a schedule. Recurrence is orthogonal to delivery pattern — any service type can be recurrent.

```toml
[service_options]
prompt_recurrence = true
recurrence_min_interval_seconds = 300    # minimum 5 minutes
recurrence_max_interval_seconds = 86400  # maximum 1 day
recurrence_allow_cron = true
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `prompt_recurrence` | bool | `false` | Prompt for recurrence parameters during enrollment |
| `recurrence_min_interval_seconds` | int | `60` | Minimum interval |
| `recurrence_max_interval_seconds` | int | `604800` | Maximum interval (7 days) |
| `recurrence_allow_cron` | bool | `true` | Allow cron expressions |

### Subscription (time-based billing)

For services where customers pay for duration (compute, content libraries), the platform creates a daily/hourly heartbeat request via RecurrentRequest. Charges accrue while enrolled; cancellation stops charges. No new billing model — uses existing `constant` pricing + scheduled requests.

### Per-enrollment code in URLs

When the *upstream* URL needs a per-enrollment value (e.g. a unique topic code), reference the
intrinsic `{{ enrollment.code }}` **directly** in the channel — every enrollment has a unique code,
so no per-enrollment variable needs to be declared:

```toml
[upstream_access_config.plus]
base_url = "https://ntfy.svcpass.com/{{ enrollment.code }}"
```

`{{ enrollment.code }}` renders to the enrollment's unique code (e.g. `CEFF`) at routing time.
The customer reaches the enrollment at `${API_GATEWAY_BASE_URL}/e/CEFF`, an address the platform
provides. A user access interface stays canonical: it never reads `{{ enrollment.code }}`, except
as the whole SMTP `routing_key.username` or S3 bucket segment (see
[Canonical user access interfaces](file-schemas.md#canonical-user-access-interfaces)).


See [file-schemas.md](file-schemas.md#jinja2-template-values) for the full templating model, and
[service-templates.md](service-templates.md) for instantiating these patterns from a template.

## Comparison Table

| Aspect | Managed | BYOK | BYOE | Recurrent | Subscription |
|--------|---------|------|------|-----------|-------------|
| **api_key reference** | `${ secrets.X }` (seller) | `${ customer_secrets.X }` (customer) | `${ customer_secrets.{{ params.X }} }` | Same as base | Same as base |
| **upstream base_url** | Static URL | Static URL | `{{ params.base_url }}` | Same as base | Same as base |
| **Enrollment?** | No | No | Yes | Yes | Yes |
| **Customer provides** | Nothing | API key | Endpoint URL | Schedule | Nothing |
| **Pricing** | Per-request/token | Per-request/token | Per-request/token | Per-request/token | Time-based (daily/hourly) |

## What Requires Enrollment?

| Condition | Why |
|-----------|-----|
| A channel declares required `params` | Customer must provide configuration |
| An `upstream_access_config` template references `{{ enrollment.* }}` or `{{ params.* }}` | Per-enrollment upstream templating |
| `service_options.enrollment.required` is `true` | Declared explicitly (e.g. MCP services) |
| `prompt_recurrence` is true | Per-enrollment schedule |
| Subscription pricing | Heartbeat linked to enrollment lifecycle |

Conditions that do **not** require enrollment:

| Condition | Why |
|-----------|-----|
| BYOK (`${ customer_secrets.X }`) | Resolved from the customer's secret store at routing time |
| Seller secrets (`${ secrets.X }`) | Seller-level, resolved at routing time |
| Shared access interfaces | Same URL for all customers |

## Service Groups

Services can be organized into [service groups](services.md) for unified routing. A customer sends a request to a group path (e.g., `/g/llm/v1/chat/completions`), and the platform routes to the best available service using weighted selection.

Groups can contain a mix of delivery patterns:

- **Managed services** — always available
- **BYOK services** — skipped if the customer hasn't stored the required secret
- **BYOE services** — skipped if the customer hasn't enrolled

This enables fallback patterns: route to the customer's BYOK key first, fall back to a seller-managed service if the key is missing.

## Capability Pools

A **PlatformService** (`/p/<capability>`) is a platform-managed service for a *commodity* capability — a model and contract fixed by the platform, offered by many providers at a **single, uniform price**. A customer sends a request to the platform-service path (e.g., `/p/llama3-2-1b/v1/chat/completions`) and the gateway load-balances across all verified providers of that capability. Because price and terms are identical across members, every provider is fungible, so the route can optimize for **performance** (latency / quality / health) rather than cost.

You don't author a platform-service member by hand. Membership comes **only** from creating a private service from the linked [system template](service-templates.md) — `usvc seller specs upload` of a hand-written spec always produces a plain standalone service, never a platform-service member. Opting in is deliberately simple: create a system-template param file and run `usvc seller specs upload`.

Pool membership is **opt-in and non-exclusive** — if you want to offer the same capability at your own price, publish it as a separate standalone service; joining a pool doesn't stop you.
