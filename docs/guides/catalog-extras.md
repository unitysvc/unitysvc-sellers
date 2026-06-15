# Promotions, Groups & Secrets

Three smaller domains round out a seller catalog. Each has its own CLI command
group and SDK namespace. Promotions and groups are **authored as files and
uploaded** (like specs); secrets live **only on the platform**.

## Promotions

A **promotion** is a price rule that discounts your services for customers. You
author a `promotion.*` file (it can live anywhere in the repo — it's keyed by
`name`) and upload it; you then activate or pause it remotely.

```json
// promotions/launch-week.json
{
    "name": "launch-week",
    "description": "20% off all LLM listings",
    "scope": { "service_type": "llm" },          // which services it applies to
    "pricing": { "type": "percentage", "value": "20" },
    "apply_at": "list_price",
    "priority": 100,
    "status": "paused"
}
```

Upload, then manage status:

```bash
usvc_seller specs upload -t promotions      # upload just promotions
usvc_seller promotions list
usvc_seller promotions show launch-week
usvc_seller promotions activate launch-week # status → active
usvc_seller promotions pause    launch-week # status → paused
usvc_seller promotions delete   launch-week
```

Key fields: `scope` (which services), `pricing` (the discount), `apply_at`,
`priority`, `expires_at`, `max_uses`. Full reference in
[File Schemas](../file-schemas.md).

## Service groups

A **service group** bundles related services behind one addressable path
(`/g/<group>`), so a customer can call the group and the platform routes to a
member. You author a `service_group.*` file and upload it.

```json
// groups/llm.json
{
    "name": "llm",
    "display_name": "LLM pool",
    "group_type": "load_balance",
    "membership_rules": { "service_type": "llm" },
    "status": "active"
}
```

```bash
usvc_seller specs upload -t groups
usvc_seller groups list
usvc_seller groups show llm
usvc_seller groups delete llm
```

Key fields: `group_type`, `membership_rules` (which services join),
`parent_group_name`, `access_interface_data_template`, `sort_order`. See
[File Schemas](../file-schemas.md). A **capability pool** (`/p/<capability>`) is a
platform-managed group — see [Service Templates](../service-templates.md#2-capability-pools-opt-in-with-a-pool-name).

## Secrets

A **secret** is a named value (an upstream API key) stored on the platform and
referenced **by name** from your specs and params — the raw value never appears
in your files or commands.

```bash
usvc_seller secrets set UPSTREAM_API_KEY     # create or rotate (idempotent); prompts for the value
usvc_seller secrets list                     # metadata only — values are never returned
usvc_seller secrets show UPSTREAM_API_KEY
usvc_seller secrets delete UPSTREAM_API_KEY  # services referencing it will stop resolving
```

Reference a secret from a service by name, using the namespace that declares who
owns it (see [Service Types](../service-types.md#byok-bring-your-own-key)):

- `${ secrets.UPSTREAM_API_KEY }` — a **seller-owned** secret (managed services).
- `${ customer_secrets.UPSTREAM_API_KEY }` — a **customer-owned** secret (BYOK).

When [instantiating a template](create-from-template.md), a secret-typed
parameter takes the **secret name**, not the value — so create the secret first.

## SDK

All three are available as SDK namespaces: `client.promotions`, `client.groups`,
`client.secrets`. See the [SDK Guide](../sdk-guide.md).
