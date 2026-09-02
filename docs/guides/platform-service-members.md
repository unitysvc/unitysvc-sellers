# Platform Service Members

Platform services are customer-facing endpoints owned by UnitySVC, such as an
LLM tier or a model facade. Sellers join one by uploading a private member
service from the platform's system template. The member is still your service:
it uses your upstream URL, your seller secret, and your accepted payout price.
The platform service supplies the customer-facing name, price, tests, and
routing contract.

Use the `platform_services/` layout when a repo manages member services for one
or more platform services.

## Layout

Keep standalone services under `services/specs/` and platform members under the
repo-level `platform_services/` directory:

```text
services/
├── specs/
│   └── crofai/
│       └── deepseek-v4-pro.json
└── templates/
    ├── provider.json
    ├── offering.json.j2
    └── listing.json.j2
platform_services/
└── llm-premium/
    └── crofai/
        ├── deepseek-v4-pro.json
        └── deepseek-v4-pro.service.json
```

The platform member service name is the path under `platform_services/`:

```text
platform_services/llm-premium/crofai/deepseek-v4-pro.json
→ llm-premium/crofai/deepseek-v4-pro
```

That shape has three meanings:

| Segment | Meaning |
|---|---|
| `llm-premium` | platform service / system template |
| `crofai` | upstream provider |
| `deepseek-v4-pro` | member service name, usually matching the standalone service |

## Param File

A platform member file is a system-template param file. It must include
`template`, `parameters`, and a `parameters.service_name` that exactly matches
the path under `platform_services/`.

```json
{
  "template": "llm-premium",
  "parameters": {
    "api_base_url": "https://api.crofai.example/v1",
    "api_key_secret": "CROFAI_API_KEY",
    "model": "deepseek-v4-pro",
    "payout_input": "0.35",
    "payout_output": "0.80",
    "service_name": "llm-premium/crofai/deepseek-v4-pro"
  }
}
```

Do not put platform member files under `services/specs/`. That tree remains the
source of truth for regular, self-managed services. Keeping platform members in
their own tree lets `update_params.py` refresh shared model facts without
confusing a platform member with the standalone service it mirrors.

## Status And Price Refresh

Provider populator scripts usually update regular model params under
`services/specs/`. With `deprecate_missing=True`, the SDK also scans
`platform_services/`:

- When a regular service is yielded, matching platform members are refreshed.
- Price fields such as `payout_input`, `payout_output`, and
  `payout_cached_input` are copied from the regular service's payout data when
  present.
- Stale `constants.status = "deprecated"` is cleared when the model appears
  again.
- If the model disappears, regular params get `parameters.status =
  "deprecated"` and platform members get `constants.status = "deprecated"`.

For platform members, status belongs in `constants.status`, not
`parameters.status`. Constants override seller-editable parameters during render,
which lets the repo retire a member without changing the template's input shape.

## Commands

The normal specs commands include both `services/specs/` and
`platform_services/`:

```bash
usvc seller specs validate
usvc seller specs format --check
usvc seller specs run-tests
usvc seller specs upload --submit
```

Selectors accept either the service name or the local path:

```bash
usvc seller specs upload llm-premium/crofai/deepseek-v4-pro --submit
usvc seller specs upload platform_services/llm-premium/crofai/deepseek-v4-pro.json --submit
```

After upload, the SDK writes the backend identity beside the param file:

```json
{
  "service_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Commit the `*.service.json` sidecar. Later uploads use it to update or revise the
same backend service. The `services` command family also reads these sidecars, so
bulk operations work for both regular and platform-member services:

```bash
usvc seller services submit --local-ids
usvc seller services run-tests --local-ids
usvc seller services activate --local-ids
```

When `--provider` is combined with `--local-ids`, platform member sidecars use
the provider segment after the platform service name. For
`platform_services/llm-premium/crofai/deepseek-v4-pro.service.json`, the provider
filter is `crofai`.

## Backend Result

Once the backend activates a generated service from a platform-linked template,
it reports `kind = platform_member` and links the member to its platform facade.
`usvc seller services show` displays the platform service it backs. The provider
shown for the member should be the upstream provider (`crofai` in the examples),
not the platform service name (`llm-premium`).

## See Also

- [Create from a System Template](create-from-template.md)
- [Compact Specs with Param Files](param-files.md)
- [Service Templates](../service-templates.md)
