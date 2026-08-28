# Deprecating models that upstream no longer serves

**Date:** 2026-08-28
**Status:** design, approved in chat; not yet implemented
**Issue:** unitysvc/unitysvc-sellers#181
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

### A defect I argued for, then disproved

An earlier draft of this design claimed a second bug: that comparing against
what the iterator *yielded* would deprecate every model a script filters out,
and that the comparison therefore had to be against a raw, pre-filter
enumeration passed in by the caller.

**That is wrong, and the repo data says so.** A script's filter is applied on
*every* run, so a filtered model is never written as a param file — it cannot
be in `committed − yielded`. Checked against openai, whose script drops ~15
substrings (`embed`, `whisper`, `tts`, `realtime`, `dall-e`, `-pro`,
`preview`, …): of its 26 committed services, **none** matches any of them.

So the reference set the function already has — what the iterator yielded — is
the right one, and no new parameter is needed. The only real bug was the dead
scan.

The genuine edge that remains is a **curated** entry: hand-added, never
yielded by any run, and therefore deprecated. That is handled by PR review,
with a `parameters.curated: true` opt-out held in reserve.

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

### Part 1 — SDK: revive `deprecate_missing`, don't reinvent it

`populate_from_iterator` already has the right argument, with the right
default and the right meaning:

```python
deprecate_missing: bool = True   # template_populate.py
```

The params path never got it and grew `prune_missing` instead — a different
name, a different default, a different action (delete), and a scan that no
longer matches anything. The fix is to give `write_params_from_iterator` the
**same argument as its sibling**, not a third mechanism:

```python
def write_params_from_iterator(
    iterator, output_dir, *,
    template=None,
    deprecate_missing=True,
) -> dict[str, int]:
```

Nothing is passed in. The function reads what it needs from disk:

1. **Before the loop**, collect every committed service under `output_dir`
   into `remaining` — keyed by service name, which *is* the path.
2. **In the loop**, each yielded service is written as usual and then
   `remaining.pop(name)`. A name that was not there counts as `new`.
3. **After the loop**, whatever is still in `remaining` never appeared this
   run. Guard, then mark each `status = "deprecated"`.

`prune_missing` is removed rather than fixed. Deleting a local param file was
never a working retirement: it orphans the sidecar holding the `service_id`
and leaves the **remote** service live forever — precisely the drift that let
`GLM-5.1` linger. Marking it deprecated retires it properly, because the
upload then acts on the remote (Part 2). Fixing prune's scan instead would
have armed deletion of 37 param files in bedrock and 235 in ollama, both of
which opted in while it was a no-op.

#### The guard

If **every** committed service would be deprecated, the run did not find a few
retirements — it failed. A populator that errored, authenticated wrongly, or
hit an endpoint serving nobody's models is indistinguishable from a catalog
that retired all at once, and only one of those is real. So:

```python
if committed_total and len(remaining) == committed_total:
    raise UpstreamEnumerationError(...)
```

The error prints a sample of the committed names and points at the likeliest
cause — a `service_name` in the wrong namespace (raw model id `Qwen/Qwen3-32B`
instead of service name `nebius/Qwen/Qwen3-32B`), which would make everything
look absent.

**Nothing needs unwinding when it raises.** The workflow's `git add specs/`
and PR-creation steps never run once the populate step exits non-zero, so a
half-written tree is discarded with the runner. That is why the check sits
after the loop, where it is cheap and exact, rather than guessing before it.

#### What counts as a service

`output_dir` holds four kinds of `.json`, and only two carry a service:

| file | count | contributes a name? |
| --- | --- | --- |
| `<NAME>.json` param file | 688 | **yes** → `<NAME>` |
| `<NAME>/{offering,listing,…}.json` expanded folder | 1 repo | **yes** → `<NAME>` |
| `<NAME>.service.json` identity sidecar | 688 | no |
| `<NAME>.override.json` companion | 36 | no |

The override companions matter: 36 exist across parasail (14), ollama (11),
huggingface (6), groq (2), mistral (2) and nebius (1). A naive `*.json` glob
counts each as a service that no run ever yields, and deprecates it every
time.

Both service shapes share one namespace, so cohere's un-migrated
`cohere/embed-v4.0` folder needs no special case: `_deprecate_service` marks
its `offering.json`/`listing.json`, `_deprecate_param_file` marks a param
file's `parameters`.

