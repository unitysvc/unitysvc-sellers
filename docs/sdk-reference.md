# Python SDK Reference

`unitysvc-sellers` ships a typed Python SDK that the `usvc_seller`
CLI is itself built on. Anything the CLI can do — upload a catalog,
list services, mutate promotions, run connectivity tests — you can
do programmatically via `unitysvc_sellers.Client` (sync) or
`unitysvc_sellers.AsyncClient` (async).

The SDK is generated from the seller OpenAPI spec, so request and
response models are fully typed: your editor will autocomplete
fields and your type checker will catch mistakes before they hit
the wire.

## Installation

```bash
pip install unitysvc-sellers
```

## Authentication

Both `Client` and `AsyncClient` read credentials from the
environment by default:

| Variable                  | Purpose                                                                        |
| ------------------------- | ------------------------------------------------------------------------------ |
| `UNITYSVC_SELLER_API_KEY` | Seller API key (`svcpass_…`). Get one from the UnitySVC dashboard.             |
| `UNITYSVC_SELLER_API_URL` | Base URL for the seller API. Defaults to `https://seller.unitysvc.com/v1`. |

```python
from unitysvc_sellers import Client

client = Client()              # reads both env vars, raises if key missing
client = Client(api_key="...") # explicit key, env URL (or default)
client = Client(api_key="...", base_url="https://seller.unitysvc.com/v1")
```

The seller context is encoded entirely in the API key — there is no
`seller_id` argument to pass. Both clients are safe to use as
context managers and will close their underlying `httpx` session on
exit:

```python
from unitysvc_sellers import Client

with Client() as client:
    for svc in client.services.list().data:
        print(svc.name)
```

## Sync vs async: when to use which

| You are writing…                                           | Use           |
| ---------------------------------------------------------- | ------------- |
| A one-off script or a Jupyter notebook                     | `Client`      |
| A Celery task or other already-sync worker                 | `Client`      |
| An `async def` function, FastAPI handler, or asyncio app   | `AsyncClient` |
| A CLI tool where you want to overlap multiple requests     | `AsyncClient` |

The two are a one-to-one mirror: every sync method has an async
counterpart with the same name and signature, just `await`able.

### Sync example

```python
from unitysvc_sellers import Client

with Client() as client:
    page = client.services.list(limit=50)
    for svc in page.data:
        print(svc.id, svc.name, svc.status)
```

### Async example

```python
import asyncio
from unitysvc_sellers import AsyncClient

async def main():
    async with AsyncClient() as client:
        page = await client.services.list(limit=50)
        for svc in page.data:
            print(svc.id, svc.name, svc.status)

asyncio.run(main())
```

## Resource namespaces

Both clients expose the same five resource namespaces as lazy
properties:

| Namespace            | Underlying endpoints                                          | Purpose                                                                 |
| -------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `client.services`    | `/seller/services/*`                                          | List, get, upload, mutate status / routing / pricing, delete services   |
| `client.promotions`  | `/seller/promotions/*`                                        | CRUD on seller-funded promotion codes                                   |
| `client.groups`      | `/seller/service-groups/*`                                    | CRUD on service groups                                                  |
| `client.documents`   | `/seller/documents/*`                                         | Fetch document file content, execute (gateway dispatch), update test    |
| `client.secrets`     | `/seller/secrets/*`                                           | Create, rotate, list, and delete encrypted seller secrets               |
| `client.tasks`       | `/seller/tasks/*`                                             | Poll Celery task state for async operations (notably service upload)   |

The async client exposes the same namespaces with `Async` prefixes
on the resource classes (`AsyncServicesResource`, etc.), but the
attribute names on the client are identical — so you can rename
`Client` to `AsyncClient` in a code snippet and the rest just needs
`await`s.

## `client.services`

The services resource covers the full seller-catalog lifecycle.

