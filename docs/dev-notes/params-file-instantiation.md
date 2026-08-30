# Design: parameterized services — system templates and local ephemeral specs

Status: local template param files are implemented (`unitysvc-sellers` ≥ 0.2.4),
and system-template param files now use the same `specs upload` surface. The
user-facing guides are [Compact Specs with Param Files](../guides/param-files.md)
and [Create from a System Template](../guides/create-from-template.md).

## Motivation

`unitysvc-services-resp` ships six services (`resp200` … `resp503`) that differ
in **three values** — an HTTP `status`, a `label` ("OK", "Service Unavailable",
…), and a one-line `blurb` — and are otherwise identical. Six hand-written
`offering.json` + `listing.json` pairs is six copies of one shape. We want
*one template + six tiny param files*.

## Two different mechanisms — keep them separate

"Template + parameter values → a service" can be realized two ways, and they are
**not** the same operation:

| | **Remote / system template** | **Local template** |
|---|---|---|
| Renders | **server-side** (backend owns the template) | **client-side** (the SDK renders `.j2`) |
| Backend receives | a template id + params | finished `offering`/`listing` specs |
| Backend object | a normal **Service** with template source metadata | a plain **Service** |
| Local `validate` / `run-tests` first | no (render is server-side) | **yes** (full spec known client-side) |
| Generated specs on disk | n/a | **ephemeral** — rendered at upload, never committed |
| It is… | a genuine **instantiate** | **`specs upload` with a renderer in front** |

Putting both behind one verb hides that a local template never reaches the
backend *as* a template. So we split by **command**, not by a hidden branch:

- **`specs`** is the single command for **all local authoring**. A repo's
  services may be defined as committed spec folders, as param files whose
  `template` is a **local directory** (rendered ephemerally), or a **mix** —
  `specs validate / run-tests / upload / list [NAME]` handle all of them through
  one path (param-defined services are simply rendered in memory first). "Params
  + template" is thus just a *compact way to author specs*.
- **`specs upload`** also handles **system templates**. Param files whose
  `template` does not resolve to a local directory are posted to backend
  instantiation instead of rendered by the SDK.

| You have… | Command |
|---|---|
| spec folders, and/or param files with a **local** `template` | `usvc seller specs …` |
| a **remote** system template + values | `usvc seller specs upload` |

**Everything lives under `specs/` — no separate `params/` directory.** A service
at `<provider>/<name>` is defined by exactly one of:

```
specs/<provider>/<name>/          ← explicit spec folder (offering + listing(s) + provider)
specs/<provider>/<name>.json      ← param file ({ template, parameters })
specs/<provider>/<name>.service.json   ← identity sidecar (sibling), holds service_id
```

The path → service_name mapping is uniform (folder or file). A param file's
`template` routes it: a **local directory** → rendered by the SDK, a **remote
name** → rendered by backend instantiation. Both happen under `specs upload`; the
`*.service.json` sidecar is identical for both. So `specs/` is the single home
for all service definitions; a folder and a `.json` file at the same path is an
error.

## A. System templates

Instantiate a platform-published template server-side. Two input forms:

```bash
usvc seller specs upload [NAME]       # from specs/<name>.json with a system template
```

The upload command reads `specs/`, processing param files whose `template` is a
system-template name or id. The backend renders the template, creates the
service, and returns a `service_id`. We persist it in a `*.service.json` sidecar;
on re-run we submit with that `service_id` and the backend applies normal
revision semantics. Sellers cannot author system templates; they discover them
with `usvc seller templates list/show`.

## B. Local template + param files — ephemeral specs

This is the resp test bed and the part we build first. **The committed source of
truth is the template + the param files; the generated specs are never written
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
specs/unitysvc/                 # one param file per service, beside any explicit folders
├── resp200.json
├── resp200.service.json        # identity sidecar (service_id) — written on upload, committed
├── resp400.json   resp404.json   resp429.json   resp500.json   resp503.json
└── …
```

For resp every service is a param file, so there are no spec *folders* — but
they could sit right here alongside the `.json` files if some service needed
hand-authoring.

### Param file — `specs/<provider>/<name>.json`

Two keys, both about as small as it gets: an optional `template` and a
`parameters` object.

```jsonc
// named template (templates/resp/)
{ "template": "resp", "parameters": { "status": 200, "label": "OK",
                                      "blurb": "success sink — close the request loop with a 200 and no upstream" } }

