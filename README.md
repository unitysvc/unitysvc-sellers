# unitysvc-sellers

Seller-facing tools for [UnitySVC](https://unitysvc.com/). Provides:

- A typed Python **HTTP SDK** (`unitysvc_sellers.Client`) for the
  `/v1/seller/*` API surface — services, promotions, service groups,
  documents, and end-to-end catalog upload.
- The **`usvc_seller` CLI** for organizing local seller catalogs and
  pushing them to the backend.

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

```
# Local data organization (no network)
usvc_seller data validate [DATA_DIR]            # schema + catalog-layout validation
usvc_seller data format   [DATA_DIR]            # normalize JSON/TOML/MD files
usvc_seller data populate [DATA_DIR]            # run provider populate scripts
usvc_seller data show     provider|offering|listing|service NAME
usvc_seller data list     providers|sellers|offerings|listings|services [DATA_DIR]
usvc_seller data list-tests                     # list code-example / connectivity tests
usvc_seller data run-tests                      # run tests locally
usvc_seller data show-test SERVICE              # show last test result

# HTTP — pushes to UnitySVC backend
usvc_seller data upload [DATA_DIR]              # upload services + promotions + groups
        [--api-key svcpass_...]                 #   defaults to $UNITYSVC_API_KEY
        [--base-url https://...]                #   defaults to $UNITYSVC_BASE_URL or staging
        [--type services|promotions|groups]     #   restrict to one resource kind
        [--dryrun]                              #   validate against backend without persisting
```

## Layout

```
src/unitysvc_sellers/
├── client.py            # Client facade (api_key + 4 resource namespaces)
├── exceptions.py        # SellerSDKError + status-code subclasses
├── _http.py             # internal: unwrap generated Response → typed model or APIError
├── resources/
│   ├── services.py      # client.services.{list,get,upload,set_status,...}
│   ├── promotions.py    # client.promotions.{list,get,upsert,update,delete}
│   ├── groups.py        # client.groups.{list,get,upsert,update,delete,refresh}
│   ├── documents.py     # client.documents.{get,execute,update_test}
│   └── upload.py        # high-level upload_directory(client, path)
├── _generated/          # openapi-python-client output (do not edit by hand)
│   ├── client.py        #   AuthenticatedClient (httpx + attrs)
│   ├── api/seller/      #   one module per operation (services_list, ...)
│   ├── models/          #   one model per schema component
│   └── ...
├── cli.py               # `usvc_seller` Typer entry point
├── data.py              # `usvc_seller data` command group
├── _cli_upload.py       # `usvc_seller data upload` Typer wrapper
├── validator.py         # seller DataValidator (extends unitysvc_core.validator)
├── format_data.py       # `usvc_seller data format`
├── populate.py          # `usvc_seller data populate`
├── example.py           # `usvc_seller data {list,run,show}-test`
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

- `unitysvc_sellers.AsyncClient` — async mirror of `Client`
  (the generated layer already exposes `asyncio` / `asyncio_detailed`
  for every operation, so this is a thin parallel facade).
- `unitysvc_sellers.builders` — catalog-builder helpers
  (`populate_from_iterator`, `render_template_file`, etc.) for
  `unitysvc-services-*` data repositories.
- Attachment-bytes upload — once the backend defines its replacement
  for the old `/seller/documents/upload-attachment` endpoint, the
  `client.upload(...)` orchestrator will inline binary file content
  again instead of requiring `external_url` references.

## License

MIT
