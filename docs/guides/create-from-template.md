# Create from a Template

The fastest way to publish a common service type is to **instantiate a platform
template** — you author no files at all. You provide a handful of parameters and
the platform renders the complete service, runs the template's bundled test, and
submits it. This is the `params` route from
[Services → Two ways to create a service](../services.md#two-ways-to-create-a-service);
for the bigger picture (capability pools, authoring your own templates) see the
[Service Templates](../service-templates.md) concept page.

## Browse the catalog

```bash
usvc_seller templates list                        # active platform templates
usvc_seller templates show openai-compatible-llm  # parameters, types, and which are required
```

`templates show` lists each parameter's name, type, and whether it's required —
your checklist for the next step.

## Instantiate

`params instantiate` is the template analog of `specs upload`: it renders the
template into a service and (by default) submits it for review.

```bash
usvc_seller params instantiate openai-compatible-llm \
    -P api_base_url=https://api.example.com/v1 \
    -P api_key_secret_name=UPSTREAM_API_KEY \
    -P input_price=1.00
```

| Option | Meaning |
|---|---|
| `-P key=value` | A template parameter (repeatable) |
| `--name` | Optional label for the service (defaults to the template name) |
| `--submit` / `--no-submit` | Submit for review (default), or leave a draft to submit later |

With `--no-submit` you get a reviewable draft; submit it later with
`usvc_seller services submit <service_name>`.

## Secret-typed parameters

A secret-typed parameter (e.g. an upstream API key) takes the **name of a
secret**, never the raw value. Create the secret first, then reference it by
name:

```bash
usvc_seller secrets set UPSTREAM_API_KEY            # stores the value securely
usvc_seller params instantiate openai-compatible-llm -P api_key_secret_name=UPSTREAM_API_KEY …
```

See [Promotions, Groups & Secrets](catalog-extras.md#secrets) for managing
secrets.

## From the SDK

`client.templates` browses the catalog; `client.instances` creates services:

```python
from unitysvc_sellers import Client

with Client() as client:
    client.templates.list()                       # available templates
    result = client.instances.create(
        "openai-compatible-llm",
        parameters={
            "api_base_url": "https://api.example.com/v1",
            "api_key_secret_name": "UPSTREAM_API_KEY",
            "input_price": 1.00,
        },
        # submit=True by default; pass submit=False to leave a draft.
    )
    # result carries the new instance_id and the ingest task_id
```

## After instantiation

The rendered service appears in your catalog like any other — manage it with
`usvc_seller services …` ([Operate Live Services](operate-services.md)). If you
outgrow the template, download the rendered files and refine them as a normal
[specs repo](author-specs.md).
