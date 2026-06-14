# Quick Start

This guide takes you from an empty machine to a published service in a few
minutes. For the bigger picture of what the package manages, see the
[Overview](index.md); for the service model, see [Services](services.md).

## 1. Install

Requires **Python 3.11+**.

```bash
pip install unitysvc-sellers      # or: uv pip install unitysvc-sellers
usvc_seller --version
```

The CLI is `usvc_seller` (a shorter alias for `unitysvc_sellers`). All examples
use `usvc_seller`.

## 2. Create a seller account & API key

Uploading needs a **seller role** on the platform:

1. Sign up at [unitysvc.com](https://unitysvc.com).
2. **Add a role → Become a seller** and wait for approval.
3. Generate a **seller API key** (Settings → API Keys). Your seller identity is
   encoded in the key — the platform associates everything you upload with it.

## 3. Authenticate

Both the CLI and the SDK read the same two environment variables:

```bash
export UNITYSVC_SELLER_API_KEY="svcpass_…"                  # your seller key
export UNITYSVC_SELLER_API_URL="https://seller.unitysvc.com/v1"   # default; override for staging
```

## CLI or SDK?

Everything here works from either front-end (they share one HTTP API). Reach for
the **CLI** for day-to-day, file-based authoring; reach for the **[SDK](sdk-guide.md)**
to embed catalog operations in your own scripts, applications, or CI/CD.

| You want to… | Use |
|---|---|
| Author a catalog in local files and upload it | CLI |
| Run connectivity tests against your services | CLI |
| Inspect, promote, or deprecate services | either |
| Embed "upload catalog" into a build script | SDK |
| Bulk-generate services from an external source | SDK |

## 4. Publish your first service

There are two routes to a published service — pick the one that fits. (Both are
explained in depth under [Services → Two ways to create a service](services.md#two-ways-to-create-a-service).)

### Route A — author specs and upload

Create a minimal `specs/` repo. Each service is a self-contained folder holding
its three parts; the folder path under `specs/` is the service name.

```
specs/
└── my-provider/
    └── my-service/
        ├── provider.json    # who provides it
        ├── offering.json    # what it is (upstream endpoint, type, details)
        └── listing.json     # how it's sold (name, docs, price)
```

The fastest way to a correct skeleton is to start from the
[unitysvc-sellers-template](https://github.com/unitysvc/unitysvc-sellers-template)
or copy an existing public provider repo under the
[unitysvc-labs org](https://github.com/unitysvc-labs). Fill in the fields by hand
([File Schemas](file-schemas.md)), export them from the dashboard, or have an AI
assistant draft them (see the [Claude Code Skill](claude-code-skill.md)).

Then validate, test, and upload:

```bash
usvc_seller specs validate          # schema + layout checks
usvc_seller specs format            # canonical formatting (cleaner git diffs)
usvc_seller specs run-tests         # run code-example / connectivity tests vs your upstream
usvc_seller specs upload            # upload every service in the repo
```

`run-tests` may need upstream credentials in the environment (e.g.
`export GROQ_API_KEY=…`). On the **first** upload of a folder a new service is
created and its id is written to `service.json` — commit that file so later
uploads update the same service.

### Route B — instantiate a platform template

If the platform publishes a template for your service type, you author **no
files** — you supply parameters and it renders the service for you:

```bash
usvc_seller templates list                          # what's available
usvc_seller templates show openai-compatible-llm    # its parameters
usvc_seller params instantiate openai-compatible-llm \
    -P api_base_url=https://api.example.com/v1 \
    -P api_key_secret_name=UPSTREAM_API_KEY \
    -P input_price=1.00
```

Secret-typed parameters take a **secret name** (create it first with
`usvc_seller secrets set …`), never the raw value. See
[Service Templates](service-templates.md) for platform templates, capability
pools, and authoring your own.

## 5. Submit for review

Uploaded/instantiated services start as drafts. Confirm and submit:

```bash
usvc_seller services list                   # find your service by name
usvc_seller services submit my-provider/my-service
```

Services are targeted by **`service_name`** (= `listing.name`, e.g.
`my-provider/my-service`); a pattern like `'my-provider/*'` targets a whole
provider. After review and approval the service goes live; set it public with
`usvc_seller services set-visibility`. What happens next — marketplace listing,
billing, payouts — is covered in [After You Publish](seller-lifecycle.md).

!!! tip "Iterate until approved"
    Typical cycle: edit → `specs validate` → `specs run-tests` → `specs upload`
    → `services run-tests` → `services submit`. Fix and repeat from the relevant
    step if anything fails.

## Next steps

- [Services](services.md) — the service model, the two routes, the status lifecycle
- [Author & Upload Specs](guides/author-specs.md) — the `specs/` repo in depth
- [Operate Live Services](guides/operate-services.md) — status, visibility, updates
- [CLI Reference](cli-reference.md) — every command and option

## Troubleshooting

**Validation errors** — run `usvc_seller specs validate`; check that each service
folder has all three files and that the folder path matches `listing.name`.

**Upload errors** — verify `UNITYSVC_SELLER_API_KEY` / `UNITYSVC_SELLER_API_URL`
are set; confirm you're in (or pointing at) the `specs/` repo.

**Format drift in CI** — run `usvc_seller specs format` locally (it rewrites
files); `specs format --check` reports what would change without writing.
