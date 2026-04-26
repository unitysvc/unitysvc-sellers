# Usage

`unitysvc-sellers` gives you two ways to manage seller catalogs on the
UnitySVC platform:

-   **CLI** — `usvc_seller` — the primary workflow for day-to-day
    catalog authoring, validation, upload, and testing. Read the
    [Getting Started](getting-started.md) guide first, then the full
    [CLI Reference](cli-reference.md).
-   **Python SDK** — `unitysvc_sellers.Client` / `AsyncClient` — a typed
    HTTP client the CLI itself is built on. Use it when you want to
    embed catalog management into your own scripts, CI/CD jobs, or
    applications. See the [SDK Guide](sdk-guide.md).

Both front-ends talk to the same `/v1/seller/*` HTTP API, so anything
you can do from the CLI you can also do from the SDK.

## Which one should I use?

| You want to…                                              | Use        |
| --------------------------------------------------------- | ---------- |
| Author a seller catalog in local files and upload it      | CLI        |
| Run connectivity tests against your services              | CLI        |
| Inspect, promote, or deprecate services                   | CLI or SDK |
| Embed "upload seller catalog" into a build script         | SDK        |
| Bulk-generate services from an external data source       | SDK        |
| Write an application that manages promotions or groups    | SDK        |
| One-off operations where a shell command is faster        | CLI        |

## Authentication

Both the CLI and the SDK authenticate with a seller API key. Get one
from the UnitySVC dashboard → **Settings → API Keys**, then export it:

```bash
export UNITYSVC_SELLER_API_KEY="svcpass_..."
export UNITYSVC_SELLER_API_URL="https://seller.unitysvc.com/v1"
```

The seller context is encoded entirely in the key — there is no
separate `seller_id` to pass. For one-off overrides, every CLI command
accepts `--api-key` / `--base-url` flags, and both `Client` and
`AsyncClient` accept `api_key=` / `base_url=` constructor arguments.

## Minimal examples

**CLI**

```bash
usvc_seller data validate
usvc_seller data upload --dryrun
usvc_seller data upload
usvc_seller services list
```

**SDK (sync)**

```python
from unitysvc_sellers import Client

with Client() as client:
    services = client.services.list(limit=50)
    for svc in services:
        print(svc.id, svc.name, svc.status)
```

**SDK (async)**

```python
import asyncio
from unitysvc_sellers import AsyncClient

async def main():
    async with AsyncClient() as client:
        services = await client.services.list(limit=50)
        for svc in services:
            print(svc.id, svc.name, svc.status)

asyncio.run(main())
```

## Next steps

-   [Getting Started](getting-started.md) — installation, seller
    onboarding, and your first upload.
-   [Data Structure](data-structure.md) — how a seller catalog is
    organized on disk.
-   [CLI Guide](cli-guide.md) / [CLI Reference](cli-reference.md) —
    workflows and complete command listing.
-   [SDK Guide](sdk-guide.md) / [SDK Reference](sdk-reference.md) —
    usage patterns and auto-generated class docs.
-   [Workflows](workflows.md) — manual, web-assisted, and automated
    catalog-authoring patterns.