`status` needs no schema change — it is already a parameter in every repo and
`deprecated` is already in use (parasail 2, mistral 2). `specs.py` folds it
into the service status via `draft > deprecated > ready`.

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
that the path, `listing.name`, and the deprecation match all derive from.

**Cost today: none.** `_sanitize_dirname` is
`name.strip("/").replace(":", "_")` and is a no-op on every name in every
repo — no path anywhere is a sanitized colon (the three `_` in nebius are
genuine, as in `MiniCPM-V-4_5`), and ollama, the one provider whose upstream
ids use `:`, already normalises `:` → `-` in its own script before naming.
Every iterator already yields a `name`; this makes the guarantee explicit
and checked instead of assumed. Silent sanitisation is precisely what would
break it later: a future `llama3:8b` would land at `llama3_8b` and every
name-to-path comparison would quietly miss.

#### Sequencing: the release is the gate, not the merge

Requiring `service_name` and dropping `name_field` breaks every script that
does not yet yield it, and the populate workflow is **shared and unpinned**:

```yaml
# unitysvc-labs/.github/.github/workflows/seller-populate-services.yml
pip install "unitysvc-sellers>=0.2.25"
```

All 17 repos resolve the same version, so there is no per-repo staging of the
SDK without first parameterising that workflow.

What makes this tractable: **publishing is triggered by a GitHub release, not
by a merge** (`publish.yml` fires on `release: [published]`). Merging the
strict SDK to `main` changes nothing for the repos — they keep resolving
0.2.36 from PyPI until someone cuts a release.

1. **Merge the strict SDK** (this change). Safe: nothing is published.
2. **17 script PRs**, one per repo, each yielding `service_name`. They may
   keep `name` alongside it — `_PATH_DERIVED_KEYS` strips both, so no param
   file changes by a byte, and the scripts stay compatible with the released
   0.2.36 throughout.
3. **Cut the release.** *This is the gate*: it must not happen until step 2
   is complete for all 17, because the next 02:00 cron picks it up
   everywhere at once.
There is no step 4. `deprecate_missing` defaults to True, so deprecation
switches on for **all 17 repos at once** when the release lands — the same
02:00 cron that picks up the strict `service_name`. Expect the first
post-release populate PR in each repo to carry deprecations; that is the
point, and each is reviewed before merge. A repo that is not ready passes
`deprecate_missing=False` in step 2.

Templates are independent of all three: the render context already supplies
`service_name`, so `"name": "{{ service_name }}"` can land whenever.

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

Per repo, one edit to `services/scripts/update_params.py`: state
`service_name` in what the iterator yields. Nothing else — `deprecate_missing`
defaults to True, and the function reads the committed set from disk itself.

```python
#   {"name": f"{PROVIDER_NAME}/{model_id}", ...}
# -> {"service_name": f"{PROVIDER_NAME}/{model_id}", ...}

write_params_from_iterator(iter_models(raw), output_dir=SPECS_DIR)
```

The two repos passing `prune_missing=True` (bedrock, ollama) drop that
argument; it has been a no-op in both, and deprecation now covers the intent
behind it.

Order: `parasail` first — it has four known-retired models, so its first PR
is the end-to-end proof. Then the rest. Cohere last, since it is the one repo
where a param file and an expanded folder coexist.

Ollama is local-only; confirm its enumeration is meaningful before relying on
it, and pass `deprecate_missing=False` there if not.

## Testing

**SDK unit tests** — the guard, the file-class exclusions, and the two
service shapes are what matter:

- a committed service the iterator does not yield is deprecated
- a yielded service that was not committed counts as `new`, not deprecated
- matching **none** of the committed services raises — the failed-populate
  guard — as does yielding nothing at all
- a first run on an empty repo is not a failure (nothing committed, nothing
  to explain)
- `<NAME>.service.json` and `<NAME>.override.json` are never services — the
  regression test for the 36 override companions
- an expanded `<NAME>/offering.json` folder contributes `<NAME>` and is
  marked via `_deprecate_service`, so cohere needs no special case
- a stale expanded folder is marked, never deleted: its `service_id` must
  survive so the upload can retire the remote service
- re-running is idempotent
- `deprecate_missing=False` leaves stale entries alone
- a name that would be sanitised raises; a missing `service_name` raises

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
