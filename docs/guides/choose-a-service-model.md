# Choose a Service Model

This guide is for a seller deciding *what kind of thing* to publish before
writing a spec. Four questions lead to one of seven service types; each type
then lists the spec sections it needs, with an annotated example. For the
mechanics of writing and uploading a spec, see
[Author & Upload Specs](author-specs.md); for the delivery patterns a channel can
take, [Service Types](../service-types.md); for price objects,
[Pricing](../pricing.md); for every field, [File Schemas](../file-schemas.md).

!!! note "Status"
    Checked against the platform topics (`seller`, `access-methods`, `channel`,
    `enrollment`, `pricing`, `invoices-payouts`, `platform-service`), the `bill`
    system service, the `labs/OpenLine` spec, and the compute plan in
    [unitysvc#2998](https://github.com/unitysvc/unitysvc/issues/2998),
    [#2999](https://github.com/unitysvc/unitysvc/issues/2999),
    [#3000](https://github.com/unitysvc/unitysvc/issues/3000) and
    [#3001](https://github.com/unitysvc/unitysvc/issues/3001). Spec shapes for
    container hosting (`unitysvc.app`) and seller-run instances are marked
    **proposed** where the contract is still being settled; §7 lists what is
    open.

## 1. The wizard: four questions, asked in order

Answer each question once. Each answer narrows the next, and the four answers together name your service type (§2) and the spec you write (§5).

### Step 1: Do you have a server?

| Answer | Meaning | What it decides |
| --- | --- | --- |
| **A. Yes, I have a server that can serve customers** | Your own machine, cloud, or a provider API behind your key. The platform never runs your code. | Nothing in the spec yet: you bring the upstream, and Step 2 decides whether the spec names it (through a gateway), only links to it (your own channel) or leaves it out (your server calls the customer's Me). The platform operates nothing for you |
| **B. No, I need compute** | You have software (a container) but nowhere to run it. unitysvc.app runs it in one of two roles: **as the product**, one instance per customer enrollment at the customer's expense; or **as your server**, one instance you enroll in and pay for yourself, behind which you publish ordinary services (then continue as 1A). See §5.4.1. **Meant for small, mostly per-customer services**: bounded CPU, RAM and ephemeral disk per instance, no GPU, no persistent volumes. A compute-heavy or high-volume upstream stays on your own infrastructure (1A). | The platform operates your container. The spec carries a container channel (`spec`, tiers with CPU / RAM / ephemeral disk, `entries`) whichever role it plays; the role decides who enrolls in it and who pays for it |
| **C. I don't need a server** | The work is done by a person, by a cron or GitHub Action from your own machine. | Nothing of yours runs, so the spec has no upstream of yours. What it has instead comes from Step 2: a link to where the work happens, or Me access requests |

### Step 2: How do customers reach the service?

| Answer | Available after | Meaning | Channel type |
| --- | --- | --- | --- |
| **A. My own channel** | 1A, 1C | Customers use it at your site, by email, on a call, in person. UnitySVC lists it, probes it daily, and never routes to it. | `external` |
| **B. Through the platform: gateway** | 1A | Every call goes through the API, S3, SMTP or MCP gateway with the customer's UnitySVC key. The gateway authenticates, meters and forwards. | `unbound` / `secret_bound` / `enrollable` |
| **C. Through the platform: instance URL** | 1B | The customer opens the URL of their own running instance. | container |
| **D. Through the platform: the customer's Me** | 1A, 1C | Your code acts *for* the customer: sends to their `/notify` or `/email`, uses their `/ai`, reads and writes their `/storage`. There may be no customer-facing endpoint at all. | `me_bound` |

A service can have more than one channel, so 2A and 2D often go together (the product is your website, the money and notifications go through Me).

### Step 3: How much do you need to know about the customer?

This is the step that decides the channel type and, through it, what you can charge for.

| Answer | Meaning | What you get | What you can do | Channel type |
| --- | --- | --- | --- | --- |
| **A. Nothing** | The service is the same for everyone. A call arrives with a valid key; you do not know, and do not need to know, who sent it. | Nothing. The gateway strips identity; you see traffic and a metering record. | Serve the call. | `unbound` (your key) or `secret_bound` (the customer's own key or endpoint) |
| **B. An account, no interaction** | Each customer has their own configuration, tenant or instance, but you never contact them. The customer sets it up once and uses it. | An **enrollment**: a stable code, the parameters the customer filled in, and the per-enrollment URL. You still don't know who they are. | Keep per-customer state keyed by the enrollment code. Route each tenant to its own upstream path or instance. | `enrollable`, or a container tier |
| **C. A personalized relationship** | You act for a specific person and may need to reach them: send alerts, email results, ask a question, hold a conversation. | What you **ask for at enrollment and the customer approves**, each item with a justification: profile fields (name, timezone, address…), `/notify`, `/email`, `/ai`, `/storage`, `/bill`, and a chat line (a `resource:room`, as OpenLine does). | Everything in B, plus: notify and email them, read the profile fields they shared, use their AI budget, read and write their files, charge them, and chat with them from their own apps (Discord, Slack, email, the Rooms page). | `me_bound` |

Rules behind the three answers:

- **A is the only answer with no enrollment.** The customer calls with a key; nothing is set up per customer. It is also the only answer that can be a platform-service member (`/p/`), because pool members must be interchangeable.
- **B gives you an account without an identity.** You know "enrollment `K7M2`, region `eu`", not the person. If you later need to reach them, you add access requests and the channel becomes C.
- **C is consent-based and itemized.** Every profile field, surface and limit is a separate request the customer sees before enrolling and can refuse unless you mark it required. Ask for the least you need: a service that only needs to send alerts asks for `/notify`, not the profile.
- **Chat is part of C.** A `resource:room` request creates a line the customer owns and you are a member of; the customer reads and posts from Discord, Slack, email, the CLI or the web, you from your code or the same tools. This is how a human-delivered service (consulting, support) talks to its customer without leaving UnitySVC.

### Step 4: How are you paid? (Steps 2 and 3 decide what is possible)

| Answer | Possible after | Meaning | What the spec gets |
| --- | --- | --- | --- |
| **A. I don't want payment** | any | Free: open source, demos, a listing for discovery. On unitysvc.app "free" means *priced at base cost*: the customer still pays the platform's compute, you take nothing. | `list_price: 0` (or `= base cost`), `payout_price: 0` |
| **B. I manage my own billing** | 2A only | The customer pays you at your site. UnitySVC is catalog and discovery only. | `external` channel, `list_price: 0` with a description of your pricing |
| **C. I charge per transaction (`/bill`)** | 3C only (any delivery) | Your code charges the customer's enrollment one or more *units* of the listing price, with an idempotency key, within per-charge, daily and monthly limits the customer approved. For an hour, a report, an alert, a seat-month, a job. | A `service:bill` access request on the `me_bound` channel; `list_price` is the unit price |
| **D. Pay as you go (platform metering)** | 2B or 2C, with 3A, 3B or 3C | The gateway prices every call (tokens, requests, bytes, seconds…), or the platform accrues instance time per tier. Nothing to code. | `list_price` with a metered `type`; `payout_price` |

Why delivery and customer knowledge decide billing:

- **Metering needs the gateway (or the platform's runner) in the path.** It cannot see traffic on your own channel, so 2A can only be free, self-billed, or `/bill`.
- **`/bill` is a Step 3C permission.** Only a key leased from an enrollment may hold `service:bill`, and `service:bill` is an access request like `/notify`, so charging per transaction means asking the customer for it. Each charge is `units` × the listing's own `list_price`, so the listing price *is* the unit you bill in.
- **unitysvc.app always meters instance time.** The customer pays your tier price `P`; the platform deducts base cost `C` and shares the rest: `payout = (P − C) × r`. Your price must exceed base cost; "free" on unitysvc.app is `P = C`. You pay for compute only when you are your own customer. In-app purchases on top of that use `/bill`.
- **The customer always pays one wallet.** In every model but 4B, charges land on the customer's single UnitySVC statement, and you are paid out per cycle after the platform fee.
- **BYOK is not a sale.** When the customer brings their own provider key, the provider bills them; your metered price is at most a routing fee.

## 2. Where the wizard lands: seven service types

Every path through the wizard ends in one of these (T0 is the step before selling, for authors who want to be found without charging). The type decides which sections your spec must contain (§5).

| Type | Wizard path | In one sentence | Typical services |
| --- | --- | --- | --- |
| **T0. Open-source app on the customer's key** | 1C / 2D / 3A (the app declares B.4 requests) / 4A | People run your app themselves with a key they create on their own account; you are listed, hold no key, and bill nothing. | An open-source agent, monitor or tool that uses its user's `/ai`, `/notify`, `/me`, `/log` |
| **T1. Ads only** | 1A / 2A / 3A / 4B (or 4A) | Your service is listed in the catalog and found by people and AI agents; customers use and pay for it at your site. | An existing SaaS, a paid API with its own sign-up, a tool or dataset hosted elsewhere |
| **T2. Metered gateway service** | 1A / 2B / 3A / 4D | Customers call your upstream through a gateway with their UnitySVC key; the platform prices every call. | LLM and other HTTP APIs (your key or the customer's), S3 datasets and media, SMTP relay, a member of a `/p/` pool |
| **T2b. BYOK relay** | 1A / 2B / 3A / 4D (routing fee) or 4A | Customers call a provider through the gateway with **their own provider key**; the provider bills them, you earn at most a routing fee. | A provider's API listed next to your managed channel so customers with their own key can use it; Labs listings of providers nobody resells |
| **T3. Per-customer gateway service** | 1A / 2B / 3B / 4D | Each customer enrolls with parameters and gets their own endpoint; you never contact them. | Multi-tenant SaaS API, uptime and scheduled checks |
| **T4. Hosted app on unitysvc.app** | 1B / 2C / 3B / 4D (4A at cost) | The platform runs your container per enrollment at a tier you define; the customer opens its URL. For small, mostly personal services, not for heavy or large-scale compute. | Open-source tools under UnitySVC Labs, your own web app or agent sold by the hour |
| **T5. Service on the customer's Me** | 1A or 1C / 2D / 3C / 4C | Your code works for the customer through their Me and charges per unit of work. | Alert and digest services, monitors, on-demand reports and jobs, agents |
| **T6. Your own app, billed here** | 1A / 2A + 2D / 3C / 4C | The product stays on your site; the customer signs in with UnitySVC and is charged through `/bill`. | A web app adding "Use your UnitySVC account", seats or jobs priced per month or per run |
| **T7. Human services** | 1C / 2A + 2D / 3C / 4C | A person delivers the work; the enrollment is the engagement, `/bill` is the timesheet, a chat line is the office. | Consulting, analysis, code review, tutoring, design |

Two paths are not types of their own:

- **BYOE recipes.** The customer runs the server and brings the key, so there is nothing for a seller to meter or bill. Rare, and in practice published by UnitySVC Labs so customers can put their own Ollama or vLLM behind the gateway. A seller whose software customers self-host can publish one free (§5.3.1) or ask Labs to.
- **Seller-run instance on unitysvc.app.** Not a type either: you enroll in a container service yourself, pay its instance time, and the instance becomes the upstream of a T2, T3 or T5 service you publish. The customer never sees the container. §5.4.1 contrasts it with T4.

## 3. The matrix the wizard lands on

Rows are Step 1, columns are Step 2; each cell names the types that live there, with the Step 3 and Step 4 answers they take.

| Hosting \ Delivery | **2A. Your own channel** | **2B. Platform gateway** | **2C. Instance URL** | **2D. Customer's Me** |
| --- | --- | --- | --- | --- |
| **1A. Your own server** | **T1 Ads only** (3A, 4B). **T6 Your own app, billed here** (3C, 4C; with a Me channel) | **T2 Metered** (3A, 4D). **T2b BYOK relay** (3A, 4D routing fee or 4A). **T3 Per-customer** (3B, 4D) | — | **T5 On the customer's Me** (3C, 4C), run from your server |
| **1B. unitysvc.app** | — | T4 variant: a container that also exposes an API entry, metered per call (3B, 4D) | **T4 Hosted app** (3B, 4D; 4A at cost). `/bill` on top for in-app purchases (3C, 4C) | T5 variant: an agent container working through the customer's Me (3C, 4C) |
| **1C. No server** | **T1 Ads only** for a thing you host nowhere. **T7 Human services** (3C, 4C) | BYOE recipe, Labs (3B, 4A) | — | **T5 On the customer's Me** (3C, 4C), run from a GitHub Action or your laptop's cron. **T0 Open-source app** (3A, 4A), run by the customer with their own key |

Empty cells are combinations the platform cannot serve: an instance URL needs unitysvc.app, and a container cannot be reached on "your own channel".

## 4. The billing mechanisms, side by side

| Mechanism | Who triggers it | Unit | Where the price lives | Types |
| --- | --- | --- | --- | --- |
| **Gateway metering** | The customer's call | tokens, requests, seconds, bytes, images… (`pricing` types) | `listing.list_price`; `offering.payout_price` | T2, T3; `invoke` calls in T5 |
| **Instance time** (proposed, [unitysvc#3001](https://github.com/unitysvc/unitysvc/issues/3001)) | Platform, from first readiness to stop/suspend/cancel | `one_hour` / `one_day` of a tier | `list_price` per tier channel | T4 |
| **`/bill` charge** | Your code, with an `Idempotency-Key` | `units` × the listing's price | `listing.list_price` (`constant` with a `/ unit` description) | T5, T6, T7; T4 in-app purchases |
| **Subscription fee** | `/bill` on your schedule, or a heartbeat `/s/` call | one period | `constant` per period | T5, T6 flat plans |
| **None** | — | — | `price: "0"` | T1, T2b, BYOE recipes, demos, T4 at cost |
| **Outside UnitySVC** | Your own billing | — | `external` channel; `list_price` describes it | T1 |

Limits the customer approves at enrollment cap `/bill`: per charge (`max_units_per_charge`), per hour/day/month by count and amount. Read the room left before doing the work.

## 5. What each type's spec needs

### 5.0 The anatomy of a spec

A service is a folder with three files and at least one test: `provider.json` (who), `offering.json` (what you deliver and what you earn), `listing.json` (how it is sold). `usvc seller specs validate`, `format`, `upload --submit`. The sections below are lettered so that each service type can be stated as a recipe: "T3 needs A.2, B.3, C.1, D.1, E.1, F.1, F.3".

#### A. `user_access_interfaces` (listing): how customers reach you through a gateway

The address a customer calls, with their UnitySVC key. Only for delivery through a gateway (Step 2B). It is what code examples are generated from.

| Variant | What to put | When |
| --- | --- | --- |
| **A.0 none** | Omit the section | Your own channel (T1, T6, T7), Me-only services (T5), hosted apps (T4: instance URLs are generated per enrollment and never written here) |
| **A.1 shared gateway URL** | `${API_GATEWAY_BASE_URL}/<name>`, with the same `routing_key` as the channel (the `model` the customer names) | One address for every customer: T2 HTTP APIs |
| **A.2 per-enrollment URL** | `${API_GATEWAY_BASE_URL}/e/{{ enrollment.code }}` | Each customer has their own configuration: T3 |
| **A.3 S3 gateway** | `${S3_GATEWAY_BASE_URL}/<bucket-name>`, `access_method: "http"` | Buckets browsed with S3 tools |
| **A.4 SMTP gateway** | `${SMTP_GATEWAY_BASE_URL}`, `access_method: "smtp"`, `routing_key.username` | Relays used from a mail client or library |

#### B. `upstream_access_config` (offering): how the platform reaches you, and what the channel needs from the customer

One or more named **channels**. A channel's *contents* decide its type, which is Step 3's answer in spec form: what the customer must set up, and whether you can reach them. A service may hold several channels (a managed and a BYOK channel, an external and a Me channel), and each can carry its own price (C.3).

| Variant | Channel type | What to put | What the customer gives | Can you reach them |
| --- | --- | --- | --- | --- |
| **B.1 your credential** | `unbound` | `access_method` (`http`, `http` + `storage_type: "s3"`, `smtp`), the upstream address, `api_key` / `secret_key` / `password` as `${ secrets.NAME }`, `routing_key`, `rate_limit_refs` | Nothing; they call with their key | No |
| **B.2 the customer's secret** | `secret_bound` | The same, with `${ customer_secrets.NAME }` for the key, the endpoint, or both | A stored secret: their own provider key or webhook | No |
| **B.3 per-enrollment parameters** | `enrollable` | `params.schema` (JSON Schema), templates reading `{{ params.* }}` or `{{ enrollment.code }}`, `${ customer_secrets.{{ params.X }} ?? }` for a customer-named secret | Parameters at enrollment: a region, a target, their own endpoint (BYOE) | No |
| **B.4 access to the customer's Me** | `me_bound` | `customer_access_requests`: one entry per surface with `object` (`service:notify`, `service:email`, `service:ai`, `service:storage`, `service:bill`, `service:me` with `profile=` / `intents=` / `preferences=` options, `service:log`, `resource:room`), `permissions`, `options`, `limits`, `required`, `justification`. Optionally `params.schema` and `invoke` (`input_schema`, `min_interval_seconds`, `expected_latency`) | Itemized approval before enrolling; a leased key with exactly those grants | Yes, within what they approved. `service:bill` is how you charge |
| **B.5 your own channel** | `external` | `type: "external"`, `url`, `description` | Nothing at UnitySVC | No; nothing is routed, the site is probed daily |
| **B.6 a container** (proposed) | container | `access_method: "container"`, `spec` (the Compose document), `resources` (`cpu`, `memory`, `ephemeral_disk`), `entries` (`name`, `service`, `port`, `auth`, `path`); one channel per tier; optional B.4 requests for what the instance may use | A tier choice at enrollment | Only through B.4 requests |

Rules: B.4 outranks everything and B.3 outranks B.2 when a channel mixes them. A secret you ship a default for (`?? value`) does not change the type. `service:bill` may appear only in a B.4 channel.

#### C. `list_price` (listing): what the customer pays per unit

One price object, as strings. Its `type` is the unit; the `description` carries the unit when the type cannot (`"$0.05 / reminder"`), plus badges and a hover note.

| Variant | What to put | When |
| --- | --- | --- |
| **C.1 metered** | `one_million_tokens` (`input` / `output`), `one_thousand` requests, `one_gigabyte`, `one_minute`, `image`, `tiered`, `graduated`, `add` | The gateway or runner meters every call: T2, T3 |
| **C.2 per unit of work** | `constant` with the unit in the description: an hour, a report, a seat-month, an alert | You charge through `/bill`: each charge is `units` of this price. T5, T6, T7 |
| **C.3 per channel or tier** | `type: "channel"`, `default`, `channels: { name: price }` | A managed and a BYOK price on one service; container tiers priced `one_hour` (T4) |
| **C.4 zero** | `price: "0"` with a description that says why (`"Free | you run the server"`, `"From $19 / month at acme.example | not billed through UnitySVC"`) | Free services, BYOE recipes, ads-only listings |

#### D. `payout_price` (offering): your contract with the platform

What you earn per unit the customer is charged. The platform computes it per call from the customer charge, after promotions.

| Variant | What to put | Meaning |
| --- | --- | --- |
| **D.1 revenue share** | `type: "revenue_share"`, `percentage: "80"` | You receive that percentage of what the customer paid, **after the platform's base cost for the unit is deducted**. For gateway services the base cost is zero, so it is a share of the list price. For hosted apps (T4) it is a share of `P − C`, the tier price less the instance's compute cost |
| **D.2 fixed unit price** | A price object in the same units as C | A unit rate you agreed with the platform, independent of the list price. Your margin is `list − payout` |
| **D.3 zero** | `price: "0"` | You decline payment: Labs listings, free recipes, ads-only |

#### E. `documents` (listing): tests and pages

| Variant | What to put | Why |
| --- | --- | --- |
| **E.1 connectivity test** | `$doc_preset` (`api_connectivity`, `s3_connectivity`, `smtp_connectivity_v2`, `notify_relay_connectivity_discord`…) or your own `category: "connectivity_test"` script | Runs on submit and daily; gates activation. Required for every gateway service |
| **E.2 code examples** | `$doc_preset` (`s3_code_example`, `smtp_code_example`…) or `category: "code_example"` files | Rendered on the listing, executed as tests |
| **E.3 getting started** | `category: "getting_started"`, a Markdown file | What the customer sees first. Required where there is no gateway call to show (T1, T4 to T7) |
| **E.4 container spec** (proposed) | `category: "container_spec"`, the Compose file | Reviewed as a revision; a change needs re-review (T4) |

#### F. `service_options` (listing): enrollment and test behaviour

| Variant | What to put | When |
| --- | --- | --- |
| **F.1 enrollment** | `enrollment.required: true`, `enrollment.limit_per_customer: N` | Any B.3, B.4 or B.6 channel; the limit says how many configurations, instances or engagements one account may hold |
| **F.2 recurrence** | `prompt_recurrence: true`, `recurrence_min_interval_seconds`, `recurrence_max_interval_seconds`, `recurrence_allow_cron` | The customer sets a schedule at enrollment and the platform fires the call: monitoring, checks |
| **F.3 test parameters** | `ops_testing_parameters: { param: value }` | Required whenever B.3 has required parameters, so the platform can enroll its test account |

#### G. Identity and description (offering and listing)

| Field | What to put |
| --- | --- |
| `name` | `provider/service`, lowercase, stable; the same in both files. It is the gateway path segment. The prefix is the provider's name (H), which for hosted or recipe listings is the author's, not yours |
| `service_type` | `llm`, `proxy`, `content`, `email`, `notification`, `saas`, `consulting`, `container` (proposed)… Catalog grouping and which presets apply |
| `capabilities`, `tags` | Registered capability names (`chat`, `embed`, `s3_read_redirect`, `smtp_relay`, `notification_relay`…) for discovery filters and agent search |
| `summary` | One line for the catalog card |
| `description` | Markdown: how it works, what the customer sets up, what each parameter and access request is for, what is charged and when, limits, what is ephemeral. The enrollment dialog links here |
| `logo` | `logo.svg` or `logo.png` in the folder |
| `display_name`, `currency` | The human title and `USD`, on the listing |

#### H. `provider.json`: who made it

The **provider** is the entity that stands behind the service, and the **seller** is the account that publishes it and is paid. They are often the same, and the spec keeps them apart so that credit and money can go to different places. For a service you built, the provider is you. For an API you resell, it is the vendor (`openai`, `cohere`). For open-source software you host (T4) or publish a recipe for, it is **the project or its author**, so the listing reads "Open WebUI, by Open WebUI, hosted by Acme" and the author is credited whether or not they are paid. A seller never lists someone else's work under their own provider name.

Fields: `name` (the catalog prefix and the first segment of every service `name`), `homepage` (the project's site or repository when the provider is an author), `contact_email` (the provider's public contact; support and disputes about the *listing* still reach the seller), `terms_of_service`, `status`, and `rate_limits` that B.1 channels reference with `rate_limit_refs`.

#### I. Outside the spec

| Item | What to do |
| --- | --- |
| Seller secrets | `usvc seller secrets create NAME --value-stdin` before upload; `${ secrets.NAME }` must resolve |
| Your runner (B.4 services) | A cron, a GitHub Action, a worker or a seller-run instance that lists enrollments, leases a key per enrollment, does the work, calls `/bill` with an `Idempotency-Key`, returns the key |
| Your sign-in (T6) | "Use your UnitySVC account" that links a user to an enrollment |
| A private container service (seller-run instance) | See §5.4.1 |

#### Recipes: what each type specifies

| Type | A | B | C | D | E | F | G, H |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **T0 Open-source app** | A.0 | B.5 + B.4 with the key issued to the customer | C.4 | D.3 | E.3 | F.1 | yes, + a policy template in the repo |
| **T1 Ads only** | A.0 | B.5 | C.4 | D.3 | E.3 | — | yes |
| **T2 Metered gateway** | A.1 / A.3 / A.4 | B.1 | C.1 (C.3 if several channels) | D.1 or D.2 | E.1 (+ E.2) | — | yes, + H `rate_limits` |
| **T2b BYOK relay** | A.1 | B.2 (usually next to a B.1 channel) | C.1 routing fee or C.4; C.3 when both channels exist | D.1 on the fee, or D.3 | E.1 | — | yes |
| **T3 Per-customer gateway** | A.2 | B.3 | C.1 | D.1 or D.2 | E.1 | F.1, F.3 (+ F.2 for checks) | yes |
| BYOE recipe (Labs) | A.2 | B.3 with `{{ params.base_url }}` | C.4 | D.3 | E.1 | F.1, F.3 | yes |
| **T4 Hosted app** | A.0 | B.6 (+ B.4 if the app uses Me) | C.3 of `one_hour` tiers (at cost for Labs) | D.1 (D.3 for Labs) | E.4, E.3 | F.1 | yes; H is the author when the software is not yours |
| **T5 On the customer's Me** | A.0 | B.4 with `service:bill` (+ `params`, `invoke`) | C.2 | D.1 | E.3 (+ E.1 once a Me test exists) | F.1, F.3 | yes |
| **T6 Your own app, billed here** | A.0 | B.5 + B.4 with `service:bill` | C.2 | D.1 | E.3 | F.1 | yes |
| **T7 Human services** | A.0 | B.5 + B.4 with `service:bill`, `resource:room` | C.2 | D.1 | E.3 | F.1 | yes |

What follows is each type's recipe in detail: the sections it uses, why, and one annotated example.

### 5.1 T1. Ads only

Catalog presence and discovery by people and MCP agents. Nothing is routed; nothing is billed through UnitySVC. The site is probed when you submit and daily after; a site that stays unreachable is unlisted.

**Recipe:** G, H · B.5 external channel · A.0 · C.4 with your real pricing in the description · D.3 · E.3.

| Section | Required | What to put | Why |
| --- | --- | --- | --- |
| channel `type: "external"` | yes | Declared explicitly: nothing in a configuration can imply it | The gateway must know not to route it |
| channel `url` | yes | The page a customer lands on; a sign-up or pricing page is best | Probed daily; the listing's call to action |
| channel `description` | yes | How to use it there: "Sign up at…", "Download from…" | Shown in place of a gateway interface |
| `list_price` | yes, `0` | `description` states your real pricing: `"From $19 / month at acme.example | not billed through UnitySVC"` | The card must not read "free" |
| `payout_price` | yes, `0` | — | Nothing is paid out |
| `user_access_interfaces` | no | Omit | There is no gateway URL |
| `documents` | a `getting_started` page | What the service does and how to start | The connectivity test is the daily probe of `url` |

```json
// offering.json
{
  "schema": "offering_v1",
  "name": "acme/studio-direct",
  "service_type": "saas",
  "summary": "Collaborative design studio for small teams",
  "description": "Use at studio.acme.example; sign up there with any email. Plans from $19 / month, billed by Acme.",
  "logo": "logo.svg",
  "tags": ["design", "collaboration"],
  "payout_price": { "type": "constant", "price": "0" },
  "upstream_access_config": {
    "web": {
      "type": "external",
      "url": "https://studio.acme.example/signup",
      "description": "Sign up and use the studio at acme.example; billed by Acme"
    }
  }
}
```

```json
// listing.json
{
  "schema": "listing_v1",
  "name": "acme/studio-direct",
  "display_name": "Acme Studio",
  "currency": "USD",
  "list_price": { "type": "constant", "price": "0", "description": "From $19 / month at acme.example | not billed through UnitySVC" },
  "documents": { "Getting started": { "category": "getting_started", "file_path": "README.md", "mime_type": "markdown" } }
}
```

### 5.2 T2. Metered gateway service

Your upstream, reached through a gateway with the customer's key. No enrollment. The platform prices every call from the metering record.

**Recipe:** G, H (with `rate_limits`) · B.1 · A.1, A.3 or A.4 · C.1, or C.3 when channels are priced apart · D.1 or D.2 · E.1 and E.2.

| Section | Required | What to put | Why |
| --- | --- | --- | --- |
| channel `access_method` | yes | `http` for APIs; `http` + `storage_type: "s3"` for buckets; `smtp` for relays | Picks the gateway |
| channel upstream | yes | HTTP: `base_url`, `api_key: "${ secrets.NAME }"`, `routing_key` (the `model` the customer names). S3: `s3_endpoint`, `bucket`, `base_path`, `region`, `access_key`, `secret_key`. SMTP: `host`, `port`, `tls`, `username`, `password` | How the gateway reaches you. Secrets are write-only and injected per request |
| seller secrets | yes | Create with `usvc seller secrets create NAME` before upload | `${ secrets.NAME }` must resolve |
| `rate_limit_refs` | recommended | Names from `provider.json` `rate_limits` | Your provider quota is shared by all customers |
| `list_price` | yes, metered | `one_million_tokens` (`input` / `output`), `one_thousand` requests, `one_gigabyte`, `one_minute`… | The unit must match what the upstream meters |
| `payout_price` | yes | `revenue_share` percentage, or your own unit price | Your earning per call |
| `user_access_interfaces` | yes | `${API_GATEWAY_BASE_URL}/<name>` with the same `routing_key`; `${S3_GATEWAY_BASE_URL}/<bucket-name>`; `${SMTP_GATEWAY_BASE_URL}` with `routing_key.username` | The customer-facing address |
| `documents` | yes | `$doc_preset`: `api_connectivity`, `s3_connectivity` + `s3_code_example`, `smtp_connectivity_v2` + `smtp_code_example`; LLMs get chat examples from the capability | Daily tests and rendered examples with no writing |
| `/p/` membership | optional | Not hand-written: instantiate the system template with a params file and upload | Pool members must be interchangeable; hand-written specs never join |

```json
// offering.json: an LLM on your own server, with a BYOK channel (see 5.2.1)
{
  "schema": "offering_v1",
  "name": "acme/llama-3.3-70b",
  "service_type": "llm",
  "capabilities": ["chat"],
  "summary": "Llama 3.3 70B served from Acme's own GPUs",
  "description": "OpenAI-compatible chat completions. The `managed` channel uses Acme's capacity; the `byok` channel forwards to Groq with your own key.",
  "logo": "logo.svg",
  "payout_price": { "type": "revenue_share", "percentage": "80" },
  "upstream_access_config": {
    "managed": {
      "access_method": "http",
      "base_url": "https://inference.acme.example/v1",
      "api_key": "${ secrets.ACME_INFERENCE_KEY }",
      "routing_key": { "model": "llama-3.3-70b" },
      "rate_limit_refs": ["acme_perminute"]
    },
    "byok": {
      "access_method": "http",
      "base_url": "https://api.groq.com/openai/v1",
      "api_key": "${ customer_secrets.GROQ_API_KEY }",
      "routing_key": { "model": "llama-3.3-70b-versatile" }
    }
  }
}
```

```json
// listing.json
{
  "schema": "listing_v1",
  "name": "acme/llama-3.3-70b",
  "display_name": "Llama 3.3 70B (Acme)",
  "currency": "USD",
  "list_price": {
    "type": "channel", "default": "managed",
    "channels": {
      "managed": { "type": "one_million_tokens", "input": "0.40", "output": "0.80" },
      "byok":    { "type": "one_thousand", "price": "0.01", "description": "$0.01 / 1,000 requests ~ routing fee | Groq bills your key for tokens" }
    }
  },
  "user_access_interfaces": {
    "openai": { "access_method": "http", "base_url": "${API_GATEWAY_BASE_URL}/acme/llama-3.3-70b", "routing_key": { "model": "llama-3.3-70b" } }
  },
  "documents": { "Connectivity test": { "$doc_preset": "api_connectivity" } }
}
```

Same type, other gateways:

```json
// S3 dataset: offering channel + listing interface and price
"bucket": { "access_method": "http", "storage_type": "s3", "s3_endpoint": "https://nyc3.digitaloceanspaces.com",
            "bucket": "acme-genomes-1k", "base_path": "hg38/", "region": "nyc3",
            "access_key": "${ secrets.ACME_SPACES_KEY_ID }", "secret_key": "${ secrets.ACME_SPACES_SECRET }" }
"list_price": { "type": "one_gigabyte", "price": "0.02", "description": "$0.02 / GB downloaded" }
"user_access_interfaces": { "s3_gateway": { "access_method": "http", "base_url": "${S3_GATEWAY_BASE_URL}/acme-genomes-1k" } }
"documents": { "Connectivity test": { "$doc_preset": "s3_connectivity" }, "Python code example": { "$doc_preset": "s3_code_example" } }
```

```json
// SMTP relay
"relay": { "access_method": "smtp", "host": "smtp.sendgrid.net", "port": 587, "tls": true, "username": "apikey", "password": "${ secrets.SENDGRID_KEY }" }
"list_price": { "type": "one_thousand", "price": "1.00", "description": "$1 / 1,000 messages" }
"user_access_interfaces": { "smtp_gateway": { "access_method": "smtp", "base_url": "${SMTP_GATEWAY_BASE_URL}", "routing_key": { "username": "acme-relay" } } }
"documents": { "Connectivity test": { "$doc_preset": "smtp_connectivity_v2" } }
```

#### 5.2.1 BYOK: the customer's own provider key

A BYOK channel is a row of its own because the money is different. The customer stores their provider key as a secret; the gateway injects it; the **provider bills the customer** for what they consume. UnitySVC meters the calls, so you can charge a routing fee per request, or nothing. You never see the key.

| Section | Required | What to put | Why |
| --- | --- | --- | --- |
| channel `api_key` | yes | `${ customer_secrets.NAME }`; the reference is the declaration, no schema needed | The namespace says who owns the secret |
| channel `rate_limit_refs` | no | Leave out; use `ops_rate_limit_refs` only for the platform's own tests | BYOK traffic spends the customer's provider quota, not yours |
| `list_price` | yes | `C.4` zero, or `C.1` a small `one_thousand` requests fee with `~ routing fee` in the description. `C.3` when the same service also has a managed channel | The card must not suggest the provider's tokens are included |
| `payout_price` | yes | `D.1` share of the fee, or `D.3` | There is nothing else to share |
| `user_access_interfaces` | yes | A.1, the same as the managed channel; customers pin with `@byok` | One address, two channels |
| `documents` | yes | E.1 `api_connectivity`; the platform's test account holds the needed secret | Daily test |

Who offers it: a seller who resells a provider adds a BYOK channel so customers who already have a key keep using it through the same address, often as the free fallback in a service group. UnitySVC Labs lists pure-BYOK services for providers nobody resells.

### 5.3 T3. Per-customer gateway service

The customer enrolls with parameters and calls their own `/e/<code>` endpoint. You get the enrollment code and parameters on every request, never the person. Covers multi-tenant APIs and scheduled checks.

**Recipe:** G, H · B.3 with `params.schema` · A.2 · C.1 · D.1 or D.2 · E.1 · F.1, F.3, and F.2 for scheduled checks.

| Section | Required | What to put | Why |
| --- | --- | --- | --- |
| channel `params.schema` | yes | JSON Schema of what the customer fills in: a region, a target URL, a project id. Secret *names* go in parameters, values never | What the enrollment dialog asks. A channel that reads `{{ params.* }}` is `enrollable` |
| channel `base_url` / `api_key` | yes | Templated: `https://app.acme.example/t/{{ enrollment.code }}` or `{{ params.base_url }}`; `${ customer_secrets.{{ params.key_secret }} ?? }` for a customer-supplied key | Per-tenant routing; `?? ` makes the secret optional |
| `user_access_interfaces` | yes | `${API_GATEWAY_BASE_URL}/e/{{ enrollment.code }}` | Each customer's own address |
| `service_options.enrollment` | recommended | `limit_per_customer`: how many configurations one account may hold | Several targets per customer, or exactly one |
| `service_options.ops_testing_parameters` | yes when params are required | Values the platform uses to enroll its test account | Otherwise the daily test cannot run |
| `service_options.prompt_recurrence` + `recurrence_*` | for checks | Let the customer set a schedule at enrollment | The platform fires the call on that schedule |
| `list_price` | yes | Metered per call or check | Same mechanism as T2 |
| `description` | yes | Say what each parameter is for | The enrollment dialog links here |

```json
// offering.json: a multi-tenant API
{
  "schema": "offering_v1",
  "name": "acme/pipeline",
  "service_type": "proxy",
  "summary": "Run Acme data pipelines on your own tenant",
  "description": "Enroll once per project. Pick a region; your tenant is created on first call and reached at your enrollment's /e/ URL.",
  "payout_price": { "type": "revenue_share", "percentage": "85" },
  "upstream_access_config": {
    "tenant": {
      "access_method": "http",
      "base_url": "https://app.acme.example/t/{{ enrollment.code }}",
      "api_key": "${ secrets.ACME_GATEWAY_KEY }",
      "params": {
        "schema": { "type": "object", "properties": {
          "region": { "type": "string", "enum": ["us", "eu"], "default": "us", "description": "Where your tenant's data lives" } } }
      }
    }
  }
}
```

```json
// listing.json
{
  "schema": "listing_v1",
  "name": "acme/pipeline",
  "display_name": "Acme Pipeline",
  "currency": "USD",
  "list_price": { "type": "one_thousand", "price": "0.50", "description": "$0.50 / 1,000 API calls" },
  "user_access_interfaces": { "enrollment": { "access_method": "http", "base_url": "${API_GATEWAY_BASE_URL}/e/{{ enrollment.code }}" } },
  "service_options": { "enrollment": { "limit_per_customer": 10 }, "ops_testing_parameters": { "region": "us" } },
  "documents": { "Connectivity test": { "$doc_preset": "api_connectivity" } }
}
```

Variants on the same skeleton:

```json
// Scheduled checks: the customer sets target and schedule at enrollment
"params": { "schema": { "type": "object", "required": ["target"], "properties": { "target": { "type": "string", "format": "uri" } } } }
"service_options": { "prompt_recurrence": true, "recurrence_min_interval_seconds": 60, "recurrence_max_interval_seconds": 86400, "recurrence_allow_cron": true,
                     "ops_testing_parameters": { "target": "https://example.com" } }
"list_price": { "type": "one_thousand", "price": "0.20", "description": "$0.20 / 1,000 checks" }
```

> Older specs put parameters in `user_parameters_schema` on the listing. Core 0.3.0 moves them to the channel's `params.schema`; use that for new specs.

#### 5.3.1 BYOE recipes: the customer's own server (Labs)

The customer runs the upstream and brings the key, so the channel is B.3 with `{{ params.base_url }}`, the price is C.4 and the payout D.3. There is nothing for a seller to monetize, which is why these are rare and mostly published by UnitySVC Labs: they let a customer put their own Ollama, vLLM or other OpenAI-compatible server behind the gateway and use it with the same key, aliases and primitives as everything else. A seller whose software customers self-host may publish one free, as documentation of the integration.

```json
// BYOE recipe: the customer's own Ollama, free
"own_instance": { "access_method": "http", "base_url": "{{ params.base_url }}",
                  "api_key": "${ customer_secrets.{{ params.api_key_secret }} ?? }",
                  "params": { "schema": { "type": "object", "required": ["base_url"], "properties": {
                    "base_url": { "type": "string", "description": "Your Ollama endpoint" },
                    "api_key_secret": { "type": "string", "default": "OLLAMA_API_KEY", "description": "Name of the secret holding your instance's key, if any" } } } } }
"list_price": { "type": "constant", "price": "0", "description": "Free | you run the server" }
"payout_price": { "type": "constant", "price": "0" }
```

The `description` must say what the customer's server has to expose. `ops_testing_parameters` should point at a server the platform can reach, or the daily test cannot run.

### 5.4 T4. Hosted app on unitysvc.app

**Proposed shape** ([unitysvc#2999](https://github.com/unitysvc/unitysvc/issues/2999), [#3000](https://github.com/unitysvc/unitysvc/issues/3000), [#3001](https://github.com/unitysvc/unitysvc/issues/3001)): you submit a restricted Compose file as a document; the platform builds or pulls an immutable image, runs one instance per enrollment at the tier the customer picked, and meters instance time. The customer pays your tier price; the platform keeps base cost and shares the rest.

**Recipe:** G, H · B.6, one channel per tier, plus B.4 requests for what the instance may use · A.0 · C.3 of `one_hour` tiers above base cost (at cost for Labs) · D.1 (D.3 for Labs) · E.4 and E.3 · F.1.

!!! note "What unitysvc.app is for"
    Small, mostly personalized services: one instance per customer, or one small
    instance of your own, inside a bounded tier of CPU, RAM and ephemeral disk.
    It is **not** a place for compute-heavy work (model inference, batch
    processing, anything that wants a GPU) or for one deployment serving a large
    number of customers at scale. Such upstreams belong on your own
    infrastructure (Step 1A) and are published as T2 or T3; a hosted app may
    still call them, or the customer's `/ai`, for its heavy parts. v1 has no
    GPU, no persistent volumes, no SSH, and bounded per-instance allocations;
    the tier catalog will state the ceilings.

| Section | Required | What to put | Why |
| --- | --- | --- | --- |
| one channel per tier | yes | `access_method: "container"`, a `description` in customer terms ("small workflow", "for a team of 100"), `resources` with `cpu`, `memory`, `ephemeral_disk` | Customers pick a tier, never hardware. Allocations fix the base cost |
| channel `spec` | yes | The Compose document's name | Which image and services the tier runs |
| channel `entries` | yes | `name`, `service`, `port`, `auth` (`enrollment_key` gates the URL behind the customer's key), optional `path` | The HTTPS entry points the instance exposes. Instance URLs are generated; never put them in `user_access_interfaces` |
| `customer_access_requests` | when the app uses Me | `service:ai`, `service:storage`, `service:notify`… with justifications | The instance gets a leased key with exactly these grants |
| `documents` → Compose file | yes, `container_spec` | Pinned image digests, declared ports, environment from the platform-injected variables. No `build`, no volumes, no host access | Reviewed as a revision; a change needs re-review |
| `documents` → `getting_started` | yes | What the customer sees after the instance is ready | There is no gateway code example |
| `list_price` | yes, per tier | `type: "channel"`, each tier `one_hour` above base cost. Labs: equal to base cost | Instance time accrues from first readiness to stop |
| `service_options.enrollment.limit_per_customer` | recommended | How many instances one account may run | Cost control for both sides |
| `user_access_interfaces` | no | Omit | Addresses are per instance |
| state | note in `description` | Runtime files are ephemeral in v1; keep state in the customer's `/storage` or your own backend | Restart, suspend and cancel wipe local files |
| `license`, `source` (proposed) | yes when the software is not yours | SPDX identifier and the repository at the deployed revision | Review checks that the license permits hosting as a service; see §5.4.2 |

```json
// offering.json: open-source tool at cost, provider = the project, seller = UnitySVC Labs
{
  "schema": "offering_v1",
  "name": "open-webui/open-webui",
  "service_type": "container",
  "summary": "Open WebUI, your own instance, over your /ai",
  "description": "One click gives you a private Open WebUI at its own URL, talking to the model you chose in /ai. Runtime files are ephemeral: export chats you want to keep.",
  "logo": "logo.svg",
  "payout_price": { "type": "constant", "price": "0", "description": "Not paid out: the author declined payment" },
  "upstream_access_config": {
    "base": {
      "access_method": "container",
      "spec": "compose.yaml",
      "description": "One user, chat UI over your /ai",
      "resources": { "cpu": "0.5", "memory": "1Gi", "ephemeral_disk": "2Gi" },
      "entries": [ { "name": "web", "service": "open-webui", "port": 8080, "auth": "enrollment_key" } ],
      "customer_access_requests": [
        { "object": "service:ai", "permissions": ["invoke"], "required": true,
          "justification": "The chat UI sends your prompts to the model you chose in /ai; billed to your wallet" }
      ]
    }
  }
}
```

```json
// provider.json: the author, credited on the listing; Labs is the seller, not the provider
{
  "schema": "provider_v1",
  "name": "open-webui",
  "homepage": "https://github.com/open-webui/open-webui",
  "contact_email": "hello@openwebui.com",
  "terms_of_service": "https://github.com/open-webui/open-webui/blob/main/LICENSE",
  "status": "ready"
}
```

```json
// listing.json
{
  "schema": "listing_v1",
  "name": "open-webui/open-webui",
  "display_name": "Open WebUI on unitysvc.app",
  "currency": "USD",
  "list_price": { "type": "channel", "default": "base",
    "channels": { "base": { "type": "one_hour", "price": "0.012", "description": "$0.012 / hour while running ~ at cost | suspend to stop charges" } } },
  "service_options": { "enrollment": { "required": true, "limit_per_customer": 1 } },
  "documents": {
    "Container spec": { "category": "container_spec", "file_path": "compose.yaml" },
    "Getting started": { "category": "getting_started", "file_path": "README.md", "mime_type": "markdown" }
  }
}
```

```yaml
# compose.yaml  (restricted subset: pinned digest, no build, no volumes, no host access)
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui@sha256:…
    ports: ["8080"]
    environment:
      OPENAI_API_BASE_URL: ${UNITYSVC_AI_BASE_URL}
      OPENAI_API_KEY: ${UNITYSVC_ENROLLMENT_KEY}
```

A seller's own SaaS is the same spec with a `payout_price` and tiers priced above cost:

```json
"team": { "access_method": "container", "spec": "compose.yaml", "description": "For a team of up to 100 people",
          "resources": { "cpu": "4", "memory": "8Gi", "ephemeral_disk": "20Gi" },
          "entries": [ { "name": "web", "service": "app", "port": 3000, "auth": "enrollment_key" } ] }
"list_price": { "type": "channel", "default": "base", "channels": {
  "base": { "type": "one_hour", "price": "0.05", "description": "$0.05 / hour ~ about $36 / month" },
  "team": { "type": "one_hour", "price": "0.30", "description": "$0.30 / hour ~ about $216 / month" } } }
"payout_price": { "type": "revenue_share", "percentage": "80", "description": "80% of the price after the platform's compute cost" }
```

#### 5.4.1 Customer-run instance or seller-run instance?

unitysvc.app can run a container in two roles. They look alike on the compute side and are different products.

| | **Customer-run: the container is the product** (T4) | **Seller-run: the container is your server** (then T2 / T3 / T5) |
| --- | --- | --- |
| Who enrolls in the container service | Each customer | You, as your own customer |
| Instances | One per customer enrollment | One (or a few) that you operate |
| Who pays instance time | The customer, at your tier price `P`; you earn `(P − C) × r` | You, at base cost `C`, from your wallet |
| What the customer sees | Their instance's URL, start / suspend / cancel on the enrollment | An ordinary service: a gateway URL, a Me-bound subscription. No container, no instance |
| What the customer pays for | Minutes the instance runs, whether or not they use it | Calls, units of work, or per-customer enrollments, metered or `/bill` |
| Isolation | Each customer's data stays in their instance | Your software is multi-tenant; you keep tenants apart |
| Scaling | The platform adds instances as customers enroll | You pick a bigger tier or run more instances |
| Lifecycle control | The customer | You |
| Can several services share it | No: one instance serves one enrollment | Yes: an API, an alert service and an on-demand job can all run on the one instance |
| Right when | Single-user or single-team software, per-user state, strict isolation, or you don't want to operate anything | A small always-on worker: a runner for Me-bound services that should not live on a laptop cron, a lightweight multi-tenant API, a webhook receiver. Not a model server or a batch farm |
| Listing | The container service, with tiers | The services in front of it; the container service is private |

The seller-run case needs two specs:

1. **A private container service** you never list. Same shape as T4, priced at base cost, with an `entries` item for the API your public services will call, authenticated by a secret of yours rather than a customer key. You enroll in it, start it, and read its instance URL.
2. **The public services**, which are ordinary T2 / T3 / T5 specs whose upstream is that URL.

```json
// 1. offering.json, private: your worker on unitysvc.app
{
  "schema": "offering_v1",
  "name": "acme/worker-host",
  "service_type": "container",
  "summary": "Acme's worker host (private): the trash-day runner and a small API",
  "payout_price": { "type": "constant", "price": "0" },
  "upstream_access_config": {
    "worker": {
      "access_method": "container",
      "spec": "compose.yaml",
      "resources": { "cpu": "1", "memory": "2Gi", "ephemeral_disk": "5Gi" },
      "entries": [ { "name": "api", "service": "app", "port": 8000, "auth": "none" } ]
    }
  }
}
```

```json
// 1. listing.json, private: priced at cost, one instance, not submitted for listing
{
  "schema": "listing_v1",
  "name": "acme/worker-host",
  "display_name": "Acme worker host",
  "currency": "USD",
  "visibility": "private",
  "list_price": { "type": "channel", "default": "worker",
    "channels": { "worker": { "type": "one_hour", "price": "0.03", "description": "$0.03 / hour | base cost" } } },
  "service_options": { "enrollment": { "required": true, "limit_per_customer": 1 } },
  "documents": { "Container spec": { "category": "container_spec", "file_path": "compose.yaml" } }
}
```

```json
// 2. offering.json, public: a small metered API whose upstream is the instance (T2).
//    The same instance runs the cron that serves the T5 trash-day enrollments.
"upstream_access_config": {
  "managed": {
    "access_method": "http",
    "base_url": "{{ instances.worker-host.entries.api }}/schedule",
    "api_key": "${ secrets.ACME_WORKER_KEY }"
  }
}
```

The `{{ instances.<name>.entries.<entry> }}` reference is **proposed**: it binds the upstream to your enrollment's live instance so the URL survives re-placement and restarts. Until it exists, paste the instance URL into `base_url` and update it when the instance moves. The `auth: "none"` entry relies on your app checking `ACME_WORKER_KEY` itself; the platform's private network keeps other instances out.

Two things follow from the table:

- **Pricing is what tells them apart.** A T4 customer pays for time, so an idle instance still costs them; price tiers so that is fair, and expect customers to suspend. A seller-run instance costs you a flat amount, so price the services in front of it by usage and make sure expected usage covers `C`.
- **A seller-run instance is also where T5 runners belong.** A cron that serves Me-bound enrollments can run there instead of on a GitHub Action, with the same leased-key loop.

#### 5.4.2 Hosting software you did not write

Nothing in the platform stops anyone, the author or a third party, from packaging an open-source project as a hosted app and charging for it. Whether they *may* is decided by the project's license and trademarks, not by UnitySVC, so the platform's job is to make the terms visible, check the obvious cases at review, and give authors a say. The rules below are the proposed policy.

| Situation | License allows hosting as a service? | What the listing must do |
| --- | --- | --- |
| Permissive (MIT, Apache 2.0, BSD, MPL) | Yes, including for profit | Attribution and the license text; no further permission needed |
| Copyleft (GPL, LGPL) | Yes | Attribution; offer the source of what you run, including your changes |
| Network copyleft (AGPL) | Yes, with an obligation | The running instance must offer its complete source, at the exact revision and digest you deploy, modifications included. Link it from the listing |
| Source-available with a service restriction (SSPL, Elastic License 2.0, BUSL before its change date, Commons Clause, "non-commercial" licenses) | **No**, not even at cost | Rejected at review unless the publisher holds a commercial license from the author |
| No license file | No | Rejected: no license means no permission |

| Rule | Why |
| --- | --- |
| **Declare `license` and `source`** (proposed fields on the offering): the SPDX identifier and the repository at the revision you build from | Review checks the table above; customers see what they are running |
| **The provider is the author, the seller is you.** `provider.json` names the project (its name, repository and public contact), so the listing credits the author and reads "hosted by Acme". The project's name and the logo it publishes identify the provider; your own branding stays on the seller profile, and nothing may imply the author endorses your hosting | Credit is structural, not a courtesy line in a description. Trademarks are separate from the code license and are the usual reason a project objects, and a listing that names the author as provider is nominative use, not branding |
| **Authors are told and can claim.** When a paid third-party listing of a project goes active, the platform notifies the project (its public contact or repository) and shows the listing as "community-hosted". The author can publish their own listing, which is marked "by the author" and ranked first; ask for a revenue share from the publisher through the platform; or file a dispute where the license or a trademark is breached | Politeness made concrete: authors should not discover a paid listing of their work by accident |
| **UnitySVC Labs hosts at cost only**, with attribution, and hands a listing to the author on request | The platform does not profit from other people's code |
| **A seller-run instance of someone else's software is their business** as long as the license allows it; the same declaration applies to the private container service | Hosting a Postgres or a Redis behind your API is ordinary use |

Whether a paid third-party listing should need the author's consent *beyond* the license is an open question (§7). The proposed answer is no, because open-source licenses already grant that permission and a consent rule would be unenforceable, but with notification, labelling, author precedence and a dispute path in return.

### 5.5 T5. Service on the customer's Me

Your code acts for the customer and charges per unit of work. There may be no customer-facing endpoint: the channel is a list of access requests, optionally with parameters and an `invoke` declaration. You serve it by leasing a key from each enrollment and calling `/notify`, `/email`, `/ai`, `/storage`, `/bill` with it.

**Recipe:** G, H · B.4 with `service:bill` and the surfaces you act on, `params.schema` and `invoke` as needed · A.0 · C.2 with the unit in the description · D.1 · E.3 · F.1, F.3. Plus I: your runner.

| Section | Required | What to put | Why |
| --- | --- | --- | --- |
| `customer_access_requests` | yes | One entry per surface: `object` (`service:notify`, `service:email`, `service:ai`, `service:storage`, `service:bill`, `service:me` with `profile=` options, `resource:room`), `permissions`, `options`, `limits`, `required`, `justification` | The customer approves each before enrolling. The leased key gets exactly these |
| → `service:bill` request | yes for 4C | `permissions: ["charge"]` (+ `refund`, `query`), `options: "max_units_per_charge=N"`, `limits` such as `count_per_day` or `amount_per_month` | Charging is a permission. Limits are the customer's budget and are shown on the enrollment |
| → `justification` | yes, each | One sentence in the customer's words: what you do with it | It is the consent text |
| channel `params.schema` | usually | What the service needs to know: an address, a search query, a lead time | Per-customer configuration without identity |
| channel `invoke` | optional | `input_schema`, `min_interval_seconds`, `expected_latency` | "Try now" on the enrollment page and `/e/<code>/invoke` for the customer's automation; delivered to you as an event |
| `list_price` | yes | `constant` with the unit in the description: `"$0.05 / reminder"`, `"$4 / report"`, `"$2 / month"` | `/bill` charges `units` of this price |
| `payout_price` | yes | `revenue_share` or per unit | Your earning per charge |
| `user_access_interfaces` | no, unless the service also answers calls | Omit for alert-only services | Nothing to call |
| `documents` | yes | A connectivity test that proves your runner can reach the customer's surfaces (`me_connectivity` preset once available), a `getting_started` page | The platform tests the listing; customers learn what to expect |
| `service_options.enrollment` | recommended | `limit_per_customer` | Several addresses, one subscription… |
| your runner | outside the spec | A cron, a GitHub Action or a worker that lists enrollments, leases keys, does the work, calls `/bill` with an `Idempotency-Key`, returns the key | Where the service actually happens |

```json
// offering.json: trash-day reminders from a cron
{
  "schema": "offering_v1",
  "name": "acme/trash-day",
  "service_type": "notification",
  "summary": "A reminder before every trash and recycling pickup at your address",
  "description": "Tell us your address and how many hours' notice you want. We look up the municipal schedule and send a reminder to your notification destinations. One unit per reminder, at most two a day. Use Try now to get the next pickup immediately.",
  "logo": "logo.svg",
  "payout_price": { "type": "revenue_share", "percentage": "80" },
  "upstream_access_config": {
    "alerts": {
      "params": { "schema": { "type": "object", "required": ["address"], "properties": {
        "address": { "type": "string", "description": "Street address the schedule is looked up for" },
        "lead_hours": { "type": "integer", "default": 8, "minimum": 1, "maximum": 48 } } } },
      "customer_access_requests": [
        { "object": "service:notify", "permissions": ["invoke"], "required": true,
          "justification": "Delivers the reminder to your notification destinations" },
        { "object": "service:bill", "permissions": ["charge", "query"], "options": "max_units_per_charge=1",
          "limits": { "count_per_day": 2 }, "required": true,
          "justification": "One unit per reminder sent; at most two a day" }
      ],
      "invoke": { "input_schema": { "type": "object", "properties": { "date": { "type": "string", "format": "date" } } },
                  "min_interval_seconds": 300, "expected_latency": "within 15 minutes" }
    }
  }
}
```

```json
// listing.json
{
  "schema": "listing_v1",
  "name": "acme/trash-day",
  "display_name": "Trash-day reminders",
  "currency": "USD",
  "list_price": { "type": "constant", "price": "0.05", "description": "$0.05 / reminder | about $0.40 a month for weekly pickup" },
  "service_options": { "enrollment": { "required": true, "limit_per_customer": 3 }, "ops_testing_parameters": { "address": "1 Main St, Houston TX" } },
  "documents": { "Getting started": { "category": "getting_started", "file_path": "README.md", "mime_type": "markdown" } }
}
```

An on-demand job is the same type with storage requests and a per-result price:

```json
"customer_access_requests": [
  { "object": "service:storage", "permissions": ["read"], "options": "path=shared/datasets/", "required": true, "justification": "Reads the dataset you point the run at" },
  { "object": "service:storage", "permissions": ["write"], "required": true, "justification": "Writes the finished report into this enrollment's output folder" },
  { "object": "service:bill", "permissions": ["charge"], "options": "max_units_per_charge=1", "required": true, "justification": "One unit per report that completes; failed runs are not charged" } ],
"invoke": { "input_schema": { "type": "object", "required": ["dataset"], "properties": { "dataset": { "type": "string" } } }, "min_interval_seconds": 60, "expected_latency": "5 to 30 minutes" }
"list_price": { "type": "constant", "price": "4.00", "description": "$4 / report | charged when the report lands in your files" }
```

### 5.6 T6. Your own app, billed here

The product is your website. UnitySVC supplies the customer, the enrollment and the money. Two channels: an `external` one the catalog shows and never routes, and a `me_bound` one that holds the leased key your backend uses.

**Recipe:** G, H · B.5 for the site and B.4 with `service:bill` · A.0 · C.2 per seat-month or job · D.1 · E.3 · F.1. Plus I: your sign-in and monthly charge.

| Section | Required | What to put | Why |
| --- | --- | --- | --- |
| `external` channel | yes | `type: "external"`, `url` to your sign-in with a UnitySVC option, `description` | Where the customer goes; probed daily |
| `me_bound` channel | yes | `customer_access_requests` with `service:bill` (`charge`, `refund`, `query`; `limits` matching your plan) and whatever else your app needs (`service:notify`, `service:email`, `service:me` with `profile=` options) | The leased key your backend holds per customer |
| `list_price` | yes | `constant` per seat-month or per job, unit in the description | What one `/bill` unit is |
| `payout_price` | yes | `revenue_share` | Your earning |
| `user_access_interfaces` | no | Omit | Nothing to call on the gateway |
| `service_options.enrollment` | yes | `required: true`, usually `limit_per_customer: 1` | One seat or account per enrollment |
| your backend | outside the spec | "Use your UnitySVC account" sign-in that accepts an enrollment; a monthly job that charges one unit with `Idempotency-Key: seat-<month>-<enrollment>` | Links your user record to the enrollment and bills it |
| double billing | note in `description` | Say that UnitySVC customers are billed here and not by card at your site | Avoid charging the same person twice |

```json
// offering.json
{
  "schema": "offering_v1",
  "name": "acme/studio",
  "service_type": "saas",
  "summary": "Collaborative design studio, paid from your UnitySVC wallet",
  "description": "Sign in at studio.acme.example with “Use your UnitySVC account”. One seat-month is charged on the 1st to this enrollment; cancel the enrollment to stop. UnitySVC customers are never asked for a card at Acme.",
  "logo": "logo.svg",
  "payout_price": { "type": "revenue_share", "percentage": "85" },
  "upstream_access_config": {
    "web": { "type": "external", "url": "https://studio.acme.example/login?via=unitysvc",
             "description": "Sign in at studio.acme.example with “Use your UnitySVC account”" },
    "billing": {
      "customer_access_requests": [
        { "object": "service:bill", "permissions": ["charge", "refund", "query"], "options": "max_units_per_charge=1",
          "limits": { "count_per_month": 1 }, "required": true,
          "justification": "One seat-month per calendar month while your seat is active; refunded pro rata if you cancel" },
        { "object": "service:notify", "permissions": ["invoke"], "required": false,
          "justification": "Tells you when an export finishes" }
      ]
    }
  }
}
```

```json
// listing.json
{
  "schema": "listing_v1",
  "name": "acme/studio",
  "display_name": "Acme Studio",
  "currency": "USD",
  "list_price": { "type": "constant", "price": "19.00", "description": "$19 / seat-month | billed on the 1st by Acme Studio" },
  "service_options": { "enrollment": { "required": true, "limit_per_customer": 1 } },
  "documents": { "Getting started": { "category": "getting_started", "file_path": "README.md", "mime_type": "markdown" } }
}
```

The monthly charge, from your backend with the enrollment's leased key:

```bash
curl -X POST "$API_GATEWAY_BASE_URL/bill" -H "Authorization: Bearer $LEASED_KEY" \
  -H "Idempotency-Key: seat-2026-12-$ENROLLMENT" \
  -d '{"units": 1, "description": "Seat, December 2026"}'
```

### 5.7 T7. Human services

No code. The enrollment is the engagement, `/bill` is the timesheet, a chat line is the office. The customer's approved monthly amount is the budget cap, visible to both sides.

**Recipe:** G, H · B.5 for booking and B.4 with `service:bill`, `resource:room`, `service:email`, `service:me` · A.0 · C.2 per hour or deliverable · D.1 · E.3 · F.1.

| Section | Required | What to put | Why |
| --- | --- | --- | --- |
| `external` channel | yes | `type: "external"`, `url` to your booking page, `description` of how sessions happen | How the work is delivered |
| `me_bound` channel | yes | `service:bill` with `max_units_per_charge` (hours per session) and `limits.amount_per_month`; `resource:room` (`create`, `kind=chat&max_members=…&max_retention=…`) for the chat line; `service:email` for deliverables; `service:me` `read` with `profile=name` so notes are addressed | Billing, conversation and deliverables all through the one enrollment |
| channel `params.schema` | recommended | A one-line project description, preferred times | Scopes the engagement without a call |
| `list_price` | yes | `constant` per hour or per deliverable, unit in the description | What one `/bill` unit is |
| `payout_price` | yes | `revenue_share`, typically high | Your earning |
| `service_options.enrollment` | yes | `required: true`, `limit_per_customer: 1` | One engagement per customer |
| `documents` | yes | `getting_started`: how booking, sessions, notes and charges work; your credentials | There is no test to run, so the page is the trust signal |
| how you work | outside the spec | After each session: `POST /bill` with the hours and a description, from the CLI or a script with the leased key; reply to the room from Discord, Slack or email | The customer sees each charge on the enrollment |

```json
// offering.json
{
  "schema": "offering_v1",
  "name": "acme/bioinformatics-consulting",
  "service_type": "consulting",
  "summary": "RNA-seq and variant-calling help from a working bioinformatician",
  "description": "Book a session; we meet by video or work asynchronously in the chat line. Hours are charged after each session with a description, never above the monthly amount you approve. First 15-minute call free.",
  "logo": "logo.svg",
  "payout_price": { "type": "revenue_share", "percentage": "90" },
  "upstream_access_config": {
    "engagement": { "type": "external", "url": "https://cal.acme.example",
                    "description": "Sessions by video call or email; book at cal.acme.example" },
    "timesheet": {
      "params": { "schema": { "type": "object", "properties": {
        "project": { "type": "string", "description": "One line on what you need help with" } } } },
      "customer_access_requests": [
        { "object": "service:bill", "permissions": ["charge", "refund", "query"], "options": "max_units_per_charge=8",
          "limits": { "amount_per_month": "2000.00" }, "required": true,
          "justification": "Hours worked, charged after each session with a description; never more than $2,000 a month unless you raise the limit" },
        { "object": "resource:room", "permissions": ["create"], "options": "kind=chat&max_members=5&max_retention=2592000", "required": false,
          "justification": "A chat line between us for questions between sessions; read and reply from Discord, Slack, email or the Rooms page" },
        { "object": "service:email", "permissions": ["invoke"], "required": false,
          "justification": "Sends session notes and deliverables to your inbox" },
        { "object": "service:me", "permissions": ["read"], "options": "profile=name", "required": false,
          "justification": "So invoices and session notes are addressed to you" }
      ]
    }
  }
}
```

```json
// listing.json
{
  "schema": "listing_v1",
  "name": "acme/bioinformatics-consulting",
  "display_name": "Bioinformatics consulting (RNA-seq, variant calling)",
  "currency": "USD",
  "list_price": { "type": "constant", "price": "150.00", "description": "$150 / hour | charged after each session; 15-minute intro call free" },
  "service_options": { "enrollment": { "required": true, "limit_per_customer": 1 } },
  "documents": { "How it works": { "category": "getting_started", "file_path": "README.md", "mime_type": "markdown" } }
}
```

### 5.8 T0. Open-source app on the customer's key

You wrote an app that people run themselves: on a laptop, on their own server, or in their own unitysvc.app instance. It talks to UnitySVC with a key **the customer creates on their own account**, so the app has no backend, you never hold a key, never see the customer, and bill nothing. What the app uses (`/ai`, `/notify`, `/log`, …) is paid by each user from their own wallet.

You want two things from UnitySVC: to be **found**, and to know **how to talk to your users' Me**. Both are below. Selling comes later, if ever: the same listing with a `service:bill` request becomes T5 or T6, and existing users link their installs.

**Wizard path:** 1C (the customer runs it) / 2D (the app acts through the customer's Me, driven by the customer's own copy) / 3A for you, with B.4 requests declared for the app / 4A.

**Recipe:** G, H · B.5 for the repository and install page, plus a B.4 channel listing what the app uses, with the key **issued to the customer** · A.0 · C.4 · D.3 · E.3 · F.1.

| Section | Required | What to put | Why |
| --- | --- | --- | --- |
| `external` channel | yes | `type: "external"`, `url` of the repository or install page, `description` | Where the customer gets the app; probed daily like any external channel |
| `me_bound` channel | yes | `customer_access_requests` naming what the app uses, each with a `justification`; `key_holder: "customer"` (proposed) so that enrolling issues the key to the customer instead of leasing it to you | The listing's **Connect** creates an enrollment and shows the customer a key to paste into the app, with exactly these grants. Without it, users create a key by hand (below) |
| `list_price`, `payout_price` | yes, zero | `C.4` with `"Free | you pay for what the app uses from your wallet"`; `D.3` | Nothing is billed for the app itself |
| `user_access_interfaces` | no | Omit | The platform never routes to the app |
| `documents` | yes | `getting_started`: install, where to paste the key, what each grant is for; link the policy template | There is no gateway call to test |
| `service_options.enrollment` | yes | `required: true`, `limit_per_customer` for several installs | One key per install |
| a policy template in your repository | recommended | `unitysvc-policy.json`: the same requests in the policy grammar, with a `schema_version` | A user who found you outside the catalog pastes it into **Create key** and gets a key with the right grants and limits; templates may not ask for `*`, `service:bill` or secrets |

```json
// offering.json
{
  "schema": "offering_v1",
  "name": "acme/paper-monitor",
  "service_type": "notification",
  "summary": "Open-source monitor that tells you when new papers match your research topics",
  "description": "Runs on your machine or in your own unitysvc.app instance. Give it a key from this page (Connect) or create one with the policy template in the repository. It reads your research topics from Me, summarizes new matches with your /ai, and sends you a daily notice. Free: you pay only for the /ai calls it makes, from your wallet.",
  "logo": "logo.svg",
  "tags": ["open-source", "research"],
  "payout_price": { "type": "constant", "price": "0" },
  "upstream_access_config": {
    "source": { "type": "external", "url": "https://github.com/acme/paper-monitor",
                "description": "Install from GitHub; the README shows where the key goes" },
    "app": {
      "key_holder": "customer",
      "customer_access_requests": [
        { "object": "service:me", "permissions": ["read"], "options": "profile=research&intents=research", "required": true,
          "justification": "Reads your research topics to decide which papers match" },
        { "object": "service:ai", "permissions": ["invoke"], "required": true,
          "justification": "Summarizes each matching paper with the AI you chose, billed to your wallet" },
        { "object": "service:notify", "permissions": ["invoke"], "required": true,
          "justification": "Sends you the daily list of matches" },
        { "object": "service:log", "permissions": ["write"], "options": "log_level=info", "required": false,
          "justification": "Records what it checked so you can see it worked" }
      ]
    }
  }
}
```

```json
// listing.json
{
  "schema": "listing_v1",
  "name": "acme/paper-monitor",
  "display_name": "Paper Monitor (open source)",
  "currency": "USD",
  "list_price": { "type": "constant", "price": "0", "description": "Free | you pay for the /ai calls it makes, from your wallet" },
  "service_options": { "enrollment": { "required": true, "limit_per_customer": 3 } },
  "documents": { "Getting started": { "category": "getting_started", "file_path": "README.md", "mime_type": "markdown" } }
}
```

```json
// unitysvc-policy.json, in the repository: the same requests for users who create a key by hand
{
  "schema_version": 1,
  "name": "paper-monitor",
  "grants": [
    { "object": "service:me", "permissions": ["read"], "options": "profile=research&intents=research" },
    { "object": "service:ai", "permissions": ["invoke"] },
    { "object": "service:notify", "permissions": ["invoke"] },
    { "object": "service:log", "permissions": ["write"], "options": "log_level=info" }
  ],
  "limits": { "spend": { "daily": "1.00" } }
}
```

**Someone else may host it.** If your app can run on unitysvc.app, any seller may package it as a hosted app (T4) and charge for it, within your license. §5.4.2 says what the platform requires of them: a declared license and source, your project named as the provider so you are credited, and notification to you, after which you can publish the listing yourself, marked "by the author", or ask for a share. If you want to be the one who hosts it, publish the T4 listing first.

#### How your app talks to the customer's Me

One key, sent as `Authorization: Bearer <key>` to the API gateway, or as the SMTP password for email. Every surface is answered by the gateway itself at a fixed path; the app never chooses a provider, a destination or an address. A call the key's grants do not cover is refused with `403`: tell the user which grant to add rather than failing silently.

| Surface | Grant | Call | What happens |
| --- | --- | --- | --- |
| **AI** | `service:ai` `invoke`; option `service=<catalog service>` pins a model | `POST ${API_GATEWAY_BASE_URL}/ai/chat/completions`, OpenAI format; any `model` value | Answered by the model the user chose as their AI preference, paid from their wallet. Streaming works. Use the OpenAI SDK with `base_url` set to `…/ai` |
| **Notify** | `service:notify` `invoke` | `POST ${API_GATEWAY_BASE_URL}/notify` with `{"title", "body", "type", "format"}` | Shown in the user's notifications and forwarded to their destination (email, Discord, push…). Free; a paid destination is billed to the user as itself |
| **Email** | `service:email` `invoke` | SMTP to `${SMTP_GATEWAY_BASE_URL}`, username `email`, password the key | Delivered to the user's verified address; you never learn it. Replies come back the same way |
| **Me** | `service:me` `read` (or `write`); options `profile=<paths>`, `intents=<categories>`, `preferences=<categories>` | `GET ${API_GATEWAY_BASE_URL}/me/profile`, `/me/intents`, `/me/preferences` | Returns only what the grant's options select and the user chose to share. A missing option grants nothing |
| **Log** | `service:log` `write` (and `read`); option `log_level=` | `POST ${API_GATEWAY_BASE_URL}/log` with one entry `{"level", "message", "attributes"}` or up to 100 | Recorded in the user's activity log: under the enrollment when the key came from Connect, otherwise in the account's general log |
| **Storage** | `service:storage` `read` / `write` | `POST ${API_GATEWAY_BASE_URL}/storage/list`, `/get`, `/put`, `/post`, `/delete`; bytes move on presigned URLs | A folder of the user's own files that belongs to the enrollment. A key from Connect reaches its own folder; a hand-made key must name an enrollment with `X-UnitySVC-Enrollment` |

Three habits make an app a good citizen:

- **Ask for the least.** Each request is consent text the user reads. An app that only needs to notify asks for `service:notify`, not `service:me`.
- **Ship the policy template** and keep it equal to the listing's requests, so a user who installs from GitHub and a user who clicked Connect end up with the same key.
- **Spend within the user's limits.** A hand-made key may carry a daily spend cap; `/ai` answers `429` or `402` when it is reached. Back off and tell the user.

When you want revenue, add a `service:bill` request and a price and the listing becomes T5 (you run it for them) or T6 (they keep running it, you charge for something). Users who already run your app are offered "Link to acme/paper-monitor"; their keys and history carry over.

## 6. What each type needs from the platform today

| Type | Ready now | Depends on |
| --- | --- | --- |
| T2 Metered gateway, T3 Per-customer gateway | Yes | — |
| T0 Open-source app | Hand-made keys with grants; the Me surfaces (`/ai`, `/notify`, `/email`, `/me`, `/log`, `/storage`) | Connect issuing the key to the customer; policy templates; "Link to" when the author starts selling |
| T1 Ads only | `external` channels per the live docs; daily probe | Confirm the declaration fields in the core release that carries `external` |
| T5, T6, T7 (`/bill`, `me_bound`) | `bill` service and `customer_access_requests` exist; grant limits are being enforced | Limit enforcement ([unitysvc#2731](https://github.com/unitysvc/unitysvc/issues/2731)); `invoke` for "Try now" (the invoke design); `/storage` grants (the storage design, deferred); a Me connectivity preset |
| T4 Hosted app | Prototype runner and staging cluster | Core contract [unitysvc#2999](https://github.com/unitysvc/unitysvc/issues/2999), spec [#3000](https://github.com/unitysvc/unitysvc/issues/3000), lifecycle and billing [#3001](https://github.com/unitysvc/unitysvc/issues/3001), customer release gates [#3007](https://github.com/unitysvc/unitysvc/issues/3007) |

## 7. Open questions for the guide

1. **Metered price plus `/bill` on one listing.** A multi-tenant API that also charges per run (T3 + T5) needs either two prices on one listing or two services. Decide the rule before the guide promises either.
2. **External channel declaration.** This draft uses `"type": "external"` with `url` and `description`; confirm the field names once the core release that carries `external` and `me_bound` is published.
3. **Container channel fields** (`access_method: "container"`, `resources`, `entries`, `spec`, the `container_spec` document category): placeholders until [unitysvc#2999](https://github.com/unitysvc/unitysvc/issues/2999) / [#3000](https://github.com/unitysvc/unitysvc/issues/3000) fix the names.
4. **Seller-run instances.** A private container listing (`visibility: "private"` is a placeholder), an entry authenticated by the seller rather than a customer key, and a `{{ instances.<name>.entries.<entry> }}` upstream reference are all proposed in §5.4.1 and exist nowhere yet. The alternative is pasting the instance URL into `base_url`.
5. **Keys issued to the customer (T0).** `key_holder: "customer"` on a Me channel, the listing's Connect flow and the "Link to" upgrade are proposed; the hand-made key with a pasted policy template is the path that exists in design today.
6. **A test for Me-bound services.** T5 to T7 have no gateway call to probe. Decide what the daily test is: a `me_connectivity` preset that leases a key and lists its grants, or no test and a manual review.
7. **Labs as seller.** Which provider open-source listings live under (`labs/…` as OpenLine does), and whether authors can be credited on the listing without being paid.
8. **Consent for paid third-party hosting.** §5.4.2 proposes license plus notification, labelling, author precedence and disputes, with no consent requirement beyond the license. Decide whether that is enough, and whether `license` and `source` become required fields for every container offering.
9. **Provider = author and service names.** Service names are `provider/service`, so two sellers hosting the same project would both want `open-webui/open-webui`. Decide whether names are unique per seller (and the catalog shows the seller), or whether hosted listings take a seller-qualified name such as `open-webui/open-webui@acme`. The catalog also needs to show provider and seller separately, with "by the author" when they coincide.
