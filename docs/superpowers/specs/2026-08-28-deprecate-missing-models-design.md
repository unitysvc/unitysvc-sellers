# Deprecating models that upstream no longer serves

**Date:** 2026-08-28
**Status:** design, approved in chat; not yet implemented
**Affects:** `unitysvc-sellers` (SDK + upload), all 17 `unitysvc-services-*` LLM repos

## Problem

`parasail/zai-org/GLM-5.1` sat in the production catalog as an active,
public service for weeks after Parasail retired the model. Every one of its
15 tests failed with HTTP 404 — `Deployment zai-org/GLM-5.1 doesn't exist or
isn't accessible` — and nothing removed it. Three more parasail services are
in the same state.

A retirement should be caught by the daily populate run. It is not, and the
reason is not "the feature is switched off in those repos". The feature does
not execute anywhere.

### Why nothing catches it today

Deprecation-on-absence exists only on `populate_from_iterator`
(`template_populate.py`), the legacy path that writes **expanded service
folders**. Its `deprecate_missing` argument defaults to `True` and calls
`_deprecate_service()` on any folder the iterator did not yield.

All 17 repos with a populate script have since migrated to **param
files**, written by
`write_params_from_iterator` (`params_render.py`). That function has no
deprecation concept at all. It has `prune_missing`, which either deletes a
stale entry or keeps it — and that loop iterates
`_expanded_service_folders(output_dir)`, which finds directories containing
`offering.json` or `service.json`.

After migration there is essentially nothing left for it to find:

| repo | service param files | `.override.json` | sidecars | expanded folders |
| --- | --- | --- | --- | --- |
| ollama | 235 | 11 | 235 | 0 |
| huggingface | 144 | 6 | 144 | 0 |
| parasail | 84 | 14 | 84 | 0 |
| bedrock | 37 | 0 | 37 | 0 |
| openai | 26 | 0 | 26 | 0 |
| cohere | 16 | 0 | 16 | **1** |
| the other 11 | 146 | 5 | 146 | 0 |

So the loop's body never runs. `prune_missing=True`, which bedrock and
ollama explicitly opted into, is a no-op in both. **Dead in 16 of the 17
repos.** The exception is cohere's single un-migrated folder
(`cohere/embed-v4.0`).

### The second defect, which a naive fix would ship

The iterator yields **post-filter** models. `unitysvc-services-openai`'s
script drops roughly fifteen substrings (`embed`, `whisper`, `tts`,
`realtime`, `dall-e`, `image`, `sora`, `moderation`, `-pro`, `instruct`,
`preview`, …) and prefers alias ids over dated snapshots. Repos also carry
curated entries that never appear in a provider's enumeration.

"Missing from the iterator" therefore does **not** mean "missing from
upstream". Comparing against what the iterator yielded — which is what
`deprecate_missing` does today — would deprecate every deliberately filtered
family and every curated entry. That is why `prune_missing` defaults to
keeping, with the comment *"curated; not in live source … so its service_id
is never lost."*

The comparison has to be against the **raw enumeration, before filtering**.

## Goals

1. A model absent from a provider's raw `/models` enumeration is marked
   deprecated in its repo, in an auto-generated PR a human reviews.
2. On merge, the service is **deprecated** if it is live, or **deleted** if
   it never went live.
3. A malformed or unauthorised enumeration fails the workflow loudly rather
   than deprecating a catalog.

### Non-goals

- Automatic un-deprecation when a model returns. A human re-runs populate.
- Any change to non-LLM repos (`smtp`, `s3`, `mcp`, `ntfy`, …), which have
  no populate script.
- Provider-side enumeration adapters in the SDK. Scripts already call their
  own `/models`; the SDK stays transport-agnostic.

## Design

### Part 1 — SDK: real deprecation in `write_params_from_iterator`

One new keyword argument, and one removed (`name_field` — see the contract
and sequencing below):

```python
def write_params_from_iterator(
    iterator, output_dir, *,
    template=None,
    prune_missing=False,
    upstream_names: set[str] | None = None,
) -> dict[str, int]:
```

**`upstream_names`** — the set of **service names**, in the same namespace as
the contract below, that the provider's raw (pre-filter) enumeration maps to.
`None` (default) preserves today's behaviour exactly, so rollout is per-repo
and explicit.

#### The iterator contract

Every iterator MUST yield `service_name` **explicitly**, and it MUST equal
the service's location under `specs/`:

```
specs/<SERVICE_NAME>.json                 # param file
specs/<SERVICE_NAME>/offering.json        # expanded folder
```

