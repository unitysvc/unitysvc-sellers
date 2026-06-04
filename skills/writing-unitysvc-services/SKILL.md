---
name: writing-unitysvc-services
description: Author UnitySVC service data files (offering.json + listing.json + connectivity test + optional code examples), set up the iterator+template pattern when a repo will host many similar services, and drive each service through the validate → format → data-tests → gateway-tests → upload pipeline. Use this skill whenever the user wants to add, modify, regenerate, or troubleshoot a service in a `unitysvc-services-*` repo, or asks for help writing an `offering.json` / `listing.json` / `listing.json.j2`, even if they don't name the skill explicitly. Also use when they mention connectivity tests, BYOK / BYOE patterns, gateway base_urls, customer secrets, or `usvc_seller data` / `usvc_seller services` commands. The skill is **rigid** about the verification order (a service is not "ready" until validate, format, data run-tests, AND services run-tests all pass) and about the connectivity-test requirement (every service must have at least one).
---

# Writing UnitySVC Services

A UnitySVC service is two pieces of declarative data — an **offering** (technical spec: upstream URL, auth, capabilities, payout) and one or more **listings** (customer-facing: gateway path, list price, docs) — plus tests that prove the upstream and the gateway actually work. This skill is the workflow for going from "we want a new service" to "the service is live on staging and a curl through the gateway returns 200."

The skill assumes the local repos under `~/unitysvc/` are checked out and writable, and that `usvc_seller` is installed (via `uvx --from unitysvc-sellers usvc_seller …` if not on PATH).

**Environment for staging access.** Anything that talks to the staging backend (`usvc_seller data upload`, `usvc_seller services list/show/run-tests`, manual `curl https://api.staging.svcpass.com/…`) needs the seller API key and URL in env. Source `~/.zshrc` first:

```bash
zsh -ic 'source ~/.zshrc && usvc_seller services list'
# or, when starting an interactive session:
source ~/.zshrc
```

`~/.zshrc` defines `UNITYSVC_SELLER_API_KEY`, `UNITYSVC_SELLER_API_URL` (= `https://seller.staging.unitysvc.com/v1/`), and `UNITYSVC_API_KEY` (the same svcpass key used to authenticate as a customer to the gateway). If a command returns 401 or "Missing svcpass API key", you forgot to source.

## 1. Find the right pattern first — don't write blind