| Method                           | Description                                                                     |
| -------------------------------- | ------------------------------------------------------------------------------- |
| `list(cursor=, limit=, …)`       | Cursor-paged list with optional `status` / `service_type` / `name` filters.     |
| `get(service_id)`                | Full service detail including interfaces, documents, upstream config.           |
| `get_test_env(service_id)`       | Environment variables for local connectivity testing (`SERVICE_BASE_URL`, …).   |
| `upload(body, dryrun=False)`     | POST provider + offering + listing bundle. Backend responds with a task id.     |
| `set_status(service_id, body)`   | Change lifecycle status (`draft` → `pending` for review, etc.).                 |
| `set_routing_vars(…)`            | Update the routing variables used by the gateway plugin.                        |
| `set_list_price(…)`              | Update the customer-facing price on an active service.                          |
| `delete(service_id)`             | Remove a service. (Most flows should use `set_status` → `deprecated` instead.)  |

### Listing services

```python
with Client() as client:
    page = client.services.list(limit=100, status="active")
    while True:
        for svc in page.data:
            print(svc.id, svc.name, svc.service_type)
        if not page.has_more:
            break
        page = client.services.list(cursor=page.next_cursor, limit=100)
```

### Fetching one service

```python
svc = client.services.get("be098e7d-59e1-498a-bc4f-e389eb61c70b")
print(svc.service_name, svc.status)
for iface in svc.interfaces:
    print(" iface:", iface.name, iface.base_url)
for doc in svc.documents or []:
    print(" doc:", doc.title, doc.category, doc.test_status)
```

### Mutating status

```python
# Submit a draft service for review. Omit run_tests to skip the
# backend's auto-queue of the full connectivity test suite (useful
# when the CLI has already run those tests locally).
client.services.set_status(
    "be098e7d-59e1-498a-bc4f-e389eb61c70b",
    {"status": "pending", "run_tests": True},
)
```

## `client.promotions`

Seller-funded promotion codes — discounts the seller pays for, to
bootstrap demand or reward specific customers.

```python
from unitysvc_sellers import Client

with Client() as client:
    # Create or update by name.
    client.promotions.upsert({
        "name": "summer2026",
        "code": "SUMMER2026",
        "pricing": {"type": "percentage_off", "percentage": "25.00"},
        "scope": {"service_type": "llm"},
        "apply_at": "request",
        "priority": 10,
        "status": "active",
    })

    # List active promotions.
    for promo in client.promotions.list(limit=100).data:
        print(promo.code, promo.status)

    # Deactivate.
    client.promotions.update("summer2026", {"status": "paused"})
```

## `client.groups`

Service groups bundle related services together for routing,
discovery, or group-wide pricing.

```python
with Client() as client:
    client.groups.upsert({
        "name": "premium-llms",
        "display_name": "Premium LLMs",
        "owner_type": "seller",
        "membership_rules": {
            "include_tags": ["premium", "llm"],
        },
    })

    for grp in client.groups.list().data:
        print(grp.name, grp.display_name)
```

## `client.documents`

Operate on documents attached to a service (code examples,
connectivity tests, terms, logos).

```python
with Client() as client:
    doc = client.documents.get("5c937b4a-980a-4a69-bb90-a1f93816de1d")
    print(doc.title, doc.mime_type)
    if doc.file_content:
        print(doc.file_content[:200])

    # Record an externally-run test result. Useful when the CLI or
    # an in-house CI ran the script locally and wants to POST the
    # per-interface outcome back.
    client.documents.update_test(
        doc.id,
        {
            "status": "success",
            "tests": {
                "default": {"status": "success", "exit_code": 0},
            },
        },
    )
```

