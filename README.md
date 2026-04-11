# unitysvc-sellers

Seller-facing tools for [UnitySVC](https://unitysvc.com/). Provides:

- A typed Python **HTTP SDK** with sync ([`Client`](#programmatic-usage))
  and async ([`AsyncClient`](#async-client)) facades for the
  `/v1/seller/*` API surface — services, promotions, service groups,
  documents, and end-to-end catalog upload.
- The **`usvc_seller` CLI** for organizing local seller catalogs and
  for managing remote services / promotions / service groups against
  the UnitySVC backend.

## Install

```bash
pip install unitysvc-sellers
```

This pulls in [`unitysvc-core`](https://pypi.org/project/unitysvc-core/)
for the shared data models, JSON schemas, and generic file validator;
plus `httpx`, `attrs`, `typer`, and `rich`.

## Programmatic usage

```python
from unitysvc_sellers import Client

client = Client(api_key="svcpass_...")  # or Client.from_env()

# List services
services = client.services.list(limit=50, status="active")
for s in services.data:
    print(s.name, s.id)

# Fetch full record
detail = client.services.get(service_id)

# Update service status
client.services.set_status(service_id, {"status": "ready"})

# Promotions (idempotent upsert by name)
client.promotions.upsert({
    "name": "summer-2026",
    "scope": {"customers": "*"},
    "pricing": {"type": "multiply", "factor": "0.80"},
    "status": "active",
})

# Service groups
group = client.groups.upsert({"name": "premium", "service_ids": [...]})

# Push an entire catalog directory
result = client.upload("./my-catalog", dryrun=False)
print(f"services: {result.services.success}/{result.services.total}")
```

### Configuration

| Source                 | Default                              | Override                               |
|------------------------|--------------------------------------|----------------------------------------|
| API key                | (required)                           | `Client(api_key=...)` / `UNITYSVC_API_KEY` |
| Base URL               | `https://seller.staging.unitysvc.com`| `Client(base_url=...)` / `UNITYSVC_BASE_URL` |
| Timeout                | 30 s                                 | `Client(timeout=...)`                  |

The seller context is encoded entirely in the API key (`svcpass_...`),
so no separate `seller_id` argument is required.

### Async client

The same API surface is exposed as `AsyncClient` for use in asyncio
contexts (FastAPI, Starlette, Trio-via-anyio, scripts using
`asyncio.run`):

```python
import asyncio
from unitysvc_sellers import AsyncClient

async def main():
    async with AsyncClient(api_key="svcpass_...") as client:
        services = await client.services.list(limit=50)
        for s in services.data:
            print(s.name)

        await client.promotions.update(promo_id, {"status": "active"})

asyncio.run(main())
```

Each async method has the exact same signature as its sync counterpart
on `Client`. The remote `usvc_seller services|promotions|groups`
commands all use `AsyncClient` under the hood.

### Errors

All errors are subclasses of `unitysvc_sellers.SellerSDKError`:

```python
from unitysvc_sellers import (
    SellerSDKError,
    AuthenticationError,   # 401
    PermissionError,       # 403
    NotFoundError,         # 404
    ValidationError,       # 400, 422
    ConflictError,         # 409
    RateLimitError,        # 429
    ServerError,           # 5xx
    APIError,              # base for everything above
)
```

Each carries `status_code`, `detail` (parsed body if JSON), and
`response_body` for debugging.

## CLI: `usvc_seller`

The CLI has two sets of commands:

- `usvc_seller data ...` — **local** seller catalog operations (no network)
- `usvc_seller services|promotions|groups ...` — **remote** operations
  against the seller backend, all using the SDK's `AsyncClient` under
  the hood

### Local commands

```
usvc_seller data validate [DATA_DIR]            # schema + catalog-layout validation
usvc_seller data format   [DATA_DIR]            # normalize JSON/TOML/MD files
usvc_seller data populate [DATA_DIR]            # run provider populate scripts
usvc_seller data show     provider|offering|listing|service NAME
usvc_seller data list     providers|sellers|offerings|listings|services [DATA_DIR]
usvc_seller data list-tests                     # list local code-example / connectivity tests
usvc_seller data run-tests                      # run them locally
usvc_seller data show-test SERVICE              # show last local test result
usvc_seller data upload   [DATA_DIR]            # upload services + promotions + groups
        [--api-key svcpass_...]                 #   defaults to $UNITYSVC_API_KEY
        [--base-url https://...]                #   defaults to $UNITYSVC_BASE_URL or staging
        [--type services|promotions|groups]     #   restrict to one resource kind
        [--dryrun]                              #   validate against backend without persisting
```

### Remote commands (require `$UNITYSVC_API_KEY` or `--api-key`)

```
# Services
usvc_seller services list [--status STATUS] [--name NAME] [--provider NAME]
                          [--fields id,name,...] [--format table|json]
usvc_seller services show SERVICE_ID [--format table|json]
usvc_seller services submit    SERVICE_IDS... | --all [--provider NAME] [--yes]
usvc_seller services withdraw  SERVICE_IDS... | --all [--provider NAME] [--yes]
usvc_seller services deprecate SERVICE_IDS... | --all [--provider NAME] [--yes]
usvc_seller services delete    SERVICE_IDS... | --all [--status STATUS]
                              [--provider NAME] [--dryrun] [--yes]
usvc_seller services update SERVICE_ID
        [--set-routing-var key=value | '{json}']        (repeatable)
        [--remove-routing-var key]                       (repeatable)
        [--load-routing-vars path/to.json]
        [--set-price key=value | '{json}' | NUMBER]      (repeatable)
        [--remove-price-field key]                       (repeatable)

# Document tests (registered under services for parity with the legacy CLI)
usvc_seller services list-tests   [SERVICE_ID] [--all] [--status STATUS]
                                  [--format table|json]
usvc_seller services show-test    DOCUMENT_ID [--format table|json]
usvc_seller services run-tests    SERVICE_ID [--document-id DOC_ID] [--force]
usvc_seller services skip-test    DOCUMENT_ID
usvc_seller services unskip-test  DOCUMENT_ID

# Promotions
usvc_seller promotions list   [--format table|json]
usvc_seller promotions show     NAME_OR_ID [--format table|json]
usvc_seller promotions activate NAME_OR_ID
usvc_seller promotions pause    NAME_OR_ID
usvc_seller promotions delete   NAME_OR_ID [--force]

# Service groups
usvc_seller groups list   [--status STATUS] [--format table|json]
usvc_seller groups show    NAME_OR_ID [--format table|json]
usvc_seller groups delete  NAME_OR_ID [--force]
usvc_seller groups refresh NAME_OR_ID
```

`promotions activate` / `pause` are sugar over
`PATCH /v1/seller/promotions/{id}` with a `status` field — the
seller-api-codegen-hygiene branch consolidated the legacy
`/activate` and `/pause` routes. The legacy `usvc services dedup`
command is **not** ported because the backing endpoint was removed in
the same cleanup; use `services delete --all --status draft` instead.

## Layout

```
src/unitysvc_sellers/
├── client.py            # Client (sync) facade
├── aclient.py           # AsyncClient (async) facade
├── exceptions.py        # SellerSDKError + status-code subclasses
├── _http.py             # internal: unwrap generated Response → typed model or APIError
├── resources/
│   ├── services.py      # client.services.{list,get,upload,set_status,...}
│   ├── promotions.py    # client.promotions.{list,get,upsert,update,delete}
│   ├── groups.py        # client.groups.{list,get,upsert,update,delete,refresh}
│   ├── documents.py     # client.documents.{get,execute,update_test}
│   ├── aservices.py     # async mirror of services.py
│   ├── apromotions.py   # async mirror of promotions.py
│   ├── agroups.py       # async mirror of groups.py
│   ├── adocuments.py    # async mirror of documents.py
│   └── upload.py        # high-level upload_directory(client, path)
├── _generated/          # openapi-python-client output (do not edit by hand)
│   ├── client.py        #   AuthenticatedClient (httpx + attrs, sync + async)
│   ├── api/seller/      #   one module per operation (services_list, ...)
│   ├── models/          #   one model per schema component
│   └── ...
├── commands/            # Typer command groups for the remote CLI
│   ├── _helpers.py      #   run_async, async_client, model_list,
│   │                    #     resolve_promotion, resolve_service_id, ...
│   ├── services.py      #   `usvc_seller services {list,show,submit,...}`
│   ├── tests.py         #   `usvc_seller services {list,show,run,skip,unskip}-test`
│   ├── promotions.py    #   `usvc_seller promotions {list,show,activate,pause,delete}`
│   └── groups.py        #   `usvc_seller groups {list,show,delete,refresh}`
├── cli.py               # `usvc_seller` Typer entry point
├── data.py              # `usvc_seller data` command group (local)
├── _cli_upload.py       # `usvc_seller data upload` Typer wrapper
├── validator.py         # seller DataValidator (extends unitysvc_core.validator)
├── format_data.py       # `usvc_seller data format`
├── populate.py          # `usvc_seller data populate`
├── example.py           # `usvc_seller data {list,run,show}-test` (local)
├── list.py              # `usvc_seller data list *`
├── output.py            # shared Rich output helpers
└── utils.py             # seller-only helpers + re-exports from unitysvc_core.utils
```

## Regenerating the API client

The low-level client under `src/unitysvc_sellers/_generated/` is
produced by [openapi-python-client] from a filtered copy of the backend
OpenAPI spec at `openapi.json`. To regenerate after a backend change:

```bash
# Requires a sibling checkout of unitysvc/unitysvc with backend/.venv set up
./scripts/generate_client.sh ../unitysvc
```

This script:

1. Dumps `/v1/openapi.json` from the backend's running app via
   `scripts/dump_spec.py`.
2. Filters to seller-tagged operations and sanitizes schema names that
   contain characters openapi-python-client cannot parse (e.g. strips
   the auto-generated pydantic `title` from anonymous inline object
   schemas to avoid `Pricing` / `Terms` collisions).
3. Runs `openapi-python-client generate` with the config in
   `scripts/openapi-python-client.yml`.

The hand-written facades in `unitysvc_sellers/{client,resources}.py`
should rarely change when the spec is regenerated; only the operation
modules under `_generated/api/seller/` and the models under
`_generated/models/` get refreshed.

[openapi-python-client]: https://github.com/openapi-generators/openapi-python-client

## History

This package was split out of
[`unitysvc-services`](https://github.com/unitysvc/unitysvc-services)
(see [issue #99](https://github.com/unitysvc/unitysvc-services/issues/99)).
Shared types + schemas live in
[`unitysvc-core`](https://github.com/unitysvc/unitysvc-core); seller CLI,
the catalog HTTP SDK, and seller-specific catalog utilities live here.

## Roadmap

- `unitysvc_sellers.builders` — catalog-builder helpers
  (`populate_from_iterator`, `render_template_file`, etc.) for
  `unitysvc-services-*` data repositories.
- Attachment-bytes upload — once the backend defines its replacement
  for the old `/seller/documents/upload-attachment` endpoint, the
  `client.upload(...)` orchestrator will inline binary file content
  again instead of requiring `external_url` references.

## License

MIT