`write_params_from_iterator` **requires** it. A yielded dict without
`service_name` is an error naming the offending entry — not the silent skip
it is today. There is no fallback key and no `name_field` argument: a
resolution order is a second way for the same value to arrive, which is the
ambiguity this contract exists to remove.

It also validates the value: if `_sanitize_dirname(service_name) !=
service_name`, raise `ParamRenderError`, rather than silently writing to a
path that no longer equals the name it was asked for.

Templates stop recomputing the name too:

```jinja
"name": "{{ provider_name }}/{{ offering_name }}"   ->   "name": "{{ service_name }}"
```

`service_name` is already in the render context at both call sites, derived
from the param file's own path:

```python
ctx = {"name": service_name, "service_name": service_name,
       "provider_name": service_name.split("/")[0], **parameters}
```

so `listing.name` becomes equal to the path *by construction* instead of by
a per-repo expression that can drift from it. No SDK change is needed to
enable this.

That edit should be a **no-op on rendered output in every repo** — which is
how it gets verified: render each repo before and after and diff. A repo
whose output changes had a latent name/path divergence, and finding it is
the point.

**Why explicit, rather than reconstructed.** The service name is currently
computed in three independent places that agree only by convention:

1. the iterator, for the file path — `"name": f"{PROVIDER_NAME}/{model_id}"`
2. the template, for `listing.name` — a per-repo Jinja expression
3. `params_render`, which re-derives `provider_name` for the template as
   `service_name.split("/")[0]` (it is stripped from `parameters` by
   `_PATH_DERIVED_KEYS`, being path-derived)

Those template expressions **already disagree in form**:

| repo | `listing.name` template |
| --- | --- |
| nebius, parasail, openai, … | `{{ provider_name }}/{{ offering_name }}` |
| **fireworks** | `{{ provider_name }}/{{ model }}` |

Fireworks had to differ: its `offering_name` is the full upstream id
`accounts/fireworks/models/kimi-k2p7-code`, so the common expression would
render `fireworks/accounts/fireworks/models/kimi-k2p7-code` — not the
`fireworks/kimi-k2p7-code` its files are actually named.

So there is no generic rule that reconstructs a service name from
parameters, and any attempt to infer one is wrong for at least one repo
today. The only unambiguous source is the iterator stating it. Requiring
`service_name` collapses three computations into one authoritative value
that the path, `listing.name`, and `upstream_names` all derive from.

**Cost today: none.** `_sanitize_dirname` is
`name.strip("/").replace(":", "_")` and is a no-op on every name in every
repo — no path anywhere is a sanitized colon (the three `_` in nebius are
genuine, as in `MiniCPM-V-4_5`), and ollama, the one provider whose upstream
ids use `:`, already normalises `:` → `-` in its own script before naming.
Every iterator already yields a `name`; this makes the guarantee explicit
and checked instead of assumed. Silent sanitisation is precisely what would
break it later: a future `llama3:8b` would land at `llama3_8b` and every
name-to-path comparison would quietly miss.

#### Sequencing: this is a breaking change to a shared, unpinned dependency

Requiring `service_name` and dropping `name_field` breaks every script that
does not yet yield it. That is worse than a normal breaking change here,
because the populate workflow is **shared and unpinned**:

```yaml
# unitysvc-labs/.github/.github/workflows/seller-populate-services.yml
pip install "unitysvc-sellers>=0.2.25"
```

All 17 repos resolve the same version, so a strict release reaches every one
of them on the next 02:00 cron. There is no per-repo staging of the SDK
without first parameterising that workflow.

So the scripts move first, and they can, because a dict may carry **both**
keys:

1. **Every script yields `service_name` alongside its existing `name`**, same
   value. Compatible with the SDK in production today, which reads `name`;
   `_PATH_DERIVED_KEYS` already strips both, so no param file changes by a
   single byte. 17 independent PRs, no coordination, nothing to break.
   Verified per repo by re-running populate and confirming an empty diff.
2. **Release the strict SDK** — requires `service_name`, no `name_field`.
   Every script already satisfies it, so the cron that picks it up is a
   no-op. Minor-version bump with the break called out.
3. **Drop `name` from the scripts.** Cleanup, one PR each, no deadline.

Templates are independent of all three and can change whenever: the render
context already supplies `service_name`.

The transitional duplication lives in the scripts for one step, and never in
the SDK. There is still no resolution order in shipped code.

#### Why the service name, and not a model-id parameter

