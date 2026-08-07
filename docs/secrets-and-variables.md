# Secrets & Variables

How a seller service repo declares the credentials and config its services
reference, seeds them for testing, and surfaces guidance to customers — as **one
committed manifest**, so nothing drifts.

## The model

A service's `offering.json` / `listing.json` reference customer-supplied values as
`${ customer_secrets.<NAME> }` (and seller-supplied ones as `${ secrets.<NAME> }`).
For those references to resolve — during **gateway tests** (the synthetic
*ops customer*) and for real customers who haven't set their own — every `<NAME>`
must exist in the platform's **seller-secret store**.

There are two moving parts, and they must not disagree:

1. **The committed manifest** — a repo file (`.env.example`, conventionally a
   symlink to `seller.secrets.txt`) that lists every `<NAME>`, its value, and a
   **customer-facing description**.
2. **The upload workflow** — on merge to `main`, seeds the seller-secret store from
   that manifest.

## The manifest is the single source of truth

Commit **`.env.example`** at the repo root (or keep `seller.secrets.txt` and
symlink `.env.example -> seller.secrets.txt` so the file is also shell-sourceable
for local testing). The upload workflows (`seller-upload-staging.yml` /
`seller-upload-production.yml`) **prefer** this file:

```bash
if [ -f .env.example ]; then
  # export every GitHub variable, then secret, into the env …
  usvc_seller secrets upload .env.example   # values AND descriptions, one call
  exit 0
fi
# … otherwise fall back to grepping ${ customer_secrets.X } names out of specs/
#     and seeding each from GitHub secrets/vars — values only, NO descriptions.
```

**Always commit the manifest.** The fallback path is the trap:

- It seeds **only** names referenced in `specs/` that also happen to exist as a
  GitHub secret/variable — a name missing from GitHub is silently skipped, so the
  service fails its gateway test with no obvious cause.
- Its values live in **GitHub variables**, maintained by hand, separately from the
  repo. When someone fixes a value in the repo but not in GitHub (or vice-versa),
  the two **drift** — the classic failure is a base URL that passes local tests
  (which read the repo/your shell) but 404s through the gateway (which used the
  stale GitHub value).

A committed manifest with in-file values ends both problems: the value in the
file is authoritative, and there is exactly one place to change it.

## Format

Shell-sourceable, one `export` per name, with the **contiguous `#` comment block
above** each entry as its description (the uploader stores it and surfaces it to
customers — unitysvc#1618/#1709):

```bash
# Amazon Chime incoming-webhook host (default https://hooks.chime.aws). In your
# Chime chat room open "Manage webhooks" and copy the webhook URL — this is the
# part before "/incomingwebhooks".
export CHIME_WEBHOOK_BASE="https://mock.unitysvc.dev/chime"

# Your Telegram bot token from @BotFather (send /newbot), e.g. "123456:ABC-DEF…".
export TELEGRAM_BOT_TOKEN="demotoken"
```

Rules:

- **Plain quoted literals** (`export NAME="value"`) — what `usvc_seller secrets
  upload` parses today. (Env-aware `${NAME:-default}` and trailing `# variable`
  markers are a newer capability; see *Variables* below.)
- **Descriptions are customer-facing.** Say what *the customer* sets and how they
  obtain it (link the provider's docs / Apprise), and give the real provider
  default. **Never** describe the seeded test value ("mock host for testing") —
  that leaks internal detail into customer-facing text.
- **Namespace names** with a service/provider prefix (`SMTP_RELAY_HOST`, not
  `SMTP_HOST`; `CHIME_WEBHOOK_BASE`, not `BASE`) — the store is per-seller, so
  generic names collide across services.

## Values: the mock, and the ops-customer fallback

Seed the **mock** value (`https://mock.unitysvc.dev/<channel>/…`, structurally-valid
placeholder tokens). Gateway tests run as the synthetic *ops customer*, which holds
none of these as its own secrets, so the gateway **falls back to your seller-secret
store** — that's what these seeded values are for. A real customer either sets their
own value or relies on the reference's `?? <real-provider>` default. So:

- URL bases use `${ customer_secrets.<SVC>_BASE ?? https://api.realprovider.com }`
  in the spec; seed `<SVC>_BASE` here to the mock host.
- The seeded value never reaches production customers — only ops-customer (test)
  traffic resolves to it.

(See the `writing-unitysvc-services` skill, §11, for the full ops-customer →
seller-secret fallback mechanics.)

## Variables vs. secrets

A seller-secret row can be **sensitive** (a *secret* — value write-only, masked) or
non-sensitive (a *variable* — value returned to the seller so they can read back
what they set). Classify by nature:

| Kind | Examples | Store as |
|---|---|---|
| Non-sensitive config | base URLs, hosts, ports, from/to addresses, region flags | **variable** |
| Credentials | API keys, tokens, passwords, device keys | **secret** |

Mark a variable in the manifest with a trailing **`# variable`**:

```bash
export CHIME_WEBHOOK_BASE="https://mock.unitysvc.dev/chime"   # variable
```

Caveats (until fully released, omit the marker and seed as secrets — the value is
what matters for routing, and a masked base still passes tests):

- `# variable` support in `usvc_seller secrets upload` ships with a specific seller
  SDK version; an older uploader mis-parses the trailing comment. Confirm the CI
  `usvc_seller` version before relying on it.
- A row's `sensitive` flag **cannot be flipped in place**. Converting an existing
  secret to a variable means **delete then re-create** (`usvc_seller secrets delete
  <NAME>`, then upload with `# variable`).

## What belongs in GitHub secrets

Only values that must **not** be committed in plaintext — a seller's *real* upstream
credential used for testing against a live provider. Rule of thumb:

> **A manifest entry with no committed default ⇒ its value comes from a GitHub
> secret** (the workflow exports all GitHub secrets/vars into the env before
> `secrets upload`, so an unquoted `${NAME}` / `${NAME:-}` resolves to it).
> Everything with a committed (mock) default lives in the manifest.

The two workflow-credential secrets (`UNITYSVC_SELLER_{STAGING,PRODUCTION}_API_KEY`
/ `_API_URL`) are the only secrets a typical mock-tested repo needs.

## Setup checklist for a new (or existing) repo

1. Create/curate the manifest with every referenced `<NAME>`, a mock value, and a
   customer-facing description.
2. `ln -sf seller.secrets.txt .env.example` (keeps one source of truth; the file
   stays shell-sourceable and the workflow finds `.env.example`).
3. Confirm no reference is unseeded:
   `grep -rho '\${ customer_secrets\.[A-Z_]*' specs/ | sort -u` vs. the manifest.
4. Seed staging and validate: `usvc_seller secrets upload seller.secrets.txt`,
   then `usvc_seller services run-tests '<name>' --force`.
5. Commit `.env.example` + the manifest; the merge-to-`main` workflow seeds the
   store from it thereafter.