The single highest-leverage move when starting a new service is to **find an existing service that already works and copy its shape**. The canonical catalog of patterns lives in [`unitysvc-services-demo`](https://github.com/unitysvc/unitysvc-services-demo). Each subdirectory under `data/unitysvc-demo/services/` is a minimal working example of one delivery pattern. The table in `data/README.md` maps patterns to use cases:

| Pattern | When the user wants … |
|---|---|
| `relay` | minimal seller-managed HTTP upstream, no auth |
| `llm` | OpenAI-compatible LLM with token pricing |
| `byok` | customer brings their own API key |
| `byoe` | customer brings both endpoint URL and key |
| `params` | per-enrollment routing key from a user parameter |
| `byoe-params` | parameterized customer-secret *names* |
| `enrollment_vars` | per-enrollment URL fragment (e.g. unique codes) |
| `recurrent` | scheduled / recurrence service |
| `routing_vars` | seller knobs editable after activation |
| `s3` / `s3-byoe` / `s3-byoe-params` | S3 gateway variants |
| `smtp` / `smtp-byoe` / `smtp-byoe-params` | SMTP gateway variants |
| `transformer` / `notification` / `relay` | composition / forwarder patterns |

**Concrete instruction:** before drafting any file, `ls ~/unitysvc/unitysvc-services-demo/data/unitysvc-demo/services/` and `cat` the closest match's `offering.json` + `listing.json`. Copy fields you don't yet understand verbatim; you can simplify later. The schemas allow extra fields and reject missing required ones — having too much from a working example is safer than too little from your imagination.

When the closest demo is itself not enough — e.g. provider-specific routing oddities — look at a real production repo that ships the same shape:
- LLM with BYOK: `~/unitysvc/unitysvc-services-anthropic` / `…-cohere` / `…-deepseek`
- LLM with multi-variant listings: `~/unitysvc/unitysvc-services-parasail` (hierarchical model names)
- HTTP relay / gateway loopback: `~/unitysvc/unitysvc-services-http`
- S3 / SMTP / direct-response: `~/unitysvc/unitysvc-services-s3` / `…-smtp` / `…-resp`

## 2. File organization rules

The SDK discovers data files by their `schema` field, not by filename — but the *directory structure* is load-bearing. The relationship between provider, offering, and listing is determined entirely by location. Get this wrong and the upload either fails or quietly groups things into the wrong service.

### Canonical layout

```
data/
└── <provider-slug>/                       # Provider directory — name MUST equal provider.name
    ├── provider.{json,toml}               # Required: exactly one provider_v1 file
    ├── README.md                          # Optional: provider description
    ├── docs/                              # Optional: shared docs / code examples / templates
    │   ├── description.md
    │   ├── code-example.py.j2
    │   └── connectivity.sh.j2
    ├── scripts/                           # Optional: iterator (update_services.py) for generated repos
    ├── templates/                         # Optional: Jinja2 templates for the iterator pattern
    └── services/                          # Required: services live here, one subdir per service
        └── <service-slug>/
            ├── offering.json|.toml        # Required: exactly one offering_v1 file
            ├── listing.json|.toml         # Required: one or more listing_v1 files
            ├── listing.override.json      # Auto-written by upload — commit it
            └── <service-specific docs>    # Optional: docs referenced only by this listing
```

### Hard rules — validator/uploader will reject violations

1. **Provider directory name must equal `provider.name`.** The validator rejects mismatches. Renaming the provider means renaming the directory in the same commit.
2. **The path must include a `services/` segment.** That's how the SDK resolves the parent provider for an offering. Putting offerings directly under `<provider>/` (no `services/`) breaks the upload.
3. **Exactly one `offering_v1` file per service directory.** Multiple offerings in one directory is ambiguous — the SDK reports "Multiple offering_v1 files found".
4. **At least one `listing_v1` file per service directory** (you can have several — pricing tiers, variant tags).
5. **Files are discovered by schema, not name.** Any filename works as long as the `schema` field matches. But sticking to convention (`offering.json`, `listing.json`, `listing-<variant>.json`) is what humans expect.
6. **External files referenced by relative path.** `docs/code-example.py.j2` in a listing's `documents` block resolves relative to the listing file's directory; `../../docs/foo.j2` lets multiple services share one file.

### Service identity is derived, not declared

A backend **Service** is the identity record. Its `name`, `display_name`, and `status` are derived at upload time:

- `service.name` ← `listing.name`, falling back to `offering.name` if `listing.name` is unset. *(Per PR #1196 the explicit `listing.name` is now required at ingest; the fallback path is going away.)*
- `service.display_name` ← `listing.display_name` → `offering.display_name` → `listing.name` → `offering.name` (first non-empty wins).
- `service.status` ← worst-of the component statuses: any `draft` → service draft (upload skipped); any `deprecated` (no draft) → deprecated; all `ready` → progresses through review.

### Override files — the service_id lifecycle

`listing.override.json` is auto-written by `usvc_seller data upload` after the first successful upload. It carries the `service_id` (and a server-resolved `name`) so subsequent uploads target the existing service rather than creating a new one. Treat it as:

- **Committed to version control** — links your local data to a specific service in staging/prod.
- **Never hand-edited** unless you explicitly want to re-upload as a brand-new service (delete the override file in that case).
- **Environment-specific** — if you upload to both staging and production, the two override files differ. Manage via separate branches or separate data dirs (the SDK only supports one override per base file).

The override mechanism is generic: any `<base>.override.<ext>` is deep-merged onto the base file at load time. Useful for sellers who auto-generate listings but want to hand-curate a few fields (status, custom logo URL).

### Multiple listings per offering

When one offering ships in multiple variants (basic / premium / `@byok` / `@byop` / per-marketplace), put each listing as a separate file in the same service directory:

```
data/cohere/services/command-r-plus/
├── offering.json
├── listing-byok.json     # name: "command-r-plus@byok"
└── listing-byop.json     # name: "command-r-plus@byop"
```

The filename stem (without `.override`) becomes the implicit `name` if the listing file omits it. Convention: set `name` explicitly — easier to track when reading.

## 3. Naming conventions (listings, services, gateway paths)

The validator at `usvc-core` runs on every `usvc_seller data validate` and rejects non-conformant catalogs *before* upload. Three places where naming matters:

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
✓ ${API_GATEWAY_BASE_URL}/{{ service_name }}/{{ enrollment_vars.code }}
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

- `data-structure.md` — directory layout, file roles, override files
- `file-schemas.md` — every field on `offering_v1`, `listing_v1`, `provider_v1`
- `pricing.md` — `list_price` / `payout_price` shapes (constant, one_million_tokens, revenue_share, etc.) — go here BEFORE inventing a pricing block
- `service-types.md` — when to pick `llm` / `proxy` / `gateway` / `embedding` / etc.
- `naming-conventions.md` — listing.name grammar, `@variant` tags, provider-slug rule
- `documenting-services.md` — how `documents` blocks work (presets, file paths, connectivity tests)
- `cli-reference.md` — full `usvc_seller` command surface
- `workflows.md` — GitHub Actions integration for upload-on-merge

When something in this skill conflicts with the docs, the docs win — they evolve with the platform.

## 5. The verification pipeline — a service is not "ready" until all four pass

The user's working definition of "ready": **validate, format, data run-tests, AND services run-tests all green.** Skipping any step risks a silent breakage upstream. Run them in order; each catches a different class of mistake:

```bash
# 1. Schema + cross-file validation (fast, no network).
#    Always runs on every service in the current directory.
usvc_seller data validate

# 2. JSON/TOML canonical formatting (writes in-place; commit the result).
#    Always runs on every service in the current directory.
usvc_seller data format

# 3. Upstream-side tests: render and execute the connectivity / code-example
#    docs against the upstream URL directly (no gateway). Catches dead
#    upstreams, wrong base_urls, broken auth before the gateway sees them.
#    NAME is a restricted glob — see "Selector grammar" below.
usvc_seller data run-tests <name>

# 4. Upload to staging so the gateway has a route to test against.
#    A re-upload of an existing service creates a *revision* (admin-review
#    queue) rather than mutating the active row in place — that's expected.
usvc_seller data upload <name>

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

All `data` and `services` commands that accept a service selector take a **positional NAME** that fnmatches against `service_name` (= `listing.name`, unitysvc#1138). The grammar is intentionally restricted so it maps cleanly onto the backend's SQL `ILIKE`:

| Form | Meaning |
|---|---|
| `cohere/command-r-plus` | exact name |
| `cohere/*` or `cohere/%` | provider scope (every service under `cohere/`) |
| `*-byok` or `%-byok` | suffix (every variant tagged `-byok`) |
| `*command*` or `%command%` | substring |
| omit (no positional) | every service in the current directory (for `data` commands) |

**`%` is a synonym for `*`** and the recommended interactive form — shells glob-expand `cohere/*` against the local filesystem and force you to quote it (`'cohere/*'`), but `cohere/%` is shell-safe.

Wildcards are only allowed at the **start, end, or both**. `?`, `[…]`, and mid-pattern wildcards like `cohere/com*and` are rejected — by design, so the grammar stays predictable.

For `services` subcommands that operate on **one** specific row (e.g. `services show`, `services update`, single-service `services run-tests`), if the positional NAME matches multiple rows (an active service plus its pending revision is the common case), the command errors and asks for **`--id <prefix>`** to disambiguate:

```bash
usvc_seller services run-tests --id 6c55d6d9 --force
```

### Why the pipeline order matters

If step 3 (`data run-tests`) passes but step 5 (`services run-tests`) fails, the upstream is healthy but the *gateway routing* or *svcpass attribution* is broken — that's almost always a wrong `user_access_interfaces.<iface>.base_url` (must use `{{ service_name }}`, see `unitysvc-sellers/docs/naming-conventions.md`) or a misconfigured `api_key` disposition (`unitysvc/unitysvc#1198` — unset/empty/`__strip__`/`__forward__`/literal).

To upload a single service in isolation (faster than uploading the whole repo):

```bash
usvc_seller data upload <name>
```

Do not declare a service done until you have actually run all four test steps (validate, format, data run-tests, services run-tests) and they all returned green. "It looks right" or "validate passed" alone has bitten this workflow more than once. The `data run-tests` Python examples may fail with `ModuleNotFoundError: No module named 'requests'` if the test runner picks the system Python instead of the active venv (the workspace venv lives at `~/unitysvc/.venv` on this system — `source ~/unitysvc/.venv/bin/activate` before running) — that's a unitysvc-sellers runner issue, not your service data; if shell + connectivity tests pass, treat the Python failure as environmental.

## 6. Iterator + template pattern — when you have a collection

If the repo will host many similar services (every model from a provider, every region of an S3 endpoint, etc.), do NOT hand-write each `offering.json` / `listing.json`. The pattern is:

```
data/<provider>/
├── scripts/
│   └── update_services.py       # iterator: yields per-service Jinja contexts
├── templates/
│   ├── offering.json.j2         # rendered per item from the iterator
│   └── listing.json.j2          # rendered per item from the iterator
└── services/                    # populated by `update_services.py`
    └── <generated dirs>/
```

The script imports `populate_from_iterator` from `unitysvc_sellers.template_populate`, builds a per-service dict (`provider_name`, `offering_name`, `display_name`, capabilities, pricing, etc.), and the template renders that dict. Real examples in `~/unitysvc/unitysvc-services-anthropic/data/anthropic/scripts/update_services.py` and `…/templates/listing.json.j2`. Cross-reference with `~/unitysvc/unitysvc-services-cohere`, `~/unitysvc/unitysvc-services-mistral`, `~/unitysvc/unitysvc-services-ollama` for variations.

**Critical Jinja escaping rule** — the template's Jinja runs at generate-time and resolves variables from the script's context (`{{ provider_name }}`, `{{ offering_name }}`, etc.). The gateway's runtime Jinja is a *different pass* that resolves later from the live service row (`{{ service_name }}`, `{{ enrollment_vars.code }}`, etc.). For runtime Jinja to survive the generator pass, wrap it in `{% raw %}…{% endraw %}`:

```jinja
"base_url": "${API_GATEWAY_BASE_URL}/{% raw %}{{ service_name }}{% endraw %}"
```

Without the wrapper, the generator either renders an empty string or raises `UndefinedError` depending on the Jinja env. Symptom in production: every regenerated listing has a broken base_url after a sync run.

## 7. Connectivity test is mandatory — every service, no exceptions

The platform considers a service untestable (and therefore unfit to activate) without at least one connectivity test. The connectivity test is a `document` of category `connectivity_test`. Two ways to provide it:

**Preset** — use a `$doc_preset` from `unitysvc-data`. The preset library covers common cases (`llm_connectivity`, `llm_connectivity_anthropic`, `llm_connectivity_embed`, `api_connectivity`, etc.). Browse via `python3 -c "from unitysvc_data.presets import list_presets; print(list_presets())"` or look at how the demo services do it (`cat ~/unitysvc/unitysvc-services-demo/data/unitysvc-demo/services/llm/listing.json`).

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

`usvc_seller data run-tests` renders templates pointing at the *upstream directly*; `usvc_seller services run-tests` renders the *same templates* pointing at the gateway URL. A test written for only one mode fails the other. The platform handles this with a `localtesting` flag exposed to the Jinja context:

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
- If the only difference is the base URL and auth header, you can often skip the `if/else` and just reference the env vars — the test runner provides different values in each mode. Look at `~/unitysvc/unitysvc-services-resp/data/unitysvc/docs/connectivity.sh.j2` for a minimal example.

When a test fails only in gateway mode, suspect: wrong base_url shape (must use `{{ service_name }}` or be a bare top-level handle), wrong `api_key` disposition, or the service hasn't been re-uploaded since the data file changed.

## 9. End-to-end checklist for a new service

When the user says "add a service to repo X":

1. **Identify the closest pattern** — `ls ~/unitysvc/unitysvc-services-demo/data/unitysvc-demo/services/` and pick one. Copy `offering.json`, `listing.json` into the target repo as a starting point.
2. **Decide single vs. iterator** — if this is one service, hand-edit. If part of a collection of >5 similar services, set up `scripts/update_services.py` + `templates/*.j2` first.
3. **Fill in the offering** — name, service_type, capabilities, upstream_access_config, payout_price. Cross-check against `unitysvc-sellers/docs/file-schemas.md` for field semantics. **For secret references:** put sensitive values behind `${ customer_secrets.<NAME> }` with a service-specific prefix (`SMTP_RELAY_HOST`, not bare `SMTP_HOST`); put operational config in direct params or as literal fields with `?? default` fallbacks. See **§11**.
4. **Fill in the listing** — name (per `naming-conventions.md`), list_price (per `pricing.md`), user_access_interfaces base_url (`${API_GATEWAY_BASE_URL}/{{ service_name }}` for normal services; bare top-level for platform-internal), documents block. **For `-plus` services**: `ops_testing_parameters` holds literal values (host, port, etc.); only `*_secret` keys name a seller secret. `user_parameters_schema` `*_secret` defaults point at the non-plus literal name. See **§11**.
5. **Add the connectivity test** — preset if a stock one fits; local Jinja file otherwise. Make sure it handles both `localtesting` modes if it isn't purely env-var-driven.
6. **Validate, format** — fix anything `usvc_seller data validate` complains about; `usvc_seller data format` to canonicalize.
7. **Data run-tests** — `usvc_seller data run-tests <name>` against the live upstream.
8. **Upload** — `usvc_seller data upload <name>` to staging. If this fails with `ValueError: Customer secret 'X' … requires a seller secret with the same name`, seed it: `usvc_seller secrets set X --value <v>` and retry. (In CI, the seed-secrets workflow step handles this automatically — see **§11**.)
9. **Services run-tests** — `usvc_seller services run-tests <name> --force` through the gateway. No visibility / submit step needed: the test runner authenticates as the seller and can route freshly-uploaded draft/pending revisions. Add `--id <prefix>` only if the name matches more than one row *and* you want to scope to one.
10. **Only after all four green:** report "ready". If anything failed, fix the underlying issue (don't skip the step) and re-run from the failing point. **Publishing** the service to customers (`set-visibility public` + `submit`) is a separate, explicit action — not part of verification.

## 10. Common failure modes and where to look

| Symptom | Likely cause | Where to look |
|---|---|---|
| `validate` fails with "base_url must route by service identifier" | Literal `<provider>/<service>` path in user_access_interfaces | `unitysvc-sellers/docs/naming-conventions.md` — switch to `${API_GATEWAY_BASE_URL}/{{ service_name }}` |
| `validate` fails with "listing name … first segment must be the provider slug" | Namespaced name doesn't match provider | Rename to `<provider-slug>/<bare>` or use a bare top-level name |
| `data run-tests` succeeds, `services run-tests` 404s | Service not yet uploaded, or uploaded under a different name | Re-run `usvc_seller data upload <name>` and check `usvc_seller services list <name>` |
| Gateway returns 401 with "Missing svcpass API key" | Customer not authenticated; case-sensitive `Bearer` required | `Authorization: Bearer <svcpass_…>` (capital B) or `x-api-key: …` |
| Test passes locally but fails in CI | Template uses generator-time Jinja for a runtime variable | Wrap in `{% raw %}…{% endraw %}` (see Section 4) |
| Re-upload creates a draft revision instead of in-place update | Renamed `listing.name` or changed routing-affecting fields — backend treats as content change and queues admin review | Expected. Submit the revision: `usvc_seller services submit --local-ids` |
| `data upload` fails with `ValueError: Customer secret 'X' … requires a seller secret with the same name for testing` | Every `${ customer_secrets.X }` reference in a listing/offering needs a same-named seller secret in *your* seller-secrets store, because the platform's gateway-side tests plug in a real value | Seed it: `usvc_seller secrets set X --value <v>` locally, or via the CI seed-secrets workflow step that auto-derives names from `data/`. See **§11**. |
| `data upload` fails with `[Errno 21] Is a directory: '.../services/<other-service>'` | A description / tutorial markdown contains a relative link to a sibling **directory** like `[label](../smtp-to-msg/)`. The uploader's markdown scanner picks up local refs as S3 assets and `open()` blows up on the directory | Replace directory-target links with prose, or point them at a specific file inside the sibling (e.g. `../smtp-to-msg/msg-description.md`). |

## 11. Secrets, parameters, and ops_testing wiring

Service definitions reference customer-supplied values through one of three forms — knowing which is which avoids the two most common upload-time errors.

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
- **In CI** (the right answer at scale): the seed-secrets workflow step — grep `${ customer_secrets.X }` and `${ secrets.X }` out of `data/`, look up each name in `toJSON(secrets)`, call `usvc_seller secrets set <NAME>` before `data upload`. Auto-derive from the data files; don't hand-maintain a manifest — it drifts. Reference implementation: `unitysvc-services-http/.github/workflows/upload-to-staging.yml` "Seed seller-secrets store".

Optional references with `?? ` fallback (e.g. `${ customer_secrets.HTTP_RELAY_API_KEY ?? }`) don't strictly require the seller-secret to exist, but the seed step will `::warning::` + skip them if unset, which is fine.

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