The service name already *is* the identity. The write loop does
`rel = _sanitize_dirname(<the yielded name>)` and writes
`output_dir/<rel>.json`, and `_PATH_DERIVED_KEYS = ("name", "service_name",
"provider_name")` strips those keys out of `parameters` precisely because
the path carries them. Matching on anything else invents a second identity
beside the one the module already maintains.

An earlier draft of this design compared a model-id parameter
(`offering_name`, with per-repo overrides). The repo data says that is both
unnecessary and unsafe:

- **fireworks** needs no override — its `offering_name` already *is* the
  full upstream id, `accounts/fireworks/models/kimi-k2p7-code`.
- **bedrock** would have been actively broken by one. Its
  `converse_model_id` is `None` for `zai.glm-4.6` and version-suffixed
  (`openai.gpt-oss-120b-1:0`) where `offering_name` is
  `openai.gpt-oss-120b`. Comparing on it would have deprecated live
  services.

A per-repo field table is a config axis that can be set wrongly, silently,
in a direction that retires working services. The name cannot: it is how the
file got its path.

The script keeps ownership of the id→name mapping, which it already performs
when it yields (fireworks: `accounts/fireworks/models/X` → `fireworks/X`).
It applies that same mapping to the unfiltered enumeration.

#### What counts as a service

`output_dir` holds four kinds of `.json`. Two carry a service identity, two
do not:

| file | count | contributes a name? |
| --- | --- | --- |
| `<NAME>.json` param file | 688 | **yes** → `<NAME>` |
| `<NAME>/{offering,listing,service,provider}.json` expanded folder | 1 repo | **yes** → `<NAME>` |
| `<NAME>.service.json` identity sidecar | 688 | no |
| `<NAME>.override.json` companion | 36 | no |

Because the contract puts both service shapes in one namespace, the pass
handles them uniformly — including cohere's single un-migrated
`cohere/embed-v4.0` folder, which needs no special case.

The override companions matter: 36 exist across parasail (14), ollama (11),
huggingface (6), groq (2), mistral (2) and nebius (1). A naive `*.json` glob
treats each as a service with no upstream match and marks it deprecated.

#### Algorithm

Runs after the write loop, only when `upstream_names is not None`:

1. **Collect local names.** Walk `output_dir` for both service shapes,
   applying the exclusions above. A param file contributes its path minus
   `.json`; an expanded folder contributes its directory path.
2. **Validate the enumeration — hard failure.** Raise
   `UpstreamEnumerationError`, writing nothing, when either holds:
   - `upstream_names` is empty, or
   - it is disjoint from the local names.

   Zero overlap with a catalog we already publish means the call was wrong —
   wrong key, wrong tier, wrong endpoint, a wholesale rename — not that
   every model retired at once. An admin investigates.
3. **Mark the missing.** For each local name absent from `upstream_names`,
   set `status = "deprecated"` — in `parameters` for a param file, in
   `offering.json`/`listing.json` for an expanded folder (what
   `_deprecate_service` already does). Idempotent: one already `deprecated`
   is counted, not rewritten.
4. **Report.** Extend the stats dict with `deprecated` and
   `already_deprecated`, and name each affected service so the job log and
   the PR body both carry it.

What the iterator yielded is never consulted — only committed local names
against raw upstream names. A model the script filters out is still in
`upstream_names`, so it is never marked. That is the defect described above,
and step 4 is where it would otherwise land.

`parameters.status` needs no schema change: `status` is already a parameter
in every repo and `deprecated` is already in use (parasail 2, mistral 2).
`specs.py` folds it into the service status via `draft > deprecated > ready`.

#### Curated entries

A hand-curated model that legitimately never appears upstream is
indistinguishable from a retired one, and would be marked. Two mitigations,
in order:

- The PR review is the gate. These are rare, and a reviewer who knows the
  entry is curated drops that hunk.
- If a repo accumulates enough to be annoying, add an explicit
  `parameters.curated: true` opt-out that step 3 skips.

Ship the first. Add the second only when a repo actually needs it.

### Part 2 — Upload: deprecate if live, delete if not

The backend's seller transition map is the constraint, not a preference:

```
active    -> [deprecated]      # the only edge into deprecated
draft     -> [pending]
pending   -> [draft, rejected]
rejected  -> [draft, pending]
review    -> [draft]
suspended -> [pending]
```

`active` is the only status that can become `deprecated`. A pending, draft,
review or rejected service **cannot** be deprecated, so deletion is the only
way to retire it. Hence: deprecate if live, delete if not.

At upload, for each spec whose computed service status is `deprecated`,
resolve the remote service (sidecar `service_id`, else name) and:

