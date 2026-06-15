# Compact Specs with Param Files

When several services share one shape but differ in a few values, you don't have
to copy `offering.json` + `listing.json` for each. Author **one local template**
and a tiny **param file** per service — `{ template, parameters }` — and the SDK
renders the full specs **in memory** at validate / test / upload time. Nothing
generated is written to git; the committed source of truth is the template plus
the small param files.

This sits between the two other local authoring shapes:

| If you have… | Use | Why |
|---|---|---|
| a handful of bespoke services | spelled-out folders → [Author & Upload Specs](author-specs.md) | full control, nothing shared |
| **several services that share one shape**, authored by hand | **param files (this guide)** | one template, one tiny file each, no generated specs in git |
| **many** services from a source list (an API, a spreadsheet) | a populator → [Generate a Catalog](generate-catalog.md) | a script *materializes* spec folders, kept in sync on re-run |

Param files and spelled-out folders can live side by side under `specs/` — the
`specs` commands handle a mix. Requires `unitysvc-sellers` ≥ 0.2.4.

> **Local template, not a platform one.** This is your *own* template, rendered
> on your machine — distinct from [Create from a Template](create-from-template.md),
> where the **platform** owns the template and renders it server-side
> (`params instantiate`). A param file whose `template` names a directory under
> your `templates/` is local; a name with no matching directory is treated as a
> remote platform template. See [Routing](#local-vs-remote-templates) below.

## Repo layout

```
templates/resp/                 # a local template directory
├── provider.json               # static provider definition
├── offering.json.j2            # {{ status }} {{ label }} {{ blurb }}
├── listing.json.j2             # references connectivity.sh.j2 by relative path
└── connectivity.sh.j2          # extra file, bundled into the rendered service
specs/unitysvc/                 # one param file per service
├── resp200.json                # { template, parameters }
├── resp200.service.json        # identity sidecar (service_id) — written on upload, committed
├── resp400.json   resp404.json   resp429.json   resp500.json   resp503.json
└── …
```

Everything lives under `specs/` — there is no separate `params/` directory. A
service at `<provider>/<name>` is defined by exactly one of a spec **folder**
(`specs/<provider>/<name>/`) or a param **file** (`specs/<provider>/<name>.json`);
a folder and a file at the same path is an error.

## The param file

Two keys: an optional `template` and a `parameters` object.

```jsonc
// specs/unitysvc/resp200.json — named template (templates/resp/)
{
  "template": "resp",
  "parameters": {
    "status": 200,
    "label": "OK",
    "blurb": "success sink — close the request loop with a 200 and no upstream"
  }
}

// single default template (templates/) — omit the template key
{ "parameters": { "status": 200, "label": "OK", "blurb": "…" } }
```

- **`template`** is a **bare name resolved under `templates/`** (no path prefix),
  and is **optional** — omit it for the single default template `templates/`, set
  `"resp"` for `templates/resp/`.
- **`parameters`** holds the values, nested (not spread at the top level) so a
  value may safely be named `template` / `name` / etc.
- **No `name` field** — the service name comes from the **path**
  (`specs/unitysvc/resp200.json` → `unitysvc/resp200`), exactly like a spec folder.

### Render context

The template is rendered with the file's `parameters` **plus** the path-derived
`service_name` and `provider_name`. So `specs/unitysvc/resp200.json` injects
`service_name = "unitysvc/resp200"` and `provider_name = "unitysvc"`. Set
`listing.name` from `{{ service_name }}` in the template to keep the rendered name
bound to the path — just as a spec folder's path binds its `listing.name`.

## The template

A local template directory holds a static `provider.json` plus `*.j2` files for
the parts that vary, and may carry **extra files** (connectivity tests, code
examples, docs) that the rendered listing references by relative path — they're
bundled with the rendered service, same as a hand-authored folder.

```jinja
{# templates/resp/offering.json.j2 (representative) #}
{
  "name": "resp{{ status }}",
  "service_type": "gateway",
  "status": "ready",
  "description": "Always returns HTTP {{ status }} ({{ label }}) — {{ blurb }}.",
  "upstream_access_config": {
    "direct_response": { "access_method": "http", "base_url": "resp://{{ status }}" }
  }
}
```

### Template organization

Pick one layout per repo:

1. **Single default** — `templates/{provider.json, offering.json.j2, listing.json.j2}`;
   param files **omit** `template`.
2. **Multiple named** — `templates/<name>/…`; param files set `"template": "<name>"`.

> If the same repo also runs a [populator](generate-catalog.md) (which also uses
> `templates/`), use **named** subdirectories here so the two don't share one
> ambiguous `templates/*.j2` set.

### Local vs remote templates

A `template` value resolves to a **local** template if `templates/<name>/` exists,
otherwise it is treated as a **remote** platform template:

| `template` | Resolves to | Realized by |
|---|---|---|
| omitted | local `templates/` | `usvc_seller specs …` |
| `"<name>"` and `templates/<name>/` exists | local directory | `usvc_seller specs …` |
| `"<name>"` with no matching directory | remote platform template | `usvc_seller params instantiate` (see [Create from a Template](create-from-template.md)) |

## Validate, test, upload

The `specs` commands render param files on the fly, then act on the result —
exactly as they do for spec folders:

```bash
usvc_seller specs validate  [NAME]   # render → schema + layout checks
usvc_seller specs run-tests [NAME]   # render → run connectivity / code-example tests
usvc_seller specs upload    [NAME]   # render → upload via the normal path
```

`NAME` fnmatches the service name (omit = all), exactly like spec folders.
`usvc_seller specs format` formats the param files themselves (it does not render
them).

### Identity round-trips through the sidecar

On the first upload a new service is created and its `service_id` is written to
the **`<name>.service.json` sidecar** beside the param file:

```jsonc
// specs/unitysvc/resp200.service.json
{ "name": "unitysvc/resp200", "service_id": "…" }
```

Commit it — later uploads read it to update *the same* service instead of
creating a duplicate. It is kept **separate from the param file** so regenerating
the param file never clobbers identity. Delete it to upload as a brand-new
service. This is the same `service.json` philosophy as a spec folder.

## Generating param files in bulk

Param files are small, so they're usually hand-written — but for a larger set you
can generate them with a script (commonly `scripts/update_params.py`) that writes
**param files**, not specs. This keeps the ephemeral-render model (no generated
specs in git) while scaling past hand-authoring.

The difference from [Generate a Catalog](generate-catalog.md): a **populator**
(`usvc_seller specs populate`) *materializes* full spec folders into the repo and
keeps them in sync with a source list; param-file generation stays compact and
ephemeral. Reach for the populator when you want the generated specs committed and
reviewable, or when the source list churns; reach for param files when the set is
small and you'd rather not commit generated output.

## See also

- [Author & Upload Specs](author-specs.md) — spelled-out folders for bespoke services.
- [Generate a Catalog](generate-catalog.md) — materialize many services from a source list.
- [Create from a Template](create-from-template.md) — instantiate a **platform** template.
- [Service Templates](../service-templates.md) — how all the template-based shapes compare.
