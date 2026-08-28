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

After migration there are none:

| repo | param files | sidecars | expanded folders |
| --- | --- | --- | --- |
| ollama | 246 | 235 | 0 |
| huggingface | 150 | 144 | 0 |
| parasail | 98 | 84 | 0 |
| bedrock | 37 | 37 | 0 |
| openai | 26 | 26 | 0 |
| nebius, groq, mistral, … | — | — | 0 |

So the loop's body never runs. `prune_missing=True`, which bedrock and
ollama explicitly opted into, is a no-op in both. **Dead code in all 17
repos.**

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

Two new keyword arguments:

```python
def write_params_from_iterator(
    iterator, output_dir, *,
    template=None,
    name_field="name",
    prune_missing=False,
    upstream_ids: set[str] | None = None,
    upstream_id_field: str = "offering_name",
) -> dict[str, int]:
```

- **`upstream_ids`** — the raw, pre-filter id set the provider's enumeration
  returned. `None` (default) preserves today's behaviour exactly, so rollout
  is per-repo and explicit, and no repo changes behaviour until its script
  opts in.
- **`upstream_id_field`** — which parameter key holds the upstream id.

`offering_name` is present in every one of the 17 repos surveyed, so it is
the default. Two repos need an override because their `offering_name` is not
what the enumeration returns:

| repo | field to compare | enumeration returns |
| --- | --- | --- |
| fireworks | `model_name` | `accounts/fireworks/models/kimi-k2p7-code` |
| bedrock | `converse_model_id` | `mistral.ministral-3-3b-instruct` |
| all others | `offering_name` | the plain model id |

#### Algorithm

Runs after the write loop, only when `upstream_ids is not None`:

1. **Collect local ids.** Walk `output_dir` for param files — `*.json`
   excluding `*.service.json`. This replaces the `_expanded_service_folders`
   scan and is the dead-loop fix. For each, read
   `parameters[upstream_id_field]`.
2. **Set aside the unjudgeable.** A param file with no value at that key
   describes something we cannot match against the enumeration. Skip it,
   count it, and name each one in the output. (Present today: 12 in
   parasail, 11 in ollama, 6 in huggingface, 4 in cohere.)
3. **Validate the enumeration — hard failure.** Raise
   `UpstreamEnumerationError` when either holds:
   - `upstream_ids` is empty, or
   - `upstream_ids.isdisjoint(local_ids)`.

   Nothing is written. Zero overlap with a catalog we already publish means
   the call was wrong — wrong key, wrong tier, wrong endpoint, a wholesale
   rename — not that every model retired at once. An admin investigates.
4. **Mark the missing.** For each id in `local_ids - upstream_ids`, set
   `parameters.status = "deprecated"` in its param file. Idempotent: a file
   already `deprecated` is counted, not rewritten.
5. **Report.** Extend the stats dict with `deprecated`,
   `already_deprecated`, and `unjudgeable`, and print each affected service
   name so the PR body and the job log both name them.

The comparison is **committed local ids against raw upstream ids**. What the
iterator yielded is not consulted. A filtered model is in `upstream_ids`, so
it is never in `missing` — which is precisely the defect described above.

`parameters.status` needs no schema change: `status` is already a parameter
in every repo, and `deprecated` is already in use (parasail 2, mistral 2).
`specs.py` already folds it into the service status via
`draft > deprecated > ready`.

#### Curated entries

A hand-curated model that legitimately never appears upstream is
indistinguishable from a retired one, and would be marked. Two mitigations,
in order:

- The PR review is the gate. These are rare, and a reviewer who knows the
  entry is curated drops that hunk.
- If a repo accumulates enough of them to be annoying, add an explicit
  `parameters.curated: true` opt-out that step 4 skips.

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

Per repo, one edit to `services/scripts/update_params.py`: keep the raw id
set the script already fetches, and pass it through.

```python
raw = fetch_models()                      # already happens
upstream_ids = {m["id"] for m in raw}     # before any filtering

write_params_from_iterator(
    iter_models(raw),                     # unchanged, still filters
    output_dir=SPECS_DIR,
    upstream_ids=upstream_ids,
    # upstream_id_field="model_name",     # fireworks
    # upstream_id_field="converse_model_id",  # bedrock
)
```

Order: `parasail` first — it has four known-retired models, so its first PR
is the end-to-end proof. Then `openai` and `nebius` (heaviest filtering, so
they exercise the filtered-model case hardest), then `fireworks` and
`bedrock` (the field overrides), then the rest.

Ollama is local-only; confirm its enumeration is meaningful before enabling
it, and leave it off if not.

## Testing

**SDK unit tests** — the guard and the filter defect are the ones that
matter:

- disjoint `upstream_ids` raises and writes nothing
- empty `upstream_ids` raises and writes nothing
- overlap present → only the genuinely absent ids are marked
- a model the iterator filtered out but that IS in `upstream_ids` is
  untouched — the regression test for the second defect
- a param file lacking `upstream_id_field` is skipped and counted, never
  marked
- re-running is idempotent
- `upstream_id_field` override resolves against the right key
- `upstream_ids=None` reproduces today's behaviour byte for byte

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
