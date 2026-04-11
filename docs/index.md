# UnitySVC Seller SDK Documentation

Welcome to the UnitySVC Seller SDK documentation. The
`unitysvc-sellers` package gives digital service providers two
complementary ways to manage their catalog on the UnitySVC platform:

-   The **`usvc_seller` CLI** — a local-first, version-controlled
    workflow for authoring, validating, uploading, and testing
    seller catalogs from the command line.
-   The **Python SDK** (`unitysvc_sellers.Client` / `AsyncClient`) — a
    typed HTTP client that powers the CLI and can be embedded in
    your own scripts, CI/CD jobs, or applications.

Both talk to the same `/v1/seller/*` HTTP API, so you can mix and
match freely.

## Quick Links

-   **[Getting Started](getting-started.md)** - Installation and first steps
-   **[Data Structure](data-structure.md)** - Understanding the Service Data model
-   **[CLI Reference](cli-reference.md)** - Complete command-line interface guide
-   **[SDK Reference](sdk-reference.md)** - Python `Client` / `AsyncClient`, resources, and examples
-   **[Workflows](workflows.md)** - Common usage patterns and best practices

## What the package gives you

-   **Define** service offerings and listings using schema-validated files
-   **Manage** service data locally in version-controlled repositories
-   **Validate** data against JSON schemas before uploading
-   **Upload** services to the UnitySVC platform (CLI or SDK)
-   **Manage Lifecycle** - Submit services for review, deprecate, or withdraw
-   **Automate** — embed catalog operations into your own scripts via
    the typed Python SDK

## Types of Services

The UnitySVC platform can route a wide variety of digital services, such as AI/ML APIs, email delivery, file/media content, compute environments, database access, monitoring, and scheduled tasks — across HTTP, S3, SMTP, and SSH protocols. See [Service Types](service-types.md) for full specification and examples.

| Type | Description | Enrollment? | Examples |
|------|-------------|:-----------:|---------|
| **Managed** | Seller provides upstream credentials | No | LLM inference (OpenAI, Anthropic), embedding APIs, image generation, translation |
| **BYOK** (Bring Your Own Key) | Customer provides their own API key for a cloud provider | No | Groq, Together AI, Fireworks with customer's own account |
| **BYOE** (Bring Your Own Endpoint) | Customer provides the URL of their self-hosted instance | Yes | Self-hosted Ollama/vLLM, on-premise inference, private deployments |
| **With User Parameters** | Customer provides configuration during enrollment; combinable with any type above | Yes | Model preferences, region selection, custom labels |
| **Recurrent** | Scheduled execution at configured intervals; combinable with any type above | Yes | Uptime monitoring, daily ETL sync, weekly report generation |

Services can be **stateless** (each request independent — most inference APIs) or **stateful** (maintaining history across requests — e.g., recommendation models, conversation context, analytics). In all cases, **no customer credentials or identity are passed to the upstream provider** — the gateway authenticates the customer separately and forwards only the request payload and upstream credentials.

UnitySVC handles **enrollment**, **service delivery via the API gateway**, and **billing** so that service providers can focus entirely on building and operating their digital services. Sellers do not need to build authentication, payment processing, usage metering, or customer management — the platform provides all of this. Sellers define their service endpoints, pricing, and parameters; UnitySVC takes care of routing requests, tracking usage, generating invoices, and processing payouts.

UnitySVC supports flexible seller business models, including **metered payouts** (sellers earn based on actual usage), **proportional payouts** (a percentage of what customers pay), **promotions** (reducing customer pricing via price rules), and **seller-funded incentives** (sellers pay the platform to offer free or discounted access for service testing and customer acquisition).

## The Service Data Model

Sellers provide services through UnitySVC by uploading service specifications using this SDK. A service specification consists of three complementary data components that work together:

| Component | Schema | Purpose | Reusability |
|-----------|--------|---------|-------------|
| **Provider Data** | `provider_v1` | WHO provides the service | One per provider, shared by all offerings |
| **Offering Data** | `offering_v1` | WHAT is being provided | One per service, can have multiple listings |
| **Listing Data** | `listing_v1` | HOW it's sold to customers | One per pricing tier/marketplace |

These three parts are **organized separately** in the file system for reusability, but are **uploaded together** as a unified service to the UnitySVC platform.

### Why This Structure?

-   **Provider Data** contains identity, contact info, and terms of service - defined once and reused
-   **Offering Data** defines the service itself, API endpoints, and upstream pricing
-   **Listing Data** defines customer-facing presentation, documentation, and pricing

This enables scenarios like:
- One provider with multiple service offerings
- One offering with multiple listings (e.g., basic/premium tiers)
- Shared documentation across services

## Key Features

-   **Unified Upload** — Provider, offering, and listing uploaded together atomically
-   **Service Lifecycle** — Submit for review, deprecate, or withdraw services
-   **Typed SDK** — `Client` / `AsyncClient` with fully typed request/response models generated from the seller OpenAPI spec
-   **Data Validation** — Comprehensive schema validation before upload
-   **Local-First CLI** — Work offline, commit to git, upload when ready
-   **Automation** — Script-based service generation and CI/CD integration
-   **Multiple Formats** — Support for JSON and TOML catalog files
-   **Smart Routing** — Request routing based on routing keys (e.g., model-specific endpoints)

## Documentation Overview

### For New Users

1. [**Getting Started**](getting-started.md) - Install the package, create your first service, and upload it
2. [**Data Structure**](data-structure.md) - Learn about the Service Data model and file organization
3. [**Workflows**](workflows.md) - Manual, web-assisted, and automated catalog-authoring patterns

### For Reference

-   [**CLI Reference**](cli-reference.md) - All `usvc_seller` commands and options
-   [**SDK Reference**](sdk-reference.md) - `Client`, `AsyncClient`, resource namespaces, and end-to-end examples
-   [**File Schemas**](file-schemas.md) - Detailed schema specifications for provider / offering / listing files

## Community & Support

-   **GitHub**: [unitysvc/unitysvc-sellers](https://github.com/unitysvc/unitysvc-sellers)
-   **Issues**: [Report bugs or request features](https://github.com/unitysvc/unitysvc-sellers/issues)
-   **PyPI**: [unitysvc-sellers](https://pypi.org/project/unitysvc-sellers/)

## License

This project is licensed under the MIT License.
