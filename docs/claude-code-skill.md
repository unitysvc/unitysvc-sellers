# Claude Code Skill: `writing-unitysvc-services`

This repository ships a [Claude Code](https://claude.com/claude-code) **skill** that teaches Claude how to author UnitySVC services correctly: file organization, naming conventions, the iterator+template pattern, mandatory connectivity tests, the validate → format → data-tests → gateway-tests → upload pipeline, and the staging-env conventions.

When the skill is installed, Claude consults it automatically any time you ask it to add, modify, regenerate, or troubleshoot a service in a `unitysvc-services-*` repo (or anything that sounds like that — BYOK / BYOE, gateway base URL, `usvc_seller specs` / `services` commands, etc.). You don't need to invoke it by name.

## Source of truth

The skill lives in this repository at:

```
skills/writing-unitysvc-services/SKILL.md
```

That file is the canonical version. Bug fixes, new sections, or any platform-rule update should be a PR against this path. The skill ships next to the SDK on purpose: it stays in lockstep with the platform conventions documented elsewhere in `docs/`.

## Install

A Claude Code skill is just a directory containing a `SKILL.md`. Claude Code discovers skills from three places, listed in order of priority:

| Location | Scope | When to use it |
|---|---|---|
| `<repo>/.claude/skills/<skill-name>/` | One repository | Pin a specific skill version to one data repo (CI runs see the same skill humans do) |
| `~/.claude/skills/<skill-name>/` | Your user account, all sessions | Standalone work that spans multiple repos on your laptop |
| Plugin paths | Installed via plugins | Not relevant here |

For most sellers, **the per-repo install is the right choice** — your seller-side automation (and any Claude Code session run from inside the data repo) picks it up automatically, and the skill version is pinned alongside your data so it can't drift mid-rollout.

### Per-repo install (recommended)

From the root of your `unitysvc-services-<yourcorp>` repo:

```bash
mkdir -p .claude/skills
git clone --depth 1 https://github.com/unitysvc/unitysvc-sellers.git /tmp/unitysvc-sellers
cp -r /tmp/unitysvc-sellers/skills/writing-unitysvc-services .claude/skills/
rm -rf /tmp/unitysvc-sellers

git add .claude/skills/writing-unitysvc-services
git commit -m "skills: add writing-unitysvc-services from unitysvc-sellers"
```

The skill is committed to your repo. Anyone cloning gets the same version Claude will use.

To pull in updates later, re-run the `git clone … && cp -r …` and commit the diff.

### User-level install

If you'd rather have the skill available in every Claude Code session regardless of which directory you're in:

```bash
mkdir -p ~/.claude/skills
git clone --depth 1 https://github.com/unitysvc/unitysvc-sellers.git /tmp/unitysvc-sellers
cp -r /tmp/unitysvc-sellers/skills/writing-unitysvc-services ~/.claude/skills/
rm -rf /tmp/unitysvc-sellers
```

Per-user skills aren't version-pinned by a data repo, so they can drift if you work across multiple `unitysvc-services-*` repos with different platform-rule eras. Re-`cp` periodically.

### Verify

In a Claude Code session, ask: *"What skills are available?"* — `writing-unitysvc-services` should appear in the list. Or just give Claude a real task; if the skill is installed it gets consulted automatically.

## How to trigger it

Once installed, **just describe the work you want done in your own words.** The skill description matches a wide range of phrasings:

- *"Add a new BYOK service for the Anthropic provider to my data repo"*
- *"Create a listing for gpt-5 in unitysvc-services-acme"*
- *"Help me set up the iterator pattern in this new provider repo"*
- *"I'm getting a validator error about base_url — what's the right shape?"*
- *"Regenerate all listings for cohere after the upstream models list changed"*
- *"The connectivity test fails through the gateway but works against the upstream directly"*

You do **not** need to say "use the writing-unitysvc-services skill." Mentioning it explicitly is fine but redundant.

The skill is "rigid" about two things, by design:

1. **The verification pipeline runs in order, all four steps.** `usvc_seller specs validate` → `usvc_seller specs format` → `usvc_seller specs run-tests <name>` → `usvc_seller services run-tests <name>`. A service is not "ready" until all four return green. Claude will not declare a task done if any of them is skipped.
2. **Every service must have at least one connectivity test.** Claude will add one (preset or local Jinja file) if you forget.

If you don't want those rails (e.g. quick prototyping), say so explicitly: *"Just generate the listing.json — skip the verification pipeline for now."*

## Staging environment

Anything that talks to the staging backend (`usvc_seller specs upload`, `usvc_seller services list/show/run-tests`, manual `curl https://api.staging.svcpass.com/…`) needs the seller API key and URL in env. The recommended setup is to put both in `~/.zshrc`:

```bash
# in ~/.zshrc
export UNITYSVC_SELLER_API_KEY="<your-staging-seller-key>"
export UNITYSVC_SELLER_API_URL="https://seller.staging.unitysvc.com/v1/"
export UNITYSVC_API_KEY="<your-svcpass-key-for-customer-side>"
```

Then any new shell (or `source ~/.zshrc` in the current one) is configured. Claude will run commands via `zsh -ic 'source ~/.zshrc && …'` from within the skill's workflow, so the env is loaded automatically inside its tool calls.

When a command returns `401` or `"Missing svcpass API key"`, the most common cause is forgetting to source — Claude will check this first.

## What the skill covers

The skill knows about:

- **File organization** — provider-dir = `provider.name`, mandatory `services/` segment, exactly-one-offering-per-service rule, override-file lifecycle.
- **Naming conventions** — listing.name grammar, namespaced first-segment rule, base_url grammar, reserved single-letter prefixes (`a/`, `b/`, `c/`, …), the `a/` movable-pointer carve-out.
- **Pattern selection** — when to copy from `unitysvc-services-demo`'s `relay` / `llm` / `byok` / `byoe` / `params` / `s3` / `smtp` / etc. variants.
- **Iterator + template pattern** — when to set up `scripts/update_services.py` + `templates/listing.json.j2`, and the `{% raw %}…{% endraw %}` rule for the runtime-Jinja-vs-generate-time-Jinja split.
- **Connectivity tests** — preset (`$doc_preset`) vs. local Jinja files, the dual-mode (`{% if localtesting %}`) requirement so the same test works for both `data run-tests` and `services run-tests`.
- **Verification pipeline** — the four-step gating order and what each step catches.
- **Common failure modes** — base_url shape mismatches, namespaced-name slug mismatches, validate-but-not-uploaded gaps, gateway 401s, generator-time vs runtime Jinja confusion, the "renamed listing creates a revision instead of in-place update" behavior post-PR #1196.

It points at this repo's docs (`docs/file-schemas.md`, `docs/pricing.md`, `docs/naming-conventions.md`, etc.) for deeper detail rather than duplicating them, so the canonical schema reference stays in one place.

## Reporting issues / contributing

If Claude does something wrong via this skill — wrong pricing block, missed naming rule, doesn't catch a validator failure that it should — open an issue or PR against `skills/writing-unitysvc-services/SKILL.md` in this repository. Include:

- The user prompt you gave Claude.
- The output Claude produced.
- What you expected instead.
- Any error messages from `usvc_seller specs validate` / `run-tests`.

Skill changes ship with the next release of the `unitysvc-sellers` package, and per-repo installs pick them up on the next `cp -r`.

## See also

- [Services](services.md) — the service model and `specs/` layout the skill operates on.
- [Naming Conventions](naming-conventions.md) — full grammar reference.
- [File Schemas](file-schemas.md) — every field on `provider_v1`, `offering_v1`, `listing_v1`.
- [Author & Upload Specs](guides/author-specs.md) — the `usvc_seller specs` commands the skill drives.
- [Generate a Catalog](guides/generate-catalog.md) — how this fits into a CI/CD pipeline.