`client.documents.execute(doc_id, force=True)` dispatches the
document to the backend Celery worker for execution against the
gateway. The CLI's `usvc_seller services run-tests` command, in
contrast, runs the scripts **locally** on the seller's machine —
see [Running connectivity tests locally](#running-connectivity-tests-locally)
below for the recommended pattern.

## `client.secrets`

Manage encrypted seller secrets (API keys, tokens, credentials).
Values are **write-only** — only metadata is ever returned by the API.

| Method                       | Parameters              | Returns         | Description                          |
| ---------------------------- | ----------------------- | --------------- | ------------------------------------ |
| `list(skip=0, limit=100)`    | `skip: int`, `limit: int` | `SecretsPublic` | List secrets (metadata only)         |
| `get(name)`                  | `name: str`             | `SecretPublic`  | Get one secret's metadata by name    |
| `create(name, value)`        | `name: str`, `value: str` | `SecretPublic`  | Create a new secret                  |
| `rotate(name, value)`        | `name: str`, `value: str` | `SecretPublic`  | Rotate (update) an existing secret   |
| `delete(name)`               | `name: str`             | `None`          | Permanently delete a secret          |

Secret names must be uppercase with underscores (e.g.
`OPENAI_API_KEY`, `STRIPE_SECRET`). Names starting with `__` are
reserved for platform use.

```python
from unitysvc_sellers import Client

with Client() as client:
    # Create a secret (value is write-only, cannot be retrieved)
    client.secrets.create("OPENAI_API_KEY", "sk-proj-abc123...")

    # List all secrets (metadata only)
    for s in client.secrets.list().data:
        print(s.name, s.created_at, s.last_used_at)

    # Get one secret's metadata
    meta = client.secrets.get("OPENAI_API_KEY")
    print(meta.name, meta.updated_at)

    # Rotate the value (e.g. after a key leak)
    client.secrets.rotate("OPENAI_API_KEY", "sk-proj-new456...")

    # Delete (immediate effect — services referencing it will break)
    client.secrets.delete("OPENAI_API_KEY")
```

!!! warning "Write-only values"
    The API never returns secret values. If you lose the value,
    rotate it with a new one. There is no "get value" endpoint.

## `client.tasks`

Several seller endpoints are fire-and-forget: they accept your
request, queue a Celery task, and return a `task_id`. The tasks
resource lets you poll for the real outcome.

| Method                                | Description                                                              |
| ------------------------------------- | ------------------------------------------------------------------------ |
| `get(task_id)`                        | One-shot status for a single task.                                       |
| `batch_status(task_ids)`              | One request, many tasks. Preferred for uploads that yield N tasks.       |
| `wait(task_id, timeout=, poll=)`      | Block until the task reaches a terminal state or times out.              |
| `wait_batch(ids, timeout=, poll=)`    | Wait for every id in a batch; returns a dict of final states.            |

Terminal Celery states the SDK recognises are `completed` and
`failed`. `wait_batch` polls with exponential-friendly delays and
returns a dict keyed by `task_id`, where each entry has `state`,
`status`, `result`, and (for failures) `error` fields.

```python
with Client() as client:
    result = client.services.upload({"services": [...]})
    task_id = result.task_id

    final = client.tasks.wait(task_id, timeout=300, poll_interval=2)
    if final["status"] == "completed":
        print("service_id =", final["result"]["service_id"])
    else:
        print("failed:", final.get("error") or final.get("message"))
```

## `upload_directory` — full catalog upload helper

For the common case of "upload a whole seller catalog directory,
wait for every task, write `.override.json` files so the next run
knows what already exists", use the `upload_directory` helper from
`unitysvc_sellers.resources.upload`. This is the same code path the
`usvc_seller data upload` CLI command uses.

```python
from pathlib import Path
from unitysvc_sellers import Client
from unitysvc_sellers.resources.upload import upload_directory

with Client() as client:
    result = upload_directory(
        client,
        data_dir=Path("./data"),
        dryrun=False,
        task_wait_timeout=600.0,
        task_poll_interval=2.0,
    )

print(f"services: {result.services.success}/{result.services.total}")
print(f"promotions: {result.promotions.success}/{result.promotions.total}")
print(f"groups: {result.groups.success}/{result.groups.total}")

for err in result.services.errors:
    print(" FAILED", err["file"], "→", err["error"])

if result.total_failed:
    raise SystemExit(1)
```

Useful keyword arguments:

-   `dryrun=True` — call every endpoint with the dryrun flag where
    supported; skips task polling entirely (dryrun runs
    synchronously on the backend).
-   `upload_services=False` / `upload_promotions=False` /
    `upload_groups=False` — upload only a subset of the catalog.
-   `on_progress=callable` — a hook that fires on every state
    transition. Signature is `on_progress(kind, status, name,
    detail)`, where `kind` is `"service"`, `"promotion"`, or
    `"group"` and `status` transitions through `"queued"` →
    (`"ok"` or `"error"` or `"dryrun"`). Useful when embedding the
    upload into a larger progress bar or web UI.
-   `task_wait_timeout` / `task_poll_interval` — control how long
    the helper is willing to wait for the async ingest tasks to
    finish.

Returns an `UploadResult` dataclass with per-resource `services` /
`promotions` / `groups` counts (total / success / failed / errors).

## Running connectivity tests locally

The `usvc_seller services run-tests` CLI runs each service's
connectivity test scripts on the seller's own machine, against the
public gateway URL, using the seller's `UNITYSVC_API_KEY` from the
local environment. The SDK exposes everything you need to do the
same thing programmatically.

The flow is:

1.  Fetch the service detail (for its interfaces + documents).
2.  If the service is in `draft` or `rejected`, elevate it to
    `pending` with `run_tests=False` so the backend does not
    auto-queue its own full test suite.
3.  For each executable document, pull its expanded `file_content`.
4.  Run the script locally (per interface) with
    `execute_script_content`, injecting `SERVICE_BASE_URL` /
    `UNITYSVC_API_KEY` / routing_key env vars.
5.  POST the per-interface results back via `documents.update_test`.
6.  Restore the original status on exit.

```python
import os
from unitysvc_sellers import AsyncClient
from unitysvc_sellers.utils import execute_script_content

EXECUTABLE = {"code_example", "connectivity_test"}
ROUTABLE = {"pending", "review", "active"}


async def run_tests(service_id: str) -> int:
    user_api_key = os.environ.get("UNITYSVC_API_KEY", "")
    failed = 0
    async with AsyncClient() as client:
        svc = await client.services.get(service_id)
        original_status = svc.status
        elevated = original_status in ("draft", "rejected")
        try:
            if elevated:
                await client.services.set_status(
                    service_id, {"status": "pending", "run_tests": False}
                )
            docs = [d for d in (svc.documents or []) if d.category in EXECUTABLE]

            for doc in docs:
                full = await client.documents.get(doc.id)
                if not full.file_content:
                    continue
                per_iface = {}
                for iface in svc.interfaces or []:
                    if not iface.is_active:
                        continue
                    env = {
                        "SERVICE_BASE_URL": iface.base_url or "",
                        "UNITYSVC_API_KEY": user_api_key,
                    }
                    for k, v in (iface.routing_key or {}).items():
                        env[k.upper()] = str(v)
                    result = execute_script_content(
                        script=full.file_content,
                        mime_type=full.mime_type or "",
                        env_vars=env,
                        timeout=30,
                    )
                    per_iface[iface.name] = {
                        "status": result["status"],
                        "exit_code": result.get("exit_code"),
                        "stdout": (result.get("stdout") or "")[:10_000],
                        "stderr": (result.get("stderr") or "")[:10_000],
                        "error": result.get("error"),
                    }
                worst = next(
                    (r["status"] for r in per_iface.values() if r["status"] != "success"),
                    "success",
                )
                if worst != "success":
                    failed += 1
                await client.documents.update_test(
                    doc.id, {"status": worst, "tests": per_iface}
                )
        finally:
            if elevated:
                await client.services.set_status(
                    service_id, {"status": original_status, "run_tests": False}
                )
    return failed
```

## Exceptions

All SDK errors derive from `SellerSDKError`. The subclasses map
directly to HTTP status classes so you can catch them narrowly:

| Exception              | Raised when…                                          |
| ---------------------- | ----------------------------------------------------- |
| `AuthenticationError`  | 401 — key missing, invalid, or expired                |
| `PermissionError`      | 403 — key is valid but not authorised for this action |
| `NotFoundError`        | 404 — resource does not exist                         |
| `ValidationError`      | 400 / 422 — request body failed server validation     |
| `ConflictError`        | 409 — e.g., service name already taken                |
| `RateLimitError`       | 429 — retry with the `Retry-After` hint               |
| `ServerError`          | 5xx — backend trouble                                 |
| `APIError`             | Catch-all parent of the above                         |
| `SellerSDKError`       | Root. Also covers non-HTTP failures (config, auth).   |

```python
from unitysvc_sellers import (
    Client,
    NotFoundError,
    ValidationError,
    APIError,
)

try:
    svc = client.services.get("00000000-0000-0000-0000-000000000000")
except NotFoundError:
    print("service does not exist")
except ValidationError as exc:
    print("bad request:", exc.detail)
except APIError as exc:
    print(f"HTTP {exc.status_code}:", exc)
```

Every `APIError` carries:

-   `status_code` (int)
-   `detail` (the parsed `ErrorResponse` from the backend, usually a
    dict, or the raw text for non-JSON responses)
-   `response_body` (the raw bytes, for debugging)

## End-to-end example: mirror a catalog into CI

Combine the pieces into a CI-friendly script that uploads a catalog,
waits for all ingest tasks, and fails the build on any per-service
errors:

```python
#!/usr/bin/env python3
"""CI entrypoint: upload the catalog under ./data and report results."""

import sys
from pathlib import Path

from unitysvc_sellers import Client
from unitysvc_sellers.resources.upload import upload_directory


def main() -> int:
    data_dir = Path("./data").resolve()

    def progress(kind: str, status: str, name: str, detail: str = "") -> None:
        icon = {"queued": "·", "ok": "✓", "error": "✗", "dryrun": "→"}.get(status, "?")
        print(f"  {icon} {kind}: {name} [{status}] {detail}")

    with Client() as client:
        result = upload_directory(
            client,
            data_dir=data_dir,
            on_progress=progress,
            task_wait_timeout=900.0,
            task_poll_interval=3.0,
        )

    print()
    print(f"services:   {result.services.success}/{result.services.total} ok")
    print(f"promotions: {result.promotions.success}/{result.promotions.total} ok")
    print(f"groups:     {result.groups.success}/{result.groups.total} ok")

    for err in (*result.services.errors, *result.promotions.errors, *result.groups.errors):
        print(f"  FAILED {err.get('file', '?')} → {err.get('error')}")

    return 1 if result.total_failed else 0


if __name__ == "__main__":
    sys.exit(main())
```

Drop that in `scripts/upload_catalog.py`, wire
`UNITYSVC_SELLER_API_KEY` and `UNITYSVC_SELLER_API_URL` into your
CI secrets, and call it from a GitHub Actions workflow:

```yaml
- name: Upload catalog
  env:
    UNITYSVC_SELLER_API_KEY: ${{ secrets.UNITYSVC_SELLER_API_KEY }}
    UNITYSVC_SELLER_API_URL: ${{ secrets.UNITYSVC_SELLER_API_URL }}
  run: python scripts/upload_catalog.py
```

## See also

-   [Getting Started](getting-started.md) — install, configure, and
    upload your first catalog.
-   [CLI Reference](cli-reference.md) — every `usvc_seller` command,
    much of which is implemented on top of the APIs above.
-   [Workflows](workflows.md) — higher-level patterns for manual,
    web-assisted, and automated catalog authoring.
-   [File Schemas](file-schemas.md) — the provider / offering /
    listing payload shapes the SDK accepts.
