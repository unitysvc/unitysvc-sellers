---
name: writing-unitysvc-services
description: Author UnitySVC service files (offering.json + listing.json + connectivity test + optional code examples) in the flat `specs/` layout, set up the `templates/` + param-file pattern when a repo will host many similar services, and drive each service through the validate → format → run-tests (local upstream) → upload → run-tests (gateway) pipeline. Use this skill whenever the user wants to add, modify, regenerate, or troubleshoot a service in a `unitysvc-services-*` repo, or asks for help writing an `offering.json` / `listing.json` / a `templates/<name>/*.j2` + param file, even if they don't name the skill explicitly. Also use when they mention connectivity tests, BYOK / BYOE / multi-channel (`plus`) patterns, gateway base_urls, customer secrets, or `usvc_seller specs` / `services` / `params` commands. The skill is **rigid** about the verification order (a service is not "ready" until `specs validate`, `specs format`, `specs run-tests`, AND `services run-tests` all pass) and about the connectivity-test requirement (every service must have at least one).
---

# Writing UnitySVC Services

A UnitySVC service is two pieces of declarative data — an **offering** (technical spec: upstream URL, auth, capabilities, payout) and one or more **listings** (customer-facing: gateway path, list price, docs) — plus tests that prove the upstream and the gateway actually work. This skill is the workflow for going from "we want a new service" to "the service is live on staging and a curl through the gateway returns 200."

The skill assumes the local repos under `~/unitysvc/` are checked out and writable, and that `usvc_seller` is installed (via `uvx --from unitysvc-sellers usvc_seller …` if not on PATH).

**Environment for staging access.** Anything that talks to the staging backend (`usvc_seller specs upload`, `usvc_seller services list/show/run-tests`, manual `curl https://api.staging.svcpass.com/…`) needs the seller API key and URL in env. Source `~/.zshrc` first:

```bash
zsh -ic 'source ~/.zshrc && usvc_seller services list'
# or, when starting an interactive session:
source ~/.zshrc
```

`~/.zshrc` defines `UNITYSVC_SELLER_API_KEY`, `UNITYSVC_SELLER_API_URL` (= `https://seller.staging.unitysvc.com/v1/`), and `UNITYSVC_API_KEY` (the same svcpass key used to authenticate as a customer to the gateway). If a command returns 401 or "Missing svcpass API key", you forgot to source.

## 1. Find the right pattern first — don't write blind

