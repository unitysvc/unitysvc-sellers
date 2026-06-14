# unitysvc-sellers

Python SDK and CLI for the [UnitySVC](https://unitysvc.com/) seller
API (`https://seller.unitysvc.com/v1`). This package provides:

1. **`unitysvc_sellers`** — a typed Python package (sync `Client` +
   async `AsyncClient`) that wraps the upstream REST API into
   importable, type-checked method calls.
2. **`usvc_seller`** — a CLI built on top of the SDK for day-to-day
   seller operations (catalog management, secret rotation, service
   lifecycle) without writing code.

| | Guide | Reference |
|-|-------|-----------|
| **Upstream API** | | [Swagger UI](https://seller.unitysvc.com/docs) · [ReDoc](https://seller.unitysvc.com/redoc) |
| **Python SDK** | [SDK Guide](https://unitysvc-sellers.readthedocs.io/en/latest/sdk-guide/) | [SDK Reference](https://unitysvc-sellers.readthedocs.io/en/latest/sdk-reference/) (auto-generated from docstrings) |
| **CLI** | [Quick Start](https://unitysvc-sellers.readthedocs.io/en/latest/getting-started/) | [CLI Reference](https://unitysvc-sellers.readthedocs.io/en/latest/cli-reference/) (auto-generated from `typer`) |

## What this package manages

The package is organized around the **kinds of data a seller works with**. Each
has a CLI command group and an SDK namespace.

| Domain | Where | What it is | Key actions |
|---|---|---|---|
| **specs** | local | Service data as files — `provider` + `offering` + `listing` per service, in a flat `specs/` layout | validate · format · test · **upload** |
| **params** | local / inline | Parameters that fill a platform **template** to create a service, with no files to author | browse templates · **instantiate** |
| **services** | remote | Your live and in-review services | list · show · submit · withdraw · deprecate · set-visibility · **update** |
| **groups** | remote | Service groups that bundle related services | list · show · delete |
| **promotions** | remote | Price rules that discount your services for customers | list · show · activate · pause · delete |
| **secrets** | remote | Named secret values (upstream API keys), referenced by name | list · show · set · delete |
| **templates** | remote | The platform's catalog of service templates you can instantiate | list · show |

The two **local** domains are two routes to the same destination — a service on
the platform: author full **specs** and `specs upload` them, **or** pick a
**template** and supply **params** to instantiate it. Everything else operates on
data that already lives on the platform. Both the `usvc_seller` CLI and the
Python SDK cover every domain.

→ Full docs: [Services](https://unitysvc-sellers.readthedocs.io/en/latest/services/)
(the spec model + the two routes + status lifecycle) ·
[Service Templates](https://unitysvc-sellers.readthedocs.io/en/latest/service-templates/)
(platform templates, capability pools, your own populators) ·
[File Schemas](https://unitysvc-sellers.readthedocs.io/en/latest/file-schemas/)
(every field and option).

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

# List services — iterate the page directly (the result is a ServiceList).
for svc in client.services.list(limit=50, status="active"):
    print(svc.id, svc.name, svc.status)

# Fetch one — `svc` is a Service active-record bound to its id.
svc = client.services.get(service_id)
print(svc.name, svc.status)

# Mutate via the bound handle (no need to re-pass the id).
svc.update({"status": "pending"})
svc.submit()  # shortcut for {"status": "pending"}

# Promotions — upsert returns a Promotion bound to its id.
promo = client.promotions.upsert({
    "name": "summer-2026",
    "scope": {"customers": "*"},
    "pricing": {"type": "multiply", "factor": "0.80"},
    "status": "active",
})
promo.update({"status": "paused"})

# Service groups — same pattern.
grp = client.groups.upsert({"name": "premium", "service_ids": [...]})
grp.update({"display_name": "Premium tier"})

# Push an entire catalog directory.
result = client.upload("./my-catalog", dryrun=False)
print(f"services: {result.services.success}/{result.services.total}")
```

### Configuration

| Source     | Default                                   | Override                                                    |
|------------|-------------------------------------------|-------------------------------------------------------------|
| API key    | (required)                                | `Client(api_key=...)` / `UNITYSVC_SELLER_API_KEY`           |
| Base URL   | `https://seller.unitysvc.com/v1`          | `Client(base_url=...)` / `UNITYSVC_SELLER_API_URL`          |
| Timeout    | 30 s                                      | `Client(timeout=...)`                                       |

The seller context is encoded entirely in the API key (`svcpass_...`),
so no separate `seller_id` argument is required.

**Env var naming:** env vars are namespaced to the seller role
(`UNITYSVC_SELLER_API_KEY`, `UNITYSVC_SELLER_API_URL`) so a single
host can run both the seller SDK and the future customer SDK side by
side without collision — each picks up its own credentials.

**URL layout:** the SDK's generated paths are semantic resource paths
(`/services/{id}`, `/documents/{id}`, `/promotions`, `/service-groups`)
with no `/seller` wrapper. The seller scope is carried by the
subdomain + API key. The same generated SDK works against any
deployment layout without regeneration:

```python
# Default: production seller subdomain
Client()  # reads UNITYSVC_SELLER_API_URL or defaults to
          # https://seller.unitysvc.com/v1

# Staging
Client(base_url="https://seller.staging.unitysvc.com/v1")

# Local development against a running backend
Client(base_url="http://localhost:8000/v1/seller")
```

### Secrets

Manage encrypted seller secrets (API keys, tokens, credentials).
Values are **write-only** — only metadata is ever returned. The API
mirrors GitHub's secrets API: `set(name, value)` is idempotent and
covers both create and rotate.

```python
# List all secrets (metadata only)
secrets = client.secrets.list()
for s in secrets.data:
    print(s.name, s.created_at)

# Get one secret's metadata by name
meta = client.secrets.get("OPENAI_API_KEY")

# Create or rotate (idempotent)
client.secrets.set("OPENAI_API_KEY", "sk-...")

# Delete a secret (immediate effect on running services)
client.secrets.delete("OPENAI_API_KEY")
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `secrets.list(skip=0, limit=100)` | `skip`, `limit` | `SecretsPublic` | List secrets (metadata only) |
| `secrets.get(name)` | `name: str` | `SecretPublic` | Get one secret's metadata |
| `secrets.set(name, value)` | `name: str`, `value: str` | `SecretPublic` | Idempotent create-or-replace |
| `secrets.delete(name)` | `name: str` | `None` | Permanently delete a secret |

Secret names must be uppercase with underscores (e.g. `OPENAI_API_KEY`,
`STRIPE_SECRET`). Names starting with `__` are reserved for platform use.

### Pagination

`services.list`, `promotions.list`, and `groups.list` use
**cursor-based pagination**. Each call returns an iterable list
wrapper (`ServiceList`, `PromotionList`, `GroupList`) that exposes
`data`, `next_cursor`, `has_more`, and `next_page()`:

```python
# Single page — iterate the wrapper directly
page = client.services.list(limit=50)
for svc in page:
    print(svc.name)

# Manual pagination via next_page()
while page.has_more:
    page = page.next_page()
    for svc in page:
        ...

# Or let the SDK walk every page for you
for svc in client.services.iter_all(status="active"):
    print(svc.name)
```

The CLI list commands accept `--cursor` and `--all` (to auto-follow
cursors and render the combined result).

### Async client

The same API surface is exposed as `AsyncClient` for use in asyncio
contexts (FastAPI, Starlette, Trio-via-anyio, scripts using
`asyncio.run`). Sync iteration walks the current page; for full
iteration use `iter_all()`:

```python
import asyncio
from unitysvc_sellers import AsyncClient

async def main():
    async with AsyncClient(api_key="svcpass_...") as client:
        # One page at a time.
        services = await client.services.list(limit=50)
        for svc in services:
            print(svc.id, svc.name)

        # Or every page, automatically:
        async for svc in client.services.iter_all(status="active"):
            print(svc.id, svc.name)

        # Active-record mutations work the same way.
        promo = await client.promotions.get(promo_id)
        await promo.update({"status": "active"})

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

- `usvc_seller specs ...` — **local** operations on a `specs/` repo (no network)
- `usvc_seller services|params|templates|promotions|groups|secrets ...` —
  **remote** operations against the seller backend, all using the SDK's
  `AsyncClient` under the hood

### Local commands (`specs`)

```
usvc_seller specs validate [SPECS_DIR]           # schema + catalog-layout validation
usvc_seller specs format   [SPECS_DIR]           # normalize JSON/TOML/MD files
usvc_seller specs populate [SPECS_DIR]           # run the repo's populator (templates/config.json)
usvc_seller specs show     SERVICE_NAME          # expanded data for one service
usvc_seller specs list     services|providers|offerings|listings|sellers [SPECS_DIR]
usvc_seller specs list-tests [NAME]              # list local code-example / connectivity tests
usvc_seller specs run-tests  [NAME]              # run them locally
usvc_seller specs show-test  SERVICE             # show last local test result
usvc_seller specs upload     [NAME]              # upload services + promotions + groups
        [--api-key svcpass_...]                  #   defaults to $UNITYSVC_SELLER_API_KEY
        [--base-url https://...]                 #   defaults to $UNITYSVC_SELLER_API_URL or staging
        [--type services|promotions|groups]      #   restrict to one resource kind
```

`NAME` is a `service_name` (= `listing.name`) — a literal or an fnmatch pattern
(`'cohere/*'`); omit it to act on the whole repo.

### Remote commands (require `$UNITYSVC_SELLER_API_KEY` or `--api-key`)

```
# Services — NAME is a service_name (= listing.name), literal or fnmatch pattern
usvc_seller services list [NAME] [--status STATUS] [--provider NAME]
                          [--fields id,name,...] [--format table|json]
usvc_seller services show           [NAME] [--format table|json]
usvc_seller services submit         [NAME] | --all [--provider NAME] [--yes]
usvc_seller services withdraw       [NAME] | --all [--provider NAME] [--yes]
usvc_seller services deprecate      [NAME] | --all [--provider NAME] [--yes]
usvc_seller services set-visibility VISIBILITY [NAME] | --all   # public|unlisted|private
usvc_seller services delete         [NAME] | --all [--status STATUS] [--yes]
usvc_seller services update [NAME]
        [--visibility public|unlisted|private]
        [--set-routing-var key=value | '{json}']        (repeatable)
        [--remove-routing-var key]                       (repeatable)
        [--load-routing-vars path/to.json]
        [--set-price key=value | '{json}' | NUMBER]      (repeatable)
        [--remove-price-field key]                       (repeatable)

# Document tests (registered under services; NAME selects services, doc ids select docs)
usvc_seller services list-tests   [NAME] [--all] [--format table|json]
usvc_seller services show-test    [DOCUMENT_ID] [--format table|json]
usvc_seller services run-tests    [NAME] [--document-id DOC_ID] [--force]
usvc_seller services skip-test    DOCUMENT_ID
usvc_seller services unskip-test  DOCUMENT_ID

# Templates + params — create a service from a platform template
usvc_seller templates list
usvc_seller templates show NAME_OR_ID
usvc_seller params instantiate TEMPLATE [-P key=value ...] [--name NAME]
                               [--submit | --no-submit]

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

# Secrets
usvc_seller secrets list   [--format table|json]
usvc_seller secrets show   NAME [--format table|json]
usvc_seller secrets set    NAME [--value VALUE | --value-file PATH | --value-stdin]   # create or rotate
usvc_seller secrets delete NAME [--force]
```

`promotions activate` / `pause` are sugar over
`PATCH /promotions/{id}` with a `status` field — the backend
consolidated the legacy `/activate` and `/pause` routes.

The legacy `usvc services dedup` command is **not** ported because the
backing endpoint was removed; use
`services delete --all --status draft` instead.

The legacy `usvc_seller groups refresh` command is **not** ported
either. Dynamic group membership is now refreshed automatically by a
background worker whenever a group is mutated, so there's no manual
refresh step for sellers to invoke.

## Claude Code skill

This repository ships a [Claude Code](https://claude.com/claude-code)
skill at `skills/writing-unitysvc-services/SKILL.md`. Installed
into `<your-repo>/.claude/skills/` or `~/.claude/skills/`, it teaches
Claude the platform's file-organization rules, naming conventions, and
the validate → format → local-tests → gateway-tests → upload pipeline,
so Claude can author services to spec without you having to thread
every rule into the prompt each time. See [Claude Code
Skill](https://unitysvc-sellers.readthedocs.io/en/latest/claude-code-skill/)
for install + usage.

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
│   ├── groups.py        # client.groups.{list,get,upsert,update,delete}
│   ├── documents.py     # client.documents.{get,execute,update_test}
│   ├── aservices.py     # async mirror of services.py
│   ├── apromotions.py   # async mirror of promotions.py
│   ├── agroups.py       # async mirror of groups.py
│   ├── adocuments.py    # async mirror of documents.py
│   └── upload.py        # high-level upload_directory(client, path)
├── _generated/          # openapi-python-client output (do not edit by hand)
│   ├── client.py        #   AuthenticatedClient (httpx + attrs, sync + async)
│   ├── api/seller_services/       #   services_list, services_get, ...
│   ├── api/seller_promotions/     #   promotions_list, promotions_upsert, ...
│   ├── api/seller_service_groups/ #   groups_list, groups_upsert, ...
│   ├── api/seller_documents/      #   documents_get, documents_execute, ...
│   ├── models/          #   one model per schema component
│   └── ...
├── commands/            # Typer command groups for the remote CLI
│   ├── _helpers.py      #   run_async, async_client, model_list,
│   │                    #     resolve_promotion, resolve_service_id, ...
│   ├── services.py      #   `usvc_seller services {list,show,submit,...}`
│   ├── tests.py         #   `usvc_seller services {list,show,run,skip,unskip}-test`
│   ├── templates.py     #   `usvc_seller templates {list,show}`
│   ├── params.py        #   `usvc_seller params instantiate`
│   ├── promotions.py    #   `usvc_seller promotions {list,show,activate,pause,delete}`
│   ├── groups.py        #   `usvc_seller groups {list,show,delete}`
│   └── secrets.py       #   `usvc_seller secrets {list,show,set,delete}`
├── cli.py               # `usvc_seller` Typer entry point
├── data.py              # `usvc_seller specs` command group (local)
├── _cli_upload.py       # `usvc_seller specs upload` Typer wrapper
├── validator.py         # seller DataValidator (extends unitysvc_core.validator)
├── format_data.py       # `usvc_seller specs format`
├── populate.py          # `usvc_seller specs populate`
├── example.py           # `usvc_seller specs {list,run,show}-test` (local)
├── list.py              # `usvc_seller specs list *`
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