| remote status | action |
| --- | --- |
| `active` | `PATCH` status → `deprecated` |
| `pending`, `draft`, `review`, `rejected`, `suspended` | `DELETE` |
| already `deprecated` | nothing |
| not found | nothing |

Both operations already exist as seller endpoints and are already wrapped by
`usvc seller services deprecate` and `usvc seller services delete`. The work
is wiring the upload path to call them, plus a summary line per service.

> **Open item to confirm during implementation.** I verified the transition
> map and the two endpoints. I did **not** find code showing that ingest
> auto-flips an `active` service when it receives an offering carrying
> `status: deprecated`. This design assumes it does **not** and drives both
> actions client-side. Confirm on staging first — upload a spec marked
> deprecated against an active service and read back its status. If ingest
> already handles the `active` case, implement only the delete half.

### Part 3 — Failure propagation

Already works; no workflow change needed. Verified end to end:

`UpstreamEnumerationError` → script exits non-zero → `specs populate`
accumulates `total_failed` and raises `typer.Exit(code=1)` → the workflow's
populate step runs under `set -euo pipefail` and fails → subsequent steps
have no `if: always()`, so **`Create Pull Request` is skipped entirely**.

A bad enumeration therefore produces a red build and no PR — not a PR full
of wrong deprecations. The red scheduled run is the admin alert.

One caveat worth noting during rollout: `specs populate` catches a failing
populator, continues to any others, and exits 1 at the end. Correct for the
overall exit code, and every repo has a single populator today.

### Part 4 — Rollout

Per repo, one edit to `services/scripts/update_params.py`: derive service
names from the raw enumeration the script already fetches, and pass them.

```python
raw = fetch_models()                       # already happens
# The same id -> service-name mapping the script already applies when it
# yields, but over the UNFILTERED enumeration.
upstream_names = {service_name_for(m) for m in raw}

# The yield carries service_name (added in sequencing step 1, alongside
# `name`; `name` is dropped in step 3):
#   {"service_name": f"{PROVIDER_NAME}/{model_id}", ...}

write_params_from_iterator(
    iter_models(raw),                      # unchanged, still filters
    output_dir=SPECS_DIR,
    upstream_names=upstream_names,
)
```

No per-repo configuration: every repo passes the same argument, and the
mapping stays in the script that already owns it.

This is sequencing step 4 — it follows the strict-SDK release, so every
script already yields `service_name` by the time a repo opts in.

Order: `parasail` first — it has four known-retired models, so its first PR
is the end-to-end proof. Then `openai` and `nebius`, whose heavy filtering
exercises the filtered-model case hardest. Then the rest. Cohere last, since
it is the one repo where a param file and an expanded folder coexist.

Ollama is local-only; confirm its enumeration is meaningful before enabling
it, and leave it off if not.

## Testing

**SDK unit tests** — the guard, the filter defect, and the file-class
exclusions are the ones that matter:

- disjoint `upstream_names` raises and writes nothing
- empty `upstream_names` raises and writes nothing
- overlap present → only the genuinely absent names are marked
- a model the iterator filtered out but that IS in `upstream_names` is
  untouched — the regression test for the second defect
- `<NAME>.service.json` and `<NAME>.override.json` are never treated as
  services and never marked — the regression test for the 36 override
  companions
- an expanded `<NAME>/offering.json` folder contributes `<NAME>` and is
  marked via `_deprecate_service`, so cohere needs no special case
- a yielded name that would be sanitised (`llama3:8b`) raises
  `ParamRenderError` instead of silently writing `llama3_8b`
- an iterator entry with no `service_name` fails with a message naming it,
  not a silent skip
- an entry carrying both `name` and `service_name` (the step-1 transitional
  shape) writes a param file byte-identical to today's
- re-running is idempotent
- `upstream_names=None` reproduces today's behaviour byte for byte

**Upload tests** — remote `active` deprecates, remote `pending` deletes,
already-`deprecated` is a no-op, missing remote is a no-op.

**End to end** — run the parasail populate against staging and confirm the
four known-retired models, and only those, are marked.

## What this would have caught

`parasail/zai-org/GLM-5.1`, `GLM-5.1-FP8`, `parasail-trinity-large-thinking`
and `parasail-kimi-k27-code` — all four absent from Parasail's live
enumeration, which still returns 92 models including plenty we publish, so
the overlap guard passes and the four are marked.

It would **not** have touched the two parasail services failing with HTTP
429 (`parasail-resemble-tts-en`, `parasail-mistralaimistral-nemo`) or the
four groq audio services failing on a gateway bug. Those models are all
present in their enumerations. Availability is not existence, and this
design only acts on existence.
