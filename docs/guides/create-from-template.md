# Create from a Template

The fastest way to publish a common service type is to **instantiate a system
template** — a template the platform publishes (e.g. an OpenAI-compatible LLM
endpoint). You author no spec files: you pick a template, supply a handful of
parameters in a small **param file** under `params/`, and the platform renders
the complete service as a reviewable draft (add `--submit` to also submit it for
review, which runs the template's bundled test).

This is the `params` route — the system-template mirror of `specs/`. Two
commands work together:

| Command | Role |
|---|---|
| **`usvc_seller templates`** | **Browse** the catalog — `list` the system templates, `show` one's parameters. Read-only. |
| **`usvc_seller params`** | **Use** them — author `params/` files, `list` / `show` them, and `instantiate` them into services. |

For the bigger picture (capability pools, authoring your *own* templates) see the
[Service Templates](../service-templates.md) concept page.

## 1. Browse the catalog — `templates`

```bash
usvc_seller templates list                        # active system templates
usvc_seller templates show openai-compatible-llm  # its parameters: name, type, required?
```

`templates show` lists each parameter's name, type, and whether it's required —
your checklist for the param file you write next.

## 2. Author a param file under `params/`

A param file is `params/<name>.json` = `{ "template", "parameters" }`: the
**system template name** (from `templates list`) plus the values to render it
with. Its path under `params/` becomes the service name.

```
params/
└── acme/
    ├── gpt.json            # { template, parameters }
    └── gpt.service.json    # identity sidecar (service_id) — written on instantiate, committed
```

```jsonc
// params/acme/gpt.json
{
  "template": "openai-compatible-llm",
  "parameters": {
    "api_base_url": "https://api.acme.ai/v1",
    "api_key_secret_name": "UPSTREAM_API_KEY",
    "input_price": 1.00
  }
}
```

> **`params/` (system templates) vs `specs/` (local).** A param file under
> `params/` names a **system** template, rendered server-side by `instantiate`.
> A param file under `specs/` whose `template` is a **local** `templates/`
> directory is instead rendered on your machine by the `specs` commands. Same
> file shape, different folder, different command — see
> [Service Templates](../service-templates.md).

## 3. Inspect what you've authored — `params list` / `show`

Offline, no API call:

```bash
usvc_seller params list                 # every param file under params/ (Service · Template · Service ID)
usvc_seller params show acme/gpt        # one file's template, parameters, and recorded service_id
```

## 4. Instantiate — `params instantiate`

`params instantiate` is the params-kind analog of `specs upload`: it renders each
param file's system template with its parameters into a backend service, left as
a reviewable **draft** by default.

```bash
usvc_seller params instantiate           # all param files under params/
usvc_seller params instantiate acme/gpt  # just this one (NAME is an fnmatch selector)
usvc_seller params instantiate 'acme/*'  # everything under acme/
usvc_seller params instantiate --submit  # render and submit for review in one go
```

| Option | Meaning |
|---|---|
| `[NAME]` | Param-file selector (fnmatch); omit = all under `params/` |
| `--submit` | Also submit each for review (validate → pending → tests); default leaves a draft |

**Identity round-trips through the sidecar.** On a successful instantiate the
backend-assigned `service_id` is written to `params/<name>.service.json` (commit
it). An entry that already has a `service_id` is skipped — re-instantiating to
*update* the same service needs backend support
([unitysvc/unitysvc#1273](https://github.com/unitysvc/unitysvc/issues/1273)).

## Secret-typed parameters

A secret-typed parameter (e.g. an upstream API key) takes the **name of a
secret**, never the raw value. Create the secret first, then reference it by name
in the param file:

```bash
usvc_seller secrets set UPSTREAM_API_KEY   # stores the value securely
```

```jsonc
// then in the param file:
"parameters": { "api_key_secret_name": "UPSTREAM_API_KEY", … }
```

See [Promotions, Groups & Secrets](catalog-extras.md#secrets) for managing
secrets.

## From the SDK

`client.templates` browses the catalog; `client.instances` creates services:

```python
from unitysvc_sellers import Client

with Client() as client:
    client.templates.list()                       # available system templates
    result = client.instances.create(
        "openai-compatible-llm",
        parameters={
            "api_base_url": "https://api.acme.ai/v1",
            "api_key_secret_name": "UPSTREAM_API_KEY",
            "input_price": 1.00,
        },
        # Draft by default; pass auto_submit=True to also submit for review now.
    )
    # result carries the new instance_id and the ingest task_id
```

## After instantiation

The rendered service appears in your catalog like any other — manage it with
`usvc_seller services …` ([Operate Live Services](operate-services.md)). If you
outgrow the template, download the rendered files and refine them as a normal
[specs repo](author-specs.md).
