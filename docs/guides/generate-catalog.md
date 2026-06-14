# Generate a Catalog

When you offer *many* similar services — every model your upstream serves, a
region per endpoint, a tier per plan — don't author them by hand. Write a
**populator**: a small template + script that the SDK runs to generate the whole
`specs/` catalog and keep it in sync with the source. This is pattern #3 from
[Service Templates](../service-templates.md#3-your-own-service-templates--usvc_seller-specs-populate).

## The pieces

A populator lives alongside your specs and has three parts:

```
templates/
├── offering.json.j2      # the per-service files, with {{ placeholders }}
├── listing.json.j2
├── provider.json         # static provider definition (copied into each folder)
└── config.json           # declares how to run the populator
scripts/
└── update_specs.py       # yields one parameter set per service (reads your upstream)
specs/                     # generated output
```

`templates/config.json` declares the populator command and its dependencies:

```json
{
  "services_populator": {
    "command": ["scripts/update_specs.py"],
    "requirements": ["httpx", "unitysvc-sellers"]
  }
}
```

The `services_populator` config lives in `config.json`, **not** in
`provider.json` — `provider.json` stays a pure provider definition that gets
copied verbatim into each generated service folder.

## Run it

```bash
usvc_seller specs populate              # render every service from the template
usvc_seller specs populate --dry-run    # preview without writing files
usvc_seller specs populate --provider acme   # restrict to one provider
```

`populate` finds `templates/config.json`, installs the declared requirements, and
runs the script from the repo root. The generated `specs/<provider>/<service>/`
folders are normal service data — validate, test, and upload them like anything
else ([Author & Upload Specs](author-specs.md)).

## Keeping in sync

Re-running `populate` reconciles the catalog with the upstream source:

- **New** upstream entries become new service folders.
- **Removed** upstream entries are marked `status: deprecated` (the folders are
  kept, not deleted).
- **Unchanged** services don't churn — each file's `time_created` is read back
  and preserved, so a daily run produces a zero-diff unless something actually
  changed.

That idempotency is what makes a **scheduled** populate safe: a daily job can
regenerate, and only real upstream changes surface as a diff.

## Writing the script

Two shapes, depending on how much control you need:

- **SDK helper (recommended for the common case).** Have your script *yield* one
  dict of template variables per service and hand them to
  `unitysvc_sellers.template_populate.populate_from_iterator`, which renders the
  templates, writes the flat nested layout, copies `provider.json` into each
  folder, localizes shared doc references, and handles deprecation +
  `time_created` for you.

  ```python
  from unitysvc_sellers.template_populate import populate_from_iterator

  def iter_models():
      for m in fetch_upstream_models():            # your API call
          yield {"name": f"acme/{m['id']}", "offering_name": m["id"], ...}

  populate_from_iterator(iter_models(), templates_dir="templates", output_dir="specs")
  ```

- **Bespoke extractor.** For unusual upstreams you can write the files yourself;
  just emit the same flat `specs/<provider>/<service>/` layout (filename-as-type,
  no `schema` field) and preserve each file's existing `time_created`.

## Automating in CI

The `unitysvc-services-*` provider repos run their populator on a schedule: a
GitHub Actions workflow runs `usvc_seller specs populate`, and if the `specs/`
diff is non-empty it opens an **auto-populate pull request** with the new and
deprecated services for review. That keeps the catalog current without anyone
re-running the script by hand — review the PR, merge, and `specs upload` (or let
the upload workflow do it).

## Next steps

- [Author & Upload Specs](author-specs.md) — validate, test, and upload the output
- [Service Templates](../service-templates.md) — platform templates and capability pools
