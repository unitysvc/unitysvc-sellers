# Author & Upload Specs

This guide is the hands-on companion to the [Services](../services.md) concept
page: how to lay out a `specs/` repository, validate and format it, and upload it
to the platform. (For *what* a service is made of, read Services first.)

## The `specs/` repository

A specs repo is just a folder of service folders under version control. Each
service is **self-contained** — its three parts plus an optional `service.json`:

```
specs/
└── <provider>/
    └── <service-name…>/         # may nest, e.g. acme/llama/8b
        ├── provider.json        # provider_v1 — who
        ├── offering.json        # offering_v1 — what
        ├── listing.json         # listing_v1  — how sold
        └── service.json         # backend service_id (written on first upload)
```

Two layout rules carry all the meaning:

- **Filename is the type** — a file's role comes from its name; there is no
  `schema` field inside.
- **Folder path = `listing.name`** — the folder under `specs/` is the service
  name (e.g. `acme/llama/8b`).

Promotion and service-group files (`promotion.*`, `service_group.*`) may live
anywhere in the repo — they're keyed by their `name` field, not their location.

The quickest start is the
[unitysvc-sellers-template](https://github.com/unitysvc/unitysvc-sellers-template)
or a public provider repo under [unitysvc-labs](https://github.com/unitysvc-labs).

## File formats

Both **JSON** and **TOML** are accepted for any data file. JSON is parsed with
JSON5, so comments and trailing commas are allowed while you edit:

```json
{
    // upstream model id (offering.name)
    "name": "command-r-plus",
    "display_name": "Command R+",
    "service_type": "llm",
}
```

`usvc_seller specs format` rewrites files to canonical JSON/TOML (it strips JSON
comments), giving clean, stable git diffs.

## Validate and format

Run both before uploading — they apply the same checks the platform runs on
upload, so you catch problems locally:

```bash
usvc_seller specs validate          # schema + layout checks
usvc_seller specs validate --has-service-id   # also assert every service is linked (see below)
usvc_seller specs format            # rewrite to canonical formatting
usvc_seller specs format --check    # CI-style: report drift, write nothing
```

Inspect what the repo contains, and what a service expands to:

```bash
usvc_seller specs list services     # also: providers · offerings · listings · sellers
usvc_seller specs show acme/llama/8b
```

## How upload works

```bash
usvc_seller specs upload                 # every service (+ promotions + groups) in the repo
usvc_seller specs upload 'acme/*'        # only matching service_names (fnmatch)
usvc_seller specs upload -t services     # restrict to one resource: services | promotions | groups
```

Upload is **listing-centric**. For each `listing` the uploader:

1. pairs it with the `offering` and `provider` in the **same folder**,
2. expands convenience fields (`logo`, `terms_of_service`) into documents, and
3. `POST`s the bundle to `/v1/seller/services` as one unified service.

Promotions and service groups upload via idempotent `PUT` keyed on their `name`.

## Service identity: `service.json`

The platform assigns a stable **`service_id`** the first time a folder is
uploaded, and the SDK writes it back to that folder's `service.json`:

```json
{ "service_id": "550e8400-e29b-41d4-a716-446655440000", "name": "acme/llama/8b" }
```

- **First upload** → a new service is created, `service.json` is written.
- **Later uploads** → the SDK reads `service.json` and updates *that* service in
  place (active services update through a [draft revision](operate-services.md)).
- **Commit `service.json`** so your whole team and CI target the same service.
- **Delete it** to upload the folder as a brand-new service (a copy, or a fresh
  environment).

Verify everything is linked before a release:

```bash
usvc_seller specs validate --has-service-id
```

### Multiple environments

There's one `service.json` per folder, so keep staging and production identities
apart with either **separate branches** (each carrying its own `service.json`) or
**separate specs repos/dirs** (`specs-staging/`, `specs-prod/`).

## Sharing documents across services

Documents and code examples are referenced by **relative `file_path`** from the
listing, so one file can serve many services:

```
specs/acme/
├── docs/code-example.py        # shared
├── llama-8b/listing.json       # file_path: "../docs/code-example.py"
└── llama-70b/listing.json      # file_path: "../docs/code-example.py"
```

See [Document Services](../documenting-services.md) for the document model and
[Test Services](../code-examples.md) for runnable code examples.

## Next steps

- [Generate a Catalog](generate-catalog.md) — produce many services from a source list
- [Operate Live Services](operate-services.md) — submit, set visibility, update
- [File Schemas](../file-schemas.md) — every field of `provider` / `offering` / `listing`
