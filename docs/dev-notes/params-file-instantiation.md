# Design: parameterized services — remote `params` vs local ephemeral specs

Status: **proposed**. Supersedes the earlier "one command, branch on the
`template` field" sketch — that conflated two genuinely different mechanisms.
First test bed: `unitysvc-services-resp`.

## Motivation

`unitysvc-services-resp` ships six services (`resp200` … `resp503`) that differ
in **three values** — an HTTP `status`, a `label` ("OK", "Service Unavailable",
…), and a one-line `blurb` — and are otherwise identical. Six hand-written
`offering.json` + `listing.json` pairs is six copies of one shape. We want
*one template + six tiny value files*.

## Two different mechanisms — keep them separate

"Template + parameter values → a service" can be realized two ways, and they are
**not** the same operation:

| | **Remote / system template** | **Local template** |
|---|---|---|
| Renders | **server-side** (backend owns the template) | **client-side** (the SDK renders `.j2`) |
| Backend receives | a template id + params | finished `offering`/`listing` specs |
| Backend object | a **TemplateInstance** → Service (binding kept) | a plain **Service** |
| Local `validate` / `run-tests` first | no (render is server-side) | **yes** (full spec known client-side) |
| Generated specs on disk | n/a | **ephemeral** — rendered at upload, never committed |
| It is… | a genuine **instantiate** | **`specs upload` with a renderer in front** |

Putting both behind one verb hides that a local template never reaches the
backend *as* a template. So:

- **`params`** (the command) handles **remote system templates** only.
- **Local template + value files** is a **`specs` generation mode** — it renders
  and uploads through the normal `specs` path, reusing all of its machinery
  (validate, run-tests, `service.json`, revisions).

## A. `params` — remote system templates

Unchanged from today: instantiate a platform-published template server-side.

```bash
usvc_seller params instantiate <system-template> -P key=value …
```

The backend renders the template, creates the service, and returns a
`service_id`. We persist it (in a `*.service.json` sidecar); on re-run we submit
with that `service_id` and the backend applies the **same revision semantics as
`specs upload`** — update in place if draft/pending, create a `revision_to` if
the service is active. Sellers cannot author platform templates (admin action),
and the staging catalog is currently empty — so `params` has no test bed yet.
See the backend dependency below.

## B. Local template + value files — ephemeral specs

This is the resp test bed and the part we build first. **The committed source of
truth is the template + the value files; the generated specs are never written
to git** — they're rendered in memory at upload time. This is the key difference
from the populator (`specs populate` / `update_specs.py`), which *materializes*
specs into the repo.

### Repo layout

```
templates/resp/                 # a local template directory
├── provider.json               # static
├── offering.json.j2            # {{ status }} {{ label }} {{ blurb }}
├── listing.json.j2             # {{ status }} {{ label }} → references connectivity.sh.j2
└── connectivity.sh.j2          # extra file, bundled into the rendered service
params/                         # one value file per service (flat)
├── resp200.json
├── resp200.service.json        # identity sidecar (service_id) — written on upload, committed
├── resp400.json   resp404.json   resp429.json   resp500.json   resp503.json
└── …
```

No `specs/` directory — that's the point.

### Value file — `params/<name>.json`

```jsonc
{
  "template": "templates/resp",        // a local template directory (repo-root-relative)
  "name": "unitysvc/resp200",          // the service name (= listing.name)
  "parameters": { "status": 200, "label": "OK",
                  "blurb": "success sink — close the request loop with a 200 and no upstream" }
}
```

Flat files (not `params/resp200/param.json`) because a value file is a single
dict — the template owns the structure, docs, and tests. They can be
hand-written or produced by an `update_params.py` script (the script writes
*params*, not specs).

### Identity sidecar — `params/<name>.service.json`

```jsonc
{ "name": "unitysvc/resp200", "service_id": "…" }
```

Separate from the value file so a regenerated value file never clobbers
identity — exactly the `specs` `service.json` philosophy. Committed; read on the
next upload to update the same service; delete to re-create as new.

### Template organization

A `template` value resolves to a **local template directory** under the repo.
Two layouts (your choice per repo):

1. **Single default** — enough for most repos:
   `templates/{provider.json, offering.json.j2, listing.json.j2}`; reference as
   `"template": "templates"`.
2. **Multiple named** — `templates/<name>/…`; reference the directory,
   `"template": "templates/resp"`.

A local template directory may carry **extra files** (connectivity tests, code
examples, docs) that the rendered listing references by relative path; they're
bundled with the rendered service, same as a hand-authored spec folder.

> The populator also uses `templates/`. A repo that runs both should use **named**
> subdirectories here to avoid sharing one ambiguous `templates/*.j2` set.

### Commands — the `specs` path renders on the fly

```bash
usvc_seller specs validate  [NAME]   # render params/<NAME> × its template → validate the specs
usvc_seller specs run-tests [NAME]   # render → run the connectivity / code-example tests
usvc_seller specs upload    [NAME]   # render → upload via the normal path; read/write service.json
```

`specs` learns that a repo with `params/` + `templates/` (and no `specs/`)
renders each value file through its template in memory, then validates / tests /
uploads the result. `NAME` fnmatches `params/*.json` (omit = all), mirroring the
existing `specs upload [NAME]`. Identity round-trips through the per-value
`*.service.json` exactly as committed spec folders round-trip through
`service.json`.

> Naming note: the `params` **command** (remote) and the `params/` **directory**
> (local value files consumed by `specs`) share a word but are different things —
> "params" = the parameter-values concept; the mechanism that realizes them
> differs. Flagged for a possible rename if it reads as confusing.

### resp `offering.json.j2` (representative)

```jinja
{
  "capabilities": ["http_relay"],
  "description": "Direct-response service that always returns HTTP {{ status }} ({{ label }}) from the gateway with no upstream call — {{ blurb }}. Backed by the reserved resp://{{ status }} upstream scheme (unitysvc/unitysvc#1188).",
  "name": "resp{{ status }}",
  "service_type": "gateway",
  "status": "ready",
  "tags": ["gateway", "test", "direct-response"],
  "upstream_access_config": {
    "direct_response": { "access_method": "http", "base_url": "resp://{{ status }}" }
  }
}
```

Six value files replace six `offering.json` + `listing.json` pairs; the template
and the single shared `connectivity.sh.j2` carry everything common — and nothing
generated is committed.

## Backend dependency (path A only)

The **remote** path needs the instantiate endpoint to accept an **existing
`service_id`** and apply `specs`-style revision semantics (update if
draft/pending, `revision_to` if active), so re-instantiation from the sidecar
updates the same service instead of duplicating. Tracked in
**[unitysvc/unitysvc#1273](https://github.com/unitysvc/unitysvc/issues/1273)**.
The **local** path (B) needs none of this — it rides the existing
`specs upload` + `service_id` round-trip.

## Phasing

1. **Path B (local, ephemeral)** — build now, no backend work: value-file +
   sidecar formats, local-template resolution, render-on-the-fly in
   `specs validate/run-tests/upload`, `[NAME]` batching. Convert
   `unitysvc-services-resp` to it end-to-end as the proof.
2. **Path A (remote)** — once #1273 lands: `params instantiate` records
   `service_id` in the sidecar and re-submits to revise on re-run.

## Out of scope

- Authoring **platform** templates (admin-only).
- Changing the populator (`specs populate`) — it *materializes* specs by design;
  path B deliberately does not.
