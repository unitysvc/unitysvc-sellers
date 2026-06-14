# UnitySVC Seller SDK

`unitysvc-sellers` is the toolkit digital-service providers use to manage their
presence on the **UnitySVC platform** — from authoring a service on your laptop
to operating it live in production. It talks to the seller API so you don't have
to: you describe *what* you offer and *how* it's sold, and the platform handles
enrollment, gateway routing, usage metering, billing, and payouts.

## What the package manages

The package is organized around the **kinds of data a seller works with**. Each
kind has its own command group and SDK namespace.

| Data type | Where it lives | What it is | Typical actions |
|---|---|---|---|
| **specs** | local repo | Your **service data** as files — `provider` + `offering` + `listing` per service, in a flat `specs/` layout | create, validate, format, test, **upload** |
| **params** | local / inline | **Parameters that fill in a platform template** to produce a service, with no files to author | browse templates, **instantiate** (render + create) |
| **services** | remote | Your **live and in-review services** on the platform | list, show, submit, withdraw, deprecate, set visibility, **update** (patch routing / price) |
| **groups** | remote | **Service groups** that bundle related services | list, show, delete |
| **promotions** | remote | **Price rules** that discount your services for customers | list, show, activate, pause, delete |
| **secrets** | remote | Named **secret values** (upstream API keys) referenced by specs and params | list, show, set, delete |
| **templates** | remote | The platform's **catalog of service templates** you can instantiate | list, show |

The two **local** kinds — `specs` and `params` — are two routes to the same
destination: *a service on the platform*. Author full spec files and
[`specs upload`](services.md#path-a-author-specs-and-upload) them, **or** pick a
platform template and supply [`params`](services.md#path-b-instantiate-a-template-with-params)
to instantiate it. Everything else (`services`, `groups`, `promotions`,
`secrets`, `templates`) operates on data that already lives on the platform.

→ See **[Services](services.md)** for what a service spec consists of, the two
upload routes, and how a service moves through its status lifecycle.

## One package, two front-ends: CLI and SDK

Every data type and action above is available through **both** front-ends, which
talk to the same `/v1/seller/*` HTTP API — mix and match freely:

-   **`usvc_seller` CLI** — a local-first, version-controlled workflow for
    authoring, validating, uploading, testing, and operating your catalog from
    the command line. *Local* commands live under `usvc_seller specs …`; *remote*
    commands under `usvc_seller services | params | groups | promotions | secrets | templates …`.
-   **Python SDK** — `unitysvc_sellers.Client` / `AsyncClient`, a typed HTTP
    client (the CLI is built on it) for embedding catalog operations in your own
    scripts, CI/CD jobs, or applications.

```bash
# CLI: validate local specs, then upload them
usvc_seller specs validate
usvc_seller specs upload

# CLI: or create a service from a platform template, no files needed
usvc_seller params instantiate openai-compatible-llm \
    -P api_base_url=https://api.example.com/v1 -P input_price=1.00
```

```python
# SDK: the same operations, embeddable in your own code
from unitysvc_sellers import Client

with Client() as client:
    services = client.services.list()
    client.instances.create("openai-compatible-llm",
                            parameters={"api_base_url": "https://api.example.com/v1"})
```

## What you can do

**Author & publish services**

-   Define services as schema-validated `specs/` files, version-controlled in git
-   Validate and format locally before anything leaves your machine
-   Run upstream connectivity / code-example tests against your endpoints
-   Upload authored specs, or instantiate a platform template with parameters
-   Generate a whole catalog of services from a source list with a populator

**Operate live services**

-   Move services through review: submit, withdraw, deprecate
-   Control marketplace visibility (public / unlisted)
-   Update a live service's routing variables and list price
-   Run server-side diagnostics and manage which documents are tested

**Manage the surrounding catalog**

-   Discount services for customers with promotions (price rules)
-   Bundle related services into service groups
-   Store upstream credentials as named secrets, referenced by name (never by value)
-   Browse the platform template catalog before instantiating

**Automate everything**

-   Drive all of the above from the typed Python SDK in scripts and CI/CD

## Where to go next

-   **[Installation & Quick Start](getting-started.md)** — install the package and publish your first service
-   **[Services](services.md)** — service specs, the two upload routes, and the status lifecycle
-   **[Service Templates](service-templates.md)** — platform templates, capability pools, and your own populators
-   **[CLI Reference](cli-reference.md)** — the complete command listing
-   **[SDK Guide](sdk-guide.md)** / **[SDK Reference](sdk-reference.md)** — usage patterns and generated class docs
-   **[Service Types](service-types.md)** — Managed, BYOK, BYOE, recurrent, and parameterized services
-   **[Seller Lifecycle](seller-lifecycle.md)** — what happens after upload: review, billing, payouts
-   **[Claude Code Skill](claude-code-skill.md)** — let Claude author services to platform conventions automatically

## Authentication

Both front-ends authenticate with a seller API key from the UnitySVC dashboard
(**Settings → API Keys**). The seller context is encoded entirely in the key:

```bash
export UNITYSVC_SELLER_API_KEY="svcpass_..."
export UNITYSVC_SELLER_API_URL="https://seller.unitysvc.com/v1"
```

## Community & Support

-   **GitHub**: [unitysvc/unitysvc-sellers](https://github.com/unitysvc/unitysvc-sellers)
-   **Issues**: [Report bugs or request features](https://github.com/unitysvc/unitysvc-sellers/issues)
-   **PyPI**: [unitysvc-sellers](https://pypi.org/project/unitysvc-sellers/)

Licensed under the MIT License.
