# Publish Platform Services

A **platform service** is a service you resell: customers call it at a `/p`
address (for example `/p/llm` with `model="fast"`), and it routes each request
to member services that other sellers contribute. You publish the platform
service together with its **member template** — the template other sellers
instantiate to join it (see [Platform Service Members](platform-service-members.md)).

Publishing platform services requires a **trusted** or **partner** seller — and, for now, the UnitySVC Labs seller (resale settlement supports only Labs so far). A new platform service from a trusted seller waits for admin approval; until then sellers cannot join it.

## Layout

One folder per platform service, under its provider:

```text
platform-services/
└── labs/
    └── llm-fast/
        ├── provider.json
        ├── offering.json
        ├── listing.json            # declares the /p address
        ├── llm-fast.service.json   # optional: {"service_id": ...}
        └── member-template/
            ├── template.json       # its name is the folder name (llm-fast)
            ├── offering.json.j2
            ├── listing.json.j2
            ├── provider.json.j2
            └── template_id.json    # optional: {"id": ..., "name": ...}
```

- The listing's `user_access_interfaces` must all point at
  `${API_GATEWAY_BASE_URL}/p/<route>`; the primary interface's `routing_key`
  is the address within that route (e.g. `{"model": "fast"}`).
- The member template reads values the platform service already declares
  through the `platform_service` render variable instead of restating them,
  e.g. `"list_price": {{ platform_service.list_price | tojson }}`.

Member template bodies are rendered by the platform, so they are limited to a
small subset of Jinja: output, `{% if %}`, `{% set %}`, conditional
expressions, comparisons, `and`/`or`/`not`, attribute/item access, literals and
`~`; the filters `tojson`, `default`, `length`, `lower`, `upper`, `trim`,
`slugify`, `replace`, `string`; and the string methods `split`, `strip`,
`startswith`, `endswith` and similar. Loops, macros, arithmetic, `%` and
`.format` are refused at upload.

Ordinary `specs` commands ignore `platform-services/`; it is never uploaded as
an ordinary service.

## Upload

```bash
usvc seller specs upload                      # everything, platform services included
usvc seller specs upload --name labs/llm-fast # one platform service
```

Each folder is sent to `POST /seller/platform-services` together with its
member template. Afterwards the platform service's id is written to
`<name>.service.json` and the template's to `member-template/template_id.json`.

Both ids are optional:

- With `<name>.service.json`, the upload updates that platform service — even
  if its name or provider changed (e.g. `unitysvc/llm-fast` → `labs/llm-fast`).
  Without it, your platform service of that name is updated, or a new one is
  created.
- The member template is matched by `(name, version)`; `template_id.json` is
  used when a template is created, so every environment shares its id.

## What happens on the platform

A platform service cannot be tested until a member backs it, so there is no
submit → test → review step:

| | New platform service | Update to one you own |
|---|---|---|
| partner | live at once | applied at once |
| trusted | waits for admin approval (`review`) | applied at once |

Its members then decide availability: it is unavailable without members,
unlisted with one provider, and public from two providers on. When the member
template changes, existing members are re-rendered from their stored
parameters.
