# LLM service metadata contract (`ModelSpec`) + universal template

**Goal:** replace 15 divergent, partly-inaccurate per-provider populate scripts
and templates with (a) one fixed uniform metadata contract each script yields,
and (b) one universal template that renders any provider from that contract.
Foundation for #1768 R11 (system templates).

## Why

Today each `scripts/update_params.py` stuffs `offering.details` with whatever it
can scrape from litellm/HF/openrouter via **fuzzy substring matching** — most of
it (`max_tokens`, `mode`, `litellm_provider`, `owned_by`, `object`,
`metadata_sources`, `parameter_count`) is read by nothing and is often wrong
(the fuzzy fallback attaches a *different* model's numbers). Only a few fields
are actually consumed. A fixed contract + accurate, tiered acquisition fixes
both the noise and the accuracy, and makes one template possible.

## `ModelSpec` — the uniform iterator output

Each provider's populate script yields dicts of exactly this shape. Required
keys are always present; optional keys are present-or-`null`.

### Required — must resolve to a real value (T3 permitted; see tiers)
| Field | Type | Notes |
|---|---|---|
| `model_id` | str | routing identity, from `/models` |
| `display_name` | str | from `/models` or derived from id |
| `service_type` | str | `llm` / `embedding` / … |
| `context_length` | int\|null | schema-required key; `by_context_length` routing |
| `price` | obj\|null | `{input_per_1m, output_per_1m, cached_input_per_1m?}` upstream reference price — description + managed resale |

### Required key, best-effort value (T2 exact only, else null — no T3)
| `parameter_count` | int\|null | closed models usually null |

### Optional (T1/T2 only, never T3; omit/null if absent)
| `capabilities` | list | vision, function_calling, … |
| `max_output_tokens` | int | |
| `description` | str | rich; else template synthesizes |
| `icon` | str | usually provider-level (provider.json) |

### Provider-static (from provider config, NOT per-model, NOT collected)
`provider_name`, `provider_display_name`, `api_base_url`, `env_api_key_name`,
`llm_translator` (dialect direction), `allow_managed`, `base_url_path_style`.

`input_formats`/`output_formats` are template constants (fixed by the dialect +
translator), not `ModelSpec` fields.

## Acquisition tiers (per field, low→high effort)

- **T1** — provider `/models` (authoritative, cheap, always present)
- **T2** — structured catalogs: litellm price/context JSON **exact-key match
  only**, openrouter models. **No fuzzy substring matching.**
- **T3** — web search **restricted to the provider's own website/pricing page**.
  Allowed only to fill an unresolved **required** field (`price`,
  `context_length`). Never for optional fields.

## `status: pending` rule

A model whose **required** value (`price` or `context_length`) can't be resolved
by T1–T3 is emitted with `status: "pending"` and `null` for the missing value —
uploaded but **not published**, flagged for human investigation — rather than
silently dropped or shipped with a wrong guess. Fully-resolved models are
`ready`.

## Universal template

`offering.json.j2` + `listing.json.j2` + the two Anthropic code examples,
provider-agnostic, consuming `ModelSpec` + provider-static params. This is
groq's template generalized: `base_url_path_style` and `llm_translator` become
params so the exact same files serve every provider (OpenAI-compat → 
`anthropic_to_openai`; Anthropic-native → `openai_to_anthropic`).

- Lean `details`: only `input_formats`/`output_formats` + `context_length` +
  `parameter_count`. (Already implemented on groq PR #65.)
- Channels: `byok` always; `managed` when `allow_managed`.
- 3-paragraph synthesized description; `sleep_after_test` on executed docs.

## Rollout

1. Land `ModelSpec` + acquisition driver in `unitysvc-sellers`
   (`model_data.py` gets an exact-match resolver + provider-website T3; a new
   `build_model_spec()` driver).
2. Refactor each provider `update_params.py` into a thin adapter: provider
   config + `/models` fetch → `build_model_spec()` → yield `ModelSpec`.
3. Adopt the universal template (local copy per repo now; system template later).
4. CI `populate-services` regenerates params (provider keys are GH secrets).

## R11 (later)

Promote the universal template to a backend system-template pool; repos switch
from local `templates/` to `params/` referencing it.
