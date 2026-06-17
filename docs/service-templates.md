# Service Templates

A **service template** is a *parameterized* version of service data: the
`offering.json` / `listing.json` (and friends) you would otherwise write by
hand, but with the parts that change from one service to the next replaced by
**parameters** — and a small amount of logic that fills those parameters in.
Render the template with a set of parameter values and you get back complete,
schema-valid service data, ready to validate and upload.

> **Is there a word for this?** The act is **parameterizing** (or
> "templatizing") your service data; the result is a **parameterized service
> definition**. Throughout the platform we just call it a *service template*.

If a plain service is "one filled-in form", a service template is "the blank
form plus instructions for filling it" — which is exactly what makes it good at
two jobs:

1. **Offer a common service with almost no effort** — the hard parts (pricing
   shape, upstream config, tests) are authored once, by the template, and you
   supply only a handful of values.
2. **Populate a whole *group* of services at once** — point a template at a
   list (your upstream's model catalog, a spreadsheet, an API) and generate one
   service per item, consistently.

## Ways to use service templates

The uses sit on a spectrum from *least effort* to *most control*. Pick the row
that matches what you're doing.

| Use | Who authors the template | How you use it | Best for |
|---|---|---|---|
| **1. Platform templates** | The platform | Dashboard *Create from template*, or `usvc_seller params instantiate` | Offering a common service type with zero file authoring |
| **2. Capability pools** | The platform (template carries a pool name) | Instantiate a pool template (dashboard or CLI); you provide only the upstream URL | Joining a fungible, uniformly-priced commodity pool |
| **3. Your own template + param files** | You | A tiny param file per service + `usvc_seller specs upload` (rendered ephemerally) | A **few** services that share one shape, authored by hand |
| **4. Your own templates + populate** | You | Author `.j2` templates + a populator script, then `usvc_seller specs populate` (materializes specs) | Generating **many** services programmatically from a source list |

### 1. Platform service templates — the easy path

The platform publishes **curated templates** for the most common service types
(e.g. an OpenAI-compatible LLM endpoint). This is the **easiest way to create
and upload a service**: in the dashboard, choose *Create from template*, fill a
short, typed form (model id, upstream URL, an API-key secret name, a price),
and the platform renders the complete service spec, runs the bundled
connectivity test, and submits it through the normal publish pipeline. No local
files to author and no test to write — the template ships its own.

You manage the resulting service exactly like any other (it appears under your
**Staging** list), and if you outgrow the template you can download the rendered
files and refine them with this SDK.

**From the CLI / CI**, the same flow is available without the dashboard — browse
the catalog with `templates`, instantiate with `params`:

```bash
usvc_seller templates list                        # active platform templates
usvc_seller templates show openai-compatible-llm  # its parameters
usvc_seller params instantiate openai-compatible-llm \
    -P api_base_url=https://api.example.com/v1 \
    -P api_key_secret_name=UPSTREAM_API_KEY \
    -P input_price=1.00
```

**From the SDK**, `client.templates` (catalog) and `client.instances` (create):

```python
from unitysvc_sellers import Client

with Client() as client:
    result = client.instances.create(
        "openai-compatible-llm",
        parameters={
            "api_base_url": "https://api.example.com/v1",
            "api_key_secret_name": "UPSTREAM_API_KEY",
            "input_price": 1.00,
        },
        # Leaves a reviewable draft by default; pass auto_submit=True to also submit.
    )
```

`create` renders the template into a **draft** service — returning the new
`instance_id` and the ingest `task_id` — and leaves it a reviewable draft by
default (mirroring the backend's `auto_submit=false`). Pass `--submit` (CLI) /
`auto_submit=True` (SDK) to also submit it for review in the same call (otherwise
submit later with `usvc_seller services submit`). Secret-typed parameters take the **secret name**
(create it first with `usvc_seller secrets`), never the key value. See the
[SDK Guide → `client.instances`](sdk-guide.md#clientinstances) for the full API.

### 2. Capability pools — opt in with a pool name

A **capability pool** (`/p/<capability>`) is a special platform template that
carries a **pool name**. Every service instantiated from a pool template
automatically joins `/p/<pool-name>`, where the gateway load-balances across all
verified providers of that capability. Because the model, contract, **price, and
terms are fixed by the template**, every member is fungible — you only provide
your upstream URL (and a key secret, if your upstream needs one). Opting in is
that simple: in the dashboard, instantiate the pool template.

A few consequences worth knowing:

- **Uniform price → performance routing.** Every member is billed at the pool's
  single price, so the pool routes requests by performance (latency / quality /
  health), not cost.
- **Opt-in and non-exclusive.** Want a different price? Offer the same
  capability as a **separate, standalone service** at your own price; pool
  membership doesn't stop you.
- **Membership comes only from a pool template.** A pool service can be created
  *only* by instantiating a pool-named template — `usvc_seller specs upload` of a
  hand-authored spec always produces a plain standalone service, never a pool
  member.

### 3. Your own template + param files — compact, ephemeral

When a *handful* of services share one shape, you don't need a populator. Author
**one local template** under `templates/` and a tiny **param file** per service —
`{ template, parameters }` — under `specs/`. The `specs` commands render the full
specs **in memory** at validate / test / upload time; nothing generated is
committed. The source of truth is the template plus the small param files.

```jsonc
// specs/unitysvc/resp200.json
{ "template": "resp", "parameters": { "status": 200, "label": "OK", "blurb": "…" } }
```

```bash
usvc_seller specs validate   # render param files × template → validate
usvc_seller specs upload      # render → upload (identity round-trips via *.service.json)
```

This is your *own* template rendered on your machine — distinct from #1, where the
platform owns and renders the template. The full how-to (param-file format,
template resolution, identity sidecar, generating param files in bulk) is in
[Compact Specs with Param Files](guides/param-files.md).

### 4. Your own templates — `usvc_seller specs populate`

When you offer *many* similar services — every model your upstream serves, a
region per endpoint, a tier per plan — author the template **yourself** and let
the SDK generate the catalog. This is the populator pattern, and it's the
SDK-native way to **populate a group of services**:

1. Author `offering.json.j2` / `listing.json.j2` (and any doc/test templates)
   under `templates/` at the repo root, replacing the per-service values with
   `{{ placeholders }}`.
2. Write a **populator script** (commonly `scripts/update_specs.py`) that yields
   one parameter dict per service — typically by reading your upstream's model
   list. SDK-based scripts can lean on
   `unitysvc_sellers.template_populate.populate_from_iterator`, which renders the
   flat nested layout, copies `provider.json` into each service folder, and
   localizes documentation references for you.
3. Declare it in `templates/config.json` under a `services_populator` object:

   ```json
   {
     "services_populator": {
       "command": ["scripts/update_specs.py"],
       "requirements": ["..."]
     }
   }
   ```

   (Your `provider.json` stays a pure provider definition — the populator
   declaration lives in `templates/config.json`, not in `provider.json`.)
4. Run it:

   ```bash
   usvc_seller specs populate           # render every service from the template
   usvc_seller specs populate --dry-run # preview without writing files
   ```

   The generated `specs/<provider>/<service>/` folders — each self-contained with
   `provider.json`, `offering.json`, and `listing.json` — are normal service
   data: validate, test, and upload them like anything else. Re-running
   `populate` keeps the catalog in sync with the source list: services that
   disappear upstream are marked `deprecated`, and unchanged services don't churn
   because their `time_created` is preserved.

The full, step-by-step guide — converting a working service into templates,
writing the populator, filtering, and CI automation — lives in
[Generate a Catalog](guides/generate-catalog.md).

## Which one should I use?

- **One common service, fastest path?** → Platform template (use #1).
- **Joining a commodity pool at the platform's price?** → Capability pool
  (use #2).
- **A few services that share one shape, authored by hand?** → Your own template
  + [param files](guides/param-files.md) (use #3).
- **Generating a catalog of many services from a source list?** → Your own
  templates + [`populate`](guides/generate-catalog.md) (use #4).

Uses #1 and #2 are about **ease** (the platform did the hard authoring for you);
uses #3 and #4 are about **reuse of your own template** — #3 stays compact and
ephemeral for a handful, #4 *materializes* a whole catalog at scale. They compose
freely — a seller might join a capability pool for a commodity model, keep a few
hand-tuned endpoints as param files, *and* run a populator for their long tail.

For the purely hand-authored, no-template case, see
[Author & Upload Specs](guides/author-specs.md).