// single default template (templates/) — no template key
{ "parameters": { "status": 200, "label": "OK", "blurb": "…" } }
```

- **`template`** is a **bare name resolved under `templates/`**, and is
  **optional**: omit it for the single default template `templates/`; set
  `"resp"` for `templates/resp/`. (No path prefix.) A name resolves to a **local**
  template if `templates/<name>/` exists, otherwise it's a **system** template
  rendered by backend instantiation during `specs upload`.
- **`parameters`** holds the values, nested (not spread at top level) so a value
  may safely be named `template`/`name`/etc., matching the SDK's
  `instances.create(parameters={…})` shape and leaving room for future control
  keys beside `template`.
- **No `name` field** — the service name comes from the **path**
  (`specs/unitysvc/resp200.json` → `unitysvc/resp200`), same as a spec folder.

Param files can be hand-written or produced by an `update_params.py` script (the
script writes *params*, not specs).

### Identity sidecar — `specs/<provider>/<name>.service.json`

```jsonc
{ "name": "unitysvc/resp200", "service_id": "…" }
```

Separate from the param file so a regenerated param file never clobbers
identity — exactly the `specs` `service.json` philosophy. Committed; read on the
next upload to update the same service; delete to re-create as new.

### Template organization

A `template` value is a **bare name resolved under `templates/`**. Two layouts
(your choice per repo):

1. **Single default** — enough for most repos:
   `templates/{provider.json, offering.json.j2, listing.json.j2}`; param files
   **omit** `template`.
2. **Multiple named** — `templates/<name>/…`; param files set `"template":
   "<name>"` (e.g. `"resp"` → `templates/resp/`).

Resolution (and local-vs-system routing): `template` omitted → local
`templates/`; `template: "<name>"` → local `templates/<name>/` if that directory
exists, otherwise a **system** template named `<name>` (handled by backend
instantiation during `specs upload`).

A local template directory may carry **extra files** (connectivity tests, code
examples, docs) that the rendered listing references by relative path; they're
bundled with the rendered service, same as a hand-authored spec folder.

**Render context** = the file's `parameters` plus the path-derived
`service_name` / `provider_name` (so `specs/unitysvc/resp200.json` injects
`service_name = "unitysvc/resp200"`, `provider_name = "unitysvc"`). The template
sets `listing.name` from `{{ service_name }}`, keeping the rendered name bound to
the path exactly as a spec folder's path binds its `listing.name`.

> The populator also uses `templates/`. A repo that runs both should use **named**
> subdirectories here to avoid sharing one ambiguous `templates/*.j2` set.

### Commands — the `specs` path renders on the fly

```bash
usvc seller specs validate  [NAME]   # render specs/<NAME>.json × its template → validate
usvc seller specs run-tests [NAME]   # render → run the connectivity / code-example tests
usvc seller specs upload    [NAME]   # render → upload via the normal path; read/write *.service.json
```

`specs` walks `specs/`, treating each `<name>/` as an explicit spec folder and
each `<name>.json` as a param file. Local-template params render in memory for
validate / test / upload. System-template params are only actionable during
upload, where they are sent to backend instantiation. `NAME` fnmatches the
service name (omit = all), exactly as today's `specs upload [NAME]`. Identity
round-trips through the `<name>.service.json` sidecar just as a folder
round-trips through its `service.json`.

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

Six param files replace six `offering.json` + `listing.json` pairs; the template
and the single shared `connectivity.sh.j2` carry everything common — and nothing
generated is committed.

## Out of scope

- Authoring **platform** templates (admin-only).
- Changing the populator (`specs populate`) — it *materializes* specs by design;
  path B deliberately does not.