The single highest-leverage move when starting a new service is to **find an existing service that already works and copy its shape**. The canonical catalog of patterns lives in [`unitysvc-services-demo`](https://github.com/unitysvc/unitysvc-services-demo). Each subdirectory under `specs/unitysvc-demo/` is a minimal working example of one delivery pattern. The table in `specs/README.md` maps patterns to use cases:

| Pattern | When the user wants … |
|---|---|
| `relay` | minimal seller-managed HTTP upstream, no auth |
| `llm` | OpenAI-compatible LLM with token pricing |
| `byok` | customer brings their own API key |
| `byoe` | customer brings both endpoint URL and key |
| `params` | per-enrollment routing key from a user parameter |
| `byoe-params` | parameterized customer-secret *names* |
| `multi-channel` | one offering with several upstream channels (e.g. free `byok` + paid `plus`), channel-keyed pricing |
| `enrollment` | per-enrollment URL fragment via the intrinsic `{{ enrollment.code }}` |
| `recurrent` | scheduled / recurrence service |
| `routing_vars` | seller knobs editable after activation |
| `s3` / `s3-byoe` / `s3-byoe-params` | S3 gateway variants |
| `smtp` / `smtp-byoe` / `smtp-byoe-params` | SMTP gateway variants |
| `transformer` | gateway body-transform / forwarder pattern |

**Concrete instruction:** before drafting any file, `ls ~/unitysvc/unitysvc-services-demo/specs/unitysvc-demo/` and `cat` the closest match's `offering.json` + `listing.json`. Copy fields you don't yet understand verbatim; you can simplify later. The schemas allow extra fields and reject missing required ones — having too much from a working example is safer than too little from your imagination.

When the closest demo is itself not enough — e.g. provider-specific routing oddities — look at a real production repo that ships the same shape:
- LLM with BYOK: `~/unitysvc/unitysvc-services-anthropic` / `…-cohere` / `…-deepseek`
- LLM with multi-variant listings: `~/unitysvc/unitysvc-services-parasail` (hierarchical model names)
- HTTP relay / gateway loopback: `~/unitysvc/unitysvc-services-http`
- S3 / SMTP / direct-response: `~/unitysvc/unitysvc-services-s3` / `…-smtp` / `…-resp`

## 2. File organization — the flat `specs/` layout

Services live under `specs/` (plus an optional `templates/` at the repo root for the param-file pattern, §6). The *location* is load-bearing: the folder (or param-file stem) under `specs/<provider>/` IS the service name. A service is authored one of two ways — a **concrete folder** or a **param file** that renders to one.

> Files carry **no `schema` field** (removed) — role is fixed by filename (`offering.json`, `listing.json`, `provider.json`, `service.json`). `.toml` is accepted anywhere `.json` is.

### Concrete service (hand-authored)

```
specs/
└── <provider-slug>/                  # provider directory (= the first segment of listing.name)
    └── <service-name>/               # folder name = the BARE service name
        ├── offering.json|.toml       # required: one offering_v1
        ├── listing.json|.toml        # required: one or more listing_v1
        ├── provider.json             # the provider_v1 record (accompanies each service folder)
        ├── service.json              # identity sidecar: { "service_id": "…" } — auto-written on upload, COMMIT it
        └── <service-specific docs>   # optional: connectivity.sh.j2, description.md, …
```

`http-relay` (`specs/http-relay/…`) and the demo services (`specs/unitysvc-demo/<name>/…`) are the reference shapes.

### Param-file service (one template, many services)

When many services share a shape, author each as a compact **param file** that an in-repo template renders *ephemerally* at validate / format / upload / test time (§6):

```
templates/
└── <template-name>/                  # e.g. notify-relay
    ├── provider.json                 # copied into every rendered service
    ├── offering.json.j2              # rendered per param file
    ├── listing.json.j2
    └── config.json                   # optional — only if `specs populate` regenerates the params from a script
specs/
└── <provider-slug>/
    ├── <name>.json                   # the param file: { "template": "<template-name>", "parameters": { … } }
    └── <name>.service.json           # identity sidecar for that param file
```

Adding a service = adding one `<name>.json` param file. The pipeline renders it into a *temporary* `specs/<provider>/<name>/` folder (offering + listing + provider), runs against it, round-trips the backend `service_id` into `<name>.service.json`, and removes the folder. **Commit the param file + its `.service.json` sidecar — never the rendered folder.** A param file whose `template` doesn't resolve to a local `templates/<name>/` dir is a *system* template — instantiate it with `usvc_seller params instantiate` instead (§6).

### Hard rules — validator/uploader will reject violations

1. **`listing.name` MUST equal `<provider>/<service-name>`** — the path under `specs/`. Validate rejects a mismatch (e.g. folder `specs/labs/discord-relay/` → `listing.name = "labs/discord-relay"`). `offering.name` stays the **bare** `<service-name>` (`discord-relay`).
2. **Exactly one `offering_v1` per service** ("Multiple offering files found" otherwise); **at least one `listing_v1`** (several allowed — pricing tiers, `@variant` tags).
3. **`service.json` carries the `service_id`** (see below) — commit it, don't hand-edit it.
4. **External files** referenced from a listing's `documents` block resolve relative to the listing's folder; a path that escapes the folder (`../shared/foo.j2`) shares one file across services.

### Service identity is derived, not declared

A backend **Service** is the identity record. Its `name`, `display_name`, and `status` are derived at upload:

- `service.name` ← `listing.name` (required at ingest, #1196).
- `service.display_name` ← `listing.display_name` → `offering.display_name` → the names (first non-empty wins).
- `service.status` ← worst-of the component statuses: any `draft` → service draft (upload skipped); any `deprecated` (no draft) → deprecated; all `ready` → progresses through review.

### The `service.json` sidecar — the service_id lifecycle

`service.json` (`{ "service_id": "…" }`) — or `<name>.service.json` next to a param file — is auto-written on the first successful `specs upload` and carries the backend `service_id`, so later uploads target the existing service rather than creating a new one. Treat it as:

- **Committed to version control** — links your local data to a specific service in staging/prod.
- **Never hand-edited** unless you deliberately want to re-upload as a brand-new service (delete it in that case).
- **Environment-specific** — staging and prod get different `service_id`s; manage via separate branches/dirs.

A re-upload of changed content queues an admin-review **revision** rather than mutating the active row in place — that's expected (submit it to promote). (This replaces the old `listing.override.json` mechanism.)

### Multiple listings per offering

When one offering ships in multiple variants (basic / premium / `@byok` / `@byop` / per-marketplace), put each listing as a separate file in the same service folder:

```
specs/cohere/command-r-plus/
├── offering.json
├── listing-byok.json     # name: "cohere/command-r-plus@byok"
└── listing-byop.json     # name: "cohere/command-r-plus@byop"
```

Set each listing's `name` explicitly (`<provider>/<service>@<variant>`). Note this is distinct from **multi-channel** (one listing, several `upstream_access_config` channels priced by a channel-keyed `list_price` — see §11): variants are separate listings/URLs, channels are alternative fulfilment paths under one listing.

## 3. Naming conventions (listings, services, gateway paths)

The validator at `usvc-core` runs on every `usvc_seller specs validate` and rejects non-conformant catalogs *before* upload. Three places where naming matters:

### Listing `name` grammar

```
<segment>[/<segment>...][@<variant>]
```

Per-segment rules (apply to every `/`-separated piece):

| Rule | Detail |
|---|---|
| Min length | **≥ 2 characters.** Single-char segments are reserved (see below). |
| Allowed chars | `A-Z`, `a-z`, `0-9`, `.`, `-`, `_`. |
| First char | Must be alphanumeric. No leading `-`, `_`, `.`. |
| `@` variant tag | At most one `@`. Variant has the same per-segment rules but **no min-length** — variants sit after `@` so they don't collide with reserved primitive prefixes. |
| Hierarchical | Multi-segment names like `Qwen/Qwen2.5-Coder-7B-Instruct` are accepted; each segment validated independently. |

```
✓ command-r-plus
✓ command-r-plus@byok
✓ Qwen/Qwen2.5-Coder-7B-Instruct@byok
✗ a                  (single-char)
✗ -leading-dash      (must start alphanumeric)
✗ has space          (space not allowed)
✗ name@v1@v2         (multiple @)
✗ /leading           (leading or trailing / rejected)
```

### Namespaced names — first segment must be the provider slug

If `listing.name` contains `/`, the first segment must equal the provider's `name`:

```
provider.name = "cohere"        → listing.name = "cohere/command-r"       ✓
provider.name = "labs"          → listing.name = "labs/http-relay-plus"   ✓
provider.name = "unitysvc-labs" → listing.name = "labs/http-relay-plus"   ✗  (slug mismatch)
```

A bare name (no `/`) is a top-level handle and currently accepted without provider scope — useful for platform-internal services where a short URL is preferred (e.g. `http-relay`, `resp200`). The admin-approval gate for top-level names is deferred.

### `user_access_interfaces.<iface>.base_url` grammar

The validator only constrains the path **after** `${API_GATEWAY_BASE_URL}/`. The portion before the first dynamic marker (`{{`, `{%`, `${`) is treated as the static identifier prefix and validated; everything from the marker on is per-enrollment substitution.

```
✓ ${API_GATEWAY_BASE_URL}/{{ service_name }}                            (most common — runtime substitution)
✓ ${API_GATEWAY_BASE_URL}/{{ service_name }}/{{ enrollment.code }}
✓ ${API_GATEWAY_BASE_URL}/a/cohere-latest                               (movable-pointer convention; see below)
✓ ${API_GATEWAY_BASE_URL}                                               (gateway root; platform-native interfaces)
✗ ${API_GATEWAY_BASE_URL}/cohere                                        (literal provider segment, no {{ service_name }})
✗ ${API_GATEWAY_BASE_URL}/cohere/command-r                              (literal <provider>/<service>)
```

The `{{ service_name }}` form is preferred because the gateway resolves it from `listing.name` at request time — data files stay deployment-agnostic. Literal paths are rejected by the post-PR-1196 validator.

### Reserved single-letter prefixes

Single-character first segments are reserved for the gateway's wrapper / primitive namespace. The platform layers behavior on top of any service URL using these prefixes; sellers can't claim them:

| Prefix | Reserved for |
|---|---|
| `a/` | Aliases & movable-pointer naming (carve-out — see below) |
| `b/` | Broadcast (fan-out one request to many services) |
| `c/` | Chain (sequence two or more services) |
| `d/` | Delayed dispatch |
| `f/` | Failover |
| `g/` | Groups |
| `l/` | Logging |
| `m/` | Memoize |
| `p/` | (legacy — superseded; bare provider path is the modern form) |
| `r/` | Recurrent |
| `t/` | Tee (fire-and-forget mirror) |

A base_url with any of these letters as the first path segment is rejected.

### `a/` — the only carve-out (movable-pointer convention, #1139)

A leading `a/` is permitted as a *customer-facing signal*: "this URL is a movable pointer — the publisher reserves the right to re-point its target at a newer listing later." No special routing semantics, just a naming convention so customers can tell `cohere/command-r-plus` (sticky listing) apart from `a/cohere-latest` (intentionally mutable).

After stripping the leading `a/`, the remainder is validated under the normal grammar. So:

```
✓ ${API_GATEWAY_BASE_URL}/a/cohere-latest
✓ ${API_GATEWAY_BASE_URL}/a/anthropic/claude-opus-latest
✓ ${API_GATEWAY_BASE_URL}/a/cohere-latest@byok
✗ ${API_GATEWAY_BASE_URL}/a/                                            (bare a/, no remainder)
✗ ${API_GATEWAY_BASE_URL}/a/x                                           (single-char after a/)
✗ ${API_GATEWAY_BASE_URL}/a/m/foo                                       (m/ still reserved at segment 2)
```

Use `a/` when you intend to re-point the URL over time (latest pointer, migration alias). Use the plain `<provider>/<service>` form for everything else — listing names are **sticky**: once published, the platform expects them to remain bound to the same underlying service.

## 4. Documentation that has the answers when the demo doesn't

The seller SDK repo carries authoritative docs at [`unitysvc-sellers/docs/`](https://github.com/unitysvc/unitysvc-sellers/tree/main/docs). Local mirror at `~/unitysvc/unitysvc-sellers/docs/`. Read these on demand:

- `service-templates.md` — the `templates/` + param-file model, `specs populate`, and system templates
- `file-schemas.md` — every field on `offering_v1`, `listing_v1`, `provider_v1`
- `pricing.md` — `list_price` / `payout_price` shapes (constant, one_million_tokens, **channel**, revenue_share, …) — go here BEFORE inventing a pricing block
- `service-types.md` — when to pick `llm` / `proxy` / `gateway` / `embedding` / etc.
- `naming-conventions.md` — listing.name grammar, `@variant` tags, provider-slug rule
- `documenting-services.md` — how `documents` blocks work (presets, file paths, connectivity tests)
- `cli-reference.md` — full `usvc_seller` command surface
- `seller-lifecycle.md` — submit / visibility / revisions; CI upload-on-merge
- `getting-started.md`, `sdk-guide.md` — orientation and the SDK end to end

When something in this skill conflicts with the docs, the docs win — they evolve with the platform.

## 5. The verification pipeline — a service is not "ready" until all four pass

The user's working definition of "ready": **`specs validate`, `specs format`, `specs run-tests`, AND `services run-tests` all green.** Skipping any step risks a silent breakage upstream. Run them in order; each catches a different class of mistake. (Param-file repos render ephemerally — every `specs` command auto-expands param files into temp folders, operates, and cleans up, so you run the same commands whether services are concrete or templated.)

```bash
# 1. Schema + cross-file validation (fast, no network).
#    Runs on every service under specs/.
usvc_seller specs validate

# 2. JSON/TOML/MD canonical formatting (writes in-place; commit the result).
usvc_seller specs format

# 3. Upstream-side tests: render and execute the connectivity / code-example
#    docs against the upstream URL directly (no gateway). Catches dead
#    upstreams, wrong base_urls, broken auth before the gateway sees them.
#    NAME is a restricted glob — see "Selector grammar" below.
usvc_seller specs run-tests <name>

# 4. Upload to staging so the gateway has a route to test against.
#    A re-upload of an existing service creates a *revision* (admin-review
#    queue) rather than mutating the active row in place — that's expected.
usvc_seller specs upload <name>

# 5. Gateway-side tests: the same documents executed from the platform,
#    routed through the gateway, exercising the registered route +
#    svcpass auth + the upstream chain end-to-end. The command skips
#    documents whose last per-iface result was 'success' — pass --force
#    to re-run them. NAME may match the active row plus the pending
#    revision; both rows get tested.
usvc_seller services run-tests <name> --force
```

**Testing does NOT require the service to be public or active.** The gateway test runner authenticates as the seller and can route freshly-uploaded draft/pending revisions through the gateway just to verify routing + svcpass attribution + upstream chain work end-to-end. `set-visibility` and `submit` are about making a service *customer-facing* — that's a separate publishing step, **not** part of the verification pipeline. Don't run them just to test.

When you *are* ready to publish (after all four verification gates pass) — that's a separate action, intentionally explicit:

```bash
# Make the active row routable for customers (visibility public + status active).
# This is publishing, not verifying — skip it when you're only testing.
usvc_seller services set-visibility public --local-ids --yes
usvc_seller services submit --local-ids --yes
usvc_seller services list --local-ids   # confirm visibility/status flipped
```

### Selector grammar (positional NAME)

All `specs` and `services` commands that accept a service selector take a **positional NAME** that fnmatches against `service_name` (= `listing.name`, unitysvc#1138). The grammar is intentionally restricted so it maps cleanly onto the backend's SQL `ILIKE`:

| Form | Meaning |
|---|---|
| `cohere/command-r-plus` | exact name |
| `cohere/*` or `cohere/%` | provider scope (every service under `cohere/`) |
| `*-byok` or `%-byok` | suffix (every variant tagged `-byok`) |
| `*command*` or `%command%` | substring |
| omit (no positional) | every service under `specs/` (for `specs` commands) |

**`%` is a synonym for `*`** and the recommended interactive form — shells glob-expand `cohere/*` against the local filesystem and force you to quote it (`'cohere/*'`), but `cohere/%` is shell-safe.

Wildcards are only allowed at the **start, end, or both**. `?`, `[…]`, and mid-pattern wildcards like `cohere/com*and` are rejected — by design, so the grammar stays predictable.

For `services` subcommands that operate on **one** specific row (e.g. `services show`, `services update`, single-service `services run-tests`), if the positional NAME matches multiple rows (an active service plus its pending revision is the common case), the command errors and asks for **`--id <prefix>`** to disambiguate:

```bash
usvc_seller services run-tests --id 6c55d6d9 --force
```

### Why the pipeline order matters

If step 3 (`specs run-tests`) passes but step 5 (`services run-tests`) fails, the upstream is healthy but the *gateway routing* or *svcpass attribution* is broken — that's almost always a wrong `user_access_interfaces.<iface>.base_url` (must use `{{ service_name }}`, see `unitysvc-sellers/docs/naming-conventions.md`) or a misconfigured `api_key` disposition (`unitysvc/unitysvc#1198` — unset/empty/`__strip__`/`__forward__`/literal).

To upload a single service in isolation (faster than uploading the whole repo):

```bash
usvc_seller specs upload <name>
```

Do not declare a service done until you have actually run all four steps (`specs validate`, `specs format`, `specs run-tests`, `services run-tests`) and they all returned green. "It looks right" or "validate passed" alone has bitten this workflow more than once. The `specs run-tests` Python examples may fail with `ModuleNotFoundError: No module named 'requests'` if the test runner picks the system Python instead of the active venv (the workspace venv lives at `~/unitysvc/.venv` on this system — `source ~/unitysvc/.venv/bin/activate` before running) — that's a unitysvc-sellers runner issue, not your service data; if shell + connectivity tests pass, treat the Python failure as environmental.

## 6. Templates + param files — when you have a collection

If the repo hosts many similar services (every model from a provider, every notification channel, …), do NOT hand-write each `offering.json` / `listing.json`. Author each service as a small **param file** that an in-repo template renders. Two layers:

```
templates/
└── <template-name>/                 # e.g. default, notify-relay, msg-to-channel
    ├── provider.json                # copied into each rendered service
    ├── offering.json.j2             # rendered per param file
    ├── listing.json.j2
    └── config.json                  # optional: {"services_populator": {"command": ["scripts/update_params.py"], "requirements": [...]}}
specs/<provider>/
├── <name>.json                      # {"template": "<template-name>"?, "parameters": {…}}   ← template omitted ⇒ the templates/ root
└── <name>.service.json              # identity sidecar (service_id)
```

- **Render is ephemeral.** `materialized_param_specs` (`unitysvc_sellers.params_render`) expands every param file into a temp folder (via `populate_from_iterator`) for the duration of a `specs` command, then removes it and round-trips `service_id` to the sidecar. Commit param files, not rendered folders.
- **Path-derived render vars.** The SDK injects `service_name` = `name` = the **full** `<provider>/<bare>` (from the file path) and `provider_name` (the first segment) into the template — **do not put these in `parameters`** (they shadow + drift). Need the bare name in the template? Pass your own param (e.g. `channel_name`) and build `offering.name = {{ channel_name }}`, `listing.name = "<provider>/{{ channel_name }}"`.
- **Two ways to produce the param files:**
  - **Hand-write** them — the common case for a fixed catalog (e.g. notification channels): adding a service is adding one param file.
  - **Generate** them from a live source — put a populator in `templates/<name>/config.json` (`services_populator`) and run `usvc_seller specs populate`; the script calls `write_params_from_iterator(...)`. Reference: `~/unitysvc/unitysvc-services-cohere` (fetches Cohere's model list → one param file per model).
- **System templates** (defined platform-side, not a local `templates/` dir) are created with `usvc_seller params instantiate <name> -P key=value`; `usvc_seller params list/show` browse them.

**Critical Jinja escaping rule.** The template's Jinja runs at *render* time and resolves the param/path vars (`{{ channel_name }}`, `{{ provider_name }}`). The gateway's Jinja is a *separate, later* pass that resolves from the live service row (`{{ service_name }}`, `{{ enrollment.code }}`, `{{ params.* }}`). For a gateway-time variable to survive the render pass, wrap it in `{% raw %}…{% endraw %}`:

```jinja
"base_url": "${API_GATEWAY_BASE_URL}/{% raw %}{{ service_name }}{% endraw %}"
```

Without the wrapper the render emits an empty string or raises `UndefinedError`; symptom in production: every regenerated listing has a broken base_url. (Param string *values* you pass in — e.g. `${ customer_secrets.{{ params.X }} }` — are emitted literally by `| tojson` and need no `{% raw %}`; only gateway-time Jinja written in the template *source* does.)

## 7. Connectivity test is mandatory — every service, no exceptions

The platform considers a service untestable (and therefore unfit to activate) without at least one connectivity test. The connectivity test is a `document` of category `connectivity_test`. Two ways to provide it:

**Preset** — use a `$doc_preset` from `unitysvc-data`. The preset library covers common cases (`llm_connectivity`, `api_connectivity`, `notify_relay_connectivity_<ch>`, `apprise_notify_connectivity_<ch>`, etc.). Browse via `python3 -c "from unitysvc_data.presets import list_presets; print(list_presets())"` or look at how the demo services do it (`cat ~/unitysvc/unitysvc-services-demo/specs/unitysvc-demo/llm/listing.json`).

```json
"documents": {
  "Connectivity test": {
    "$doc_preset": "llm_connectivity"
  }
}
```

**Local Jinja file** — when the upstream needs a custom probe (synthetic gateway services, exotic auth, multi-step handshake). Put `connectivity.sh.j2` (or `.py.j2`, `.js.j2`) under the service dir; reference it in the listing's `documents`:

```json
"Connectivity test": {
  "category": "connectivity_test",
  "file_path": "connectivity.sh.j2",
  "is_active": true,
  "is_public": false,
  "meta": { "output_contains": "ok" },
  "mime_type": "bash"
}
```

`meta.output_contains` (and friends) lets the test runner accept a successful run on a string match rather than just `exit 0`.

## 8. Tests must run in both modes — local upstream AND gateway

`usvc_seller specs run-tests` renders templates pointing at the *upstream directly*; `usvc_seller services run-tests` renders the *same templates* pointing at the gateway URL. A test written for only one mode fails the other. The platform handles this with a `localtesting` flag exposed to the Jinja context:

```jinja
{# connectivity.sh.j2 #}
{% if localtesting %}
curl -sS "{{ upstream_base_url }}/healthz" \
  -H "Authorization: Bearer {{ HTTP_RELAY_API_KEY }}"
{% else %}
curl -sS "${SERVICE_BASE_URL}/healthz" \
  -H "Authorization: Bearer $UNITYSVC_API_KEY"
{% endif %}
echo "ok"
```

Rules of thumb:
- The `localtesting=true` branch uses the *real* upstream URL and the *seller's* upstream credential. It's the "is the upstream alive?" probe.
- The `localtesting=false` branch uses the gateway's `SERVICE_BASE_URL` and the customer's `UNITYSVC_API_KEY` (svcpass). It's the "does the gateway route + auth + forward correctly?" probe.
- If the only difference is the base URL and auth header, you can often skip the `if/else` and just reference the env vars — the test runner provides different values in each mode. The demo services and `unitysvc-services-notify/validation/` hold minimal env-var-driven probes.

When a test fails only in gateway mode, suspect: wrong base_url shape (must use `{{ service_name }}` or be a bare top-level handle), wrong `api_key` disposition, or the service hasn't been re-uploaded since the data file changed.

## 9. End-to-end checklist for a new service

When the user says "add a service to repo X":

1. **Identify the closest pattern** — `ls ~/unitysvc/unitysvc-services-demo/specs/unitysvc-demo/` and pick one. Copy `offering.json`, `listing.json` into a `specs/<provider>/<name>/` folder in the target repo as a starting point.
2. **Decide concrete vs. param-file** — one service: hand-write the `specs/<provider>/<name>/` folder. A collection of similar services: set up a `templates/<name>/` + param files first (§6).
3. **Fill in the offering** — name, service_type, capabilities, upstream_access_config, payout_price. Cross-check against `unitysvc-sellers/docs/file-schemas.md` for field semantics. **For secret references:** put sensitive values behind `${ customer_secrets.<NAME> }` with a service-specific prefix (`SMTP_RELAY_HOST`, not bare `SMTP_HOST`); put operational config in direct params or as literal fields with `?? default` fallbacks. See **§11**.
4. **Fill in the listing** — name (per `naming-conventions.md`), list_price (per `pricing.md`), user_access_interfaces base_url (`${API_GATEWAY_BASE_URL}/{{ service_name }}` for normal services; bare top-level for platform-internal), documents block. **For `-plus` services**: `ops_testing_parameters` holds literal values (host, port, etc.); only `*_secret` keys name a seller secret. `user_parameters_schema` `*_secret` defaults point at the non-plus literal name. See **§11**.
5. **Add the connectivity test** — preset if a stock one fits; local Jinja file otherwise. Make sure it handles both `localtesting` modes if it isn't purely env-var-driven.
6. **Validate, format** — fix anything `usvc_seller specs validate` complains about; `usvc_seller specs format` to canonicalize.
7. **Local run-tests** — `usvc_seller specs run-tests <name>` against the live upstream.
8. **Upload** — `usvc_seller specs upload <name>` to staging. If this fails with `ValueError: Customer secret 'X' … requires a seller secret with the same name`, seed it: `usvc_seller secrets set X --value <v>` and retry. (In CI, the seed-secrets workflow step handles this automatically — see **§11**.)
9. **Services run-tests** — `usvc_seller services run-tests <name> --force` through the gateway. No visibility / submit step needed: the test runner authenticates as the seller and can route freshly-uploaded draft/pending revisions. Add `--id <prefix>` only if the name matches more than one row *and* you want to scope to one.
10. **Only after all four green:** report "ready". If anything failed, fix the underlying issue (don't skip the step) and re-run from the failing point. **Publishing** the service to customers (`set-visibility public` + `submit`) is a separate, explicit action — not part of verification.

## 10. Common failure modes and where to look

| Symptom | Likely cause | Where to look |
|---|---|---|
| `validate` fails with "base_url must route by service identifier" | Literal `<provider>/<service>` path in user_access_interfaces | `unitysvc-sellers/docs/naming-conventions.md` — switch to `${API_GATEWAY_BASE_URL}/{{ service_name }}` |
| `validate` fails with "listing name … first segment must be the provider slug" | Namespaced name doesn't match provider | Rename to `<provider-slug>/<bare>` or use a bare top-level name |
| `specs run-tests` succeeds, `services run-tests` 404s | Service not yet uploaded, or uploaded under a different name | Re-run `usvc_seller specs upload <name>` and check `usvc_seller services list <name>` |
| Gateway returns 401 with "Missing svcpass API key" | Customer not authenticated; case-sensitive `Bearer` required | `Authorization: Bearer <svcpass_…>` (capital B) or `x-api-key: …` |
| Test passes locally but fails in CI | Template uses generator-time Jinja for a runtime variable | Wrap in `{% raw %}…{% endraw %}` (see Section 4) |
| Re-upload creates a draft revision instead of in-place update | Renamed `listing.name` or changed routing-affecting fields — backend treats as content change and queues admin review | Expected. Submit the revision: `usvc_seller services submit --local-ids` |
| `specs upload` fails with `ValueError: Customer secret 'X' … requires a seller secret with the same name for testing` | Every `${ customer_secrets.X }` reference in a listing/offering needs a same-named seller secret in *your* seller-secrets store, because the platform's gateway-side tests plug in a real value | Seed it: `usvc_seller secrets set X --value <v>` locally, or via the CI seed-secrets workflow step that auto-derives names from `specs/`. See **§11**. |
| `specs upload` fails with `[Errno 21] Is a directory: '.../<other-service>'` | A description / tutorial markdown contains a relative link to a sibling **directory** like `[label](../smtp-to-msg/)`. The uploader's markdown scanner picks up local refs as S3 assets and `open()` blows up on the directory | Replace directory-target links with prose, or point them at a specific file inside the sibling (e.g. `../smtp-to-msg/msg-description.md`). |
| `validate` fails: "listing name 'X' does not match the folder path 'P'" | `listing.name` isn't `<provider>/<bare>` matching the folder under `specs/` | Set `listing.name` = the folder path; keep `offering.name` bare (§2) |

## 11. Secrets, parameters, and ops_testing wiring

Service definitions reference customer-supplied values through one of three forms — knowing which is which avoids the two most common upload-time errors.

### Upstream access channels (the `upstream_access_config` entries)

Each named entry in `upstream_access_config` is an **upstream access channel** — one complete way for the gateway to reach the upstream (`access_method` + `base_url` + `api_key` + `routing_key` + `rate_limits`). Names are free-form (`managed`, `byok`, `plus`). Its **`channel_type`** is *derived from the channel's own config*, never hand-labelled:

- `managed` — seller's key, `${ secrets.* }`
- `byok` — customer's key `${ customer_secrets.* }`, static endpoint
- `byoe` — customer's key **and** a customer-templated `base_url`
- `enrollable` (the **`plus`** channel) — references `{{ params.* }}` / `{{ enrollment.* }}` (precedence over byok/byoe); the customer binds it per enrollment and reaches it at `/e/<code>`

One offering may expose several channels; the gateway picks one per request (by customer-secret satisfiability, `routing_key` match, or the `_channel=<name>` selector), and a **channel-keyed `list_price`** (`"type": "channel"`, with a `default`) prices each separately — see `docs/pricing.md`. The headline pattern (#1305): a free open channel (`byok`/`managed`) **co-exists** with a paid enrollable `plus` channel on one listing — a canonical request is served by the open channel, while each `plus` enrollment is reached at `/e/<code>`. See the `multi-channel` demo and `unitysvc-services-http/specs/http-relay`.

Orthogonal to channels are **user access interfaces** (`user_access_interfaces`, the downstream URLs customers connect to). Conventions: name the single static-URL interface **`canonical`** (`${API_GATEWAY_BASE_URL}/{% raw %}{{ service_name }}{% endraw %}`) — don't invent a per-service name; and do **not** declare a separate `enrollment` interface — the platform's `/e/<code>` already reaches enrollments and binds their params, and the service stays `enrollment_required` via its required `user_parameters_schema` params. A channel is *how a request is fulfilled & billed* (gated by secrets); an interface is *how you connect* (gated by enrollment) — they pair freely, not as a matrix.

### Three shapes a reference can take

```text
${ customer_secrets.<NAME> }              ← literal customer-secret reference
${ customer_secrets.{{ params.<X> }} }    ← per-enrollment customer-secret reference (-plus services)
{{ params.<X> }}                          ← direct enrollment parameter (no secret indirection)
```

The first is for **fixed-name secrets** every customer of the service supplies under the same name (e.g. `HTTP_RELAY_BASE_URL` on the free single variant). The second is the multi-enrollment indirection: the customer names the secret at enrollment time via the `<X>_secret` parameter, value resolved at request time. The third is for **non-sensitive operational config** — a URL, port, hostname, flag — that doesn't need to live in the secrets store.

**Decision rule:** anything sensitive (password, API key, bearer token) goes through `customer_secrets`. Anything operational (host, port, tls flag, plain destination URL) is a direct parameter with a default. Don't put a URL behind `customer_secrets` just because someone wanted "the same indirection for everything" — that's how an op URL ends up needing a seller-secret seed at upload time when a literal param would suffice.

### Every `${ customer_secrets.<NAME> }` needs a same-named seller secret on the platform

The upload validator rejects a listing whose `${ customer_secrets.X }` references don't have a same-named seller secret in *your* seller-secrets store. This is because the platform's gateway-side tests plug in a real value for the synthetic test enrollment. Two ways to satisfy it:

- **Locally** (one-off): `usvc_seller secrets set <NAME> --value <value>` against staging or production.
- **In CI** (the right answer at scale): the seed-secrets workflow step — grep `${ customer_secrets.X }` and `${ secrets.X }` out of `specs/`, look up each name in `toJSON(secrets)`, call `usvc_seller secrets set <NAME>` before `specs upload`. Auto-derive from the spec files; don't hand-maintain a manifest — it drifts. Reference implementation: `unitysvc-services-http/.github/workflows/upload-to-staging.yml` "Seed seller-secrets store".

Optional references with `?? ` fallback (e.g. `${ customer_secrets.HTTP_RELAY_API_KEY ?? }`) don't strictly require the seller-secret to exist, but the seed step will `::warning::` + skip them if unset, which is fine.

### Point the upstream host at the mock for testing — the ops-customer → seller-secret fallback

To make a service reach the **mock** (`mock.unitysvc.dev`) during testing but the **real provider** in production — on one platform, no staging/production split — route the upstream host (or base URL) through a `customer_secrets` reference whose `??` default is the real provider, then seed a same-named **seller** secret pointing at the mock:

```text
base_url = ${ customer_secrets.<SVC>_BASE_URL ?? https://api.realprovider.com }/...
```

It resolves to the right host in each context because, for the synthetic **ops_customer** the gateway uses in its tests, a missing `${ customer_secrets.X }` **falls back to your seller-secrets store** (`backend/app/core/route_mapping.py` — "customer_secrets … not found for ops_customer, falling back to seller secrets"):

- **Production** — a normal customer hasn't set `<SVC>_BASE_URL`, so the `??` default (the real provider) is used. A customer running their own provider-compatible proxy may set it to point there.
- **Gateway-side tests** — the ops_customer hasn't set it either, so the gateway falls back to **your** seller secret. Seed it to the mock: `usvc_seller secrets set <SVC>_BASE_URL --value https://mock.unitysvc.dev/<svc>/...`. Only ops-customer (test) traffic resolves to the mock; production customers are untouched.
- **Local upstream tests** — the runner reads `<SVC>_BASE_URL` from the environment; export it to the mock host.

This is the **one** justified exception to the "operational URLs are direct params, not `customer_secrets`" rule above (§ *Three shapes a reference can take*): the indirection is precisely what buys the ops-customer→seller-secret fallback, so *you* own the mock/real switch from your seller-secrets store and never touch the service definition to test it. Do **not** use a seller-scope `${ secrets.X }` reference for the host — a seller secret is global, so a mock value would route *production* traffic to the mock too.

### Namespace your customer-secret names

`SMTP_HOST` and `SMTP_PASSWORD` are too generic — they'll collide the moment a second SMTP-flavored service appears under the same customer. Use a service-specific prefix:

- `SMTP_RELAY_HOST` / `SMTP_RELAY_PASSWORD` — for `smtp-relay`
- `HTTP_RELAY_BASE_URL` / `HTTP_RELAY_API_KEY` — for `http-relay`
- `<PROVIDER>_API_KEY` — for upstream-provider services (`ANTHROPIC_API_KEY`, `COHERE_API_KEY`, …)

The seed-secrets CI step grep-matches against bare names, so collisions are silent bugs. Pick the namespace once when the service is created.

### `ops_testing_parameters` shape — literals, not template refs

For `-plus` (multi-enrollment) services, `service_options.ops_testing_parameters` defines the synthetic enrollment the platform uses for gateway tests. The values are **literals** — what the platform plugs in directly — except for one special case:

```json
"ops_testing_parameters": {
  "host":            "mailpit.svcmarket.com",
  "port":            1025,
  "username":        "",
  "tls":             false,
  "password_secret": "SMTP_RELAY_PASSWORD"     ← ONLY this names a seller secret
}
```

- All non-`_secret` keys are **literal values** of the right type (string / int / bool). Do **not** wrap them in `${ customer_secrets.X }` — that's the wrong primitive, even though the platform may resolve it at upload time by accident.
- Keys ending in `_secret` (`password_secret`, `api_key_secret`) name a seller secret. The platform looks up the value at test time. Default them to the corresponding non-plus service's literal secret name (e.g. `SMTP_RELAY_PASSWORD`, `HTTP_RELAY_API_KEY`).

### `-plus` `user_parameters_schema` defaults

Same convention in the customer-facing parameter schema:

- Non-secret params (`host`, `port`, `username`, `tls`, `base_url`) get **direct literal defaults** of the right type.
- `*_secret` params **default to the non-plus literal secret name**. This makes an empty-params enrollment work out of the box against the seller-seeded fixture, and the seed-secrets grep over the non-plus offering picks the name up transparently — no per-enrollment fix-up needed for the common case.

```json
"user_parameters_schema": {
  "type": "object",
  "required": [],
  "properties": {
    "host":            { "type": "string",  "default": "mailpit.svcmarket.com" },
    "port":            { "type": "integer", "default": 1025 },
    "tls":             { "type": "boolean", "default": false },
    "username":        { "type": "string",  "default": "" },
    "password_secret": { "type": "string",  "default": "SMTP_RELAY_PASSWORD" }
  }
}
```

### Markdown links to sibling services — never bare directories

The uploader's markdown scanner extracts every local href (anything containing `/`) and tries to upload it to S3. A link like `[label](../smtp-to-msg/)` resolves to a *directory*, the uploader calls `open()` on it, and the whole offering fails with `[Errno 21] Is a directory`. Two safe forms:

- **Prose** (recommended for "switch to X" pointers): `the smtp-to-msg service` — no link at all.
- **File-specific link** (when navigation is genuinely useful): `[smtp-to-msg](../smtp-to-msg/msg-description.md)` — targets a real file.

Never `[label](../sibling/)` with a trailing slash.

## 12. When to ask the user vs. proceed

- **Proceed without asking** if the closest demo pattern is obvious and the user gave a specific service name + behavior.
- **Ask the user** about: list_price shape (constant vs. token-based vs. revenue_share); whether the service needs a routing_key.model (most LLMs do, some don't); whether customer secrets are required (BYOK / BYOE) or seller-supplied (managed). Don't invent these — pricing and auth model are commercial decisions, not technical ones.
