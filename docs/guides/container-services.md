# Container services

Use `unitysvc-core>=0.3.12` and the `container` access method. Keep a concrete service under `services/specs/<provider>/<name>/` with `provider.json`, `offering.json`, `listing.json` and the Compose file. Each channel declares its Kubernetes-style `resources`; multiple Compose services require a complete per-service allocation within that tier.

## The instance spec

An offering has **exactly one** instance spec, and every container channel (tier) runs it, so tiers differ in `resources`, not in stack. Write it as an offering-level shortcut, the way `logo` works:

```json
"service_type": "container",
"instance_spec": "compose.yaml"
```

The value is a path relative to `offering.json` or an https URL. On upload the SDK expands it to a Document titled `Instance spec` (category `instance_spec`, `meta.format: compose`, not public); a path is uploaded like any other file. Writing that Document by hand (with exactly one of `file_path` and `external_url`) is equivalent, but an offering may not have both forms.

### A URL is a snapshot, not a link

```json
"instance_spec": "https://github.com/acme/stacks/blob/3f2a9c1d.../compose.yaml"
```

`specs upload` does **not** download the URL. It sends it as the Document's `external_url`; the platform fetches it once at ingest, stores the bytes, keeps your URL in `meta.source`, and validates the snapshot (a failed fetch or an invalid file fails the upload). Nothing is fetched at enrollment, so what runs is what was approved: re-upload to refresh the snapshot. The platform accepts https only, with a size limit and a timeout, and refuses private addresses. Prefer a commit-SHA permalink; a branch URL (`/main/`) works but warns, because it can change after you tested it. To pin the bytes, add the file's digest to a Document form with `meta.sha256` (64 lowercase hex characters); the upload is refused if the snapshot differs.

For `specs validate` and the local Docker `run-tests` the SDK downloads the file itself, into memory (never into your tree), under the same rules: https only, at most 1 MiB, a 15 second timeout, at most 3 redirects that must stay https, no private, loopback or link-local host (checked again after every redirect), and `github.com/<owner>/<repo>/blob/<ref>/<path>` pages rewritten to `raw.githubusercontent.com`. `specs format` never touches a remote file.

### Images, `env_file` and variables

An image may be a tag (`ghcr.io/acme/app:1.4`) or untagged: it is accepted with a warning, the platform runs it as written and records the digest it resolved. A digest you write (`app@sha256:...`) is honored as written; a malformed digest is an error. Pin by digest when you need exactly the bytes you tested.

`env_file` is ignored, with a loud warning, because the file is not part of the upload. Supply the variables it would have held with `meta.environment` on the Document form: a map from Compose service name to `NAME: "value"`, merged over the file's own `environment` when the spec is compiled. The Compose file itself is not edited, `${UNITYSVC_INSTANCE_API_KEY}` works as a value, and a bare `KEY` in the file takes the overlay's value. Only `environment` can be overlaid, and every service named must exist in the file.

```json
"documents": {
  "Instance spec": {
    "category": "instance_spec",
    "external_url": "https://github.com/acme/stacks/blob/3f2a9c1d.../compose.yaml",
    "meta": {
      "sha256": "<64 hex characters>",
      "environment": {"gateway": {"API_KEY": "${UNITYSVC_INSTANCE_API_KEY}"}}
    }
  }
}
```

This is how you reuse a project's generic Compose file as it is (see `weixin-ilink-gateway-upstream` in unitysvc-core's examples). `specs validate` and the local test apply the overlay the same way the platform does.

### Scratch storage

A named or anonymous volume mount (`data:/app/data`) becomes scratch space: the path exists and is writable, its data survives a container restart but not a replacement of the instance, and it counts against the service's `ephemeral-storage`. Host paths and bind mounts are still refused. To keep the files between runs, see [Persistent storage](#persistent-storage). The local Docker test gives each scratch path a disposable disk-backed volume (removed afterwards), so it counts against disk, not memory.

### Persistent storage

Scratch is lost when the instance is replaced. To keep a volume's files between runs, persist it **in the channel**, not in the Compose file. The file stays plain Compose (it runs unchanged under Docker), so one file can back a channel that persists a volume (a production tier) and one that does not (a demo). Persistence needs `unitysvc-core>=0.3.20`.

The Compose file only mounts a named volume, and declares it at the top level:

```yaml
services:
  app:
    image: example/app:1.4
    ports: [8080]
    volumes:
      - data:/var/lib/app
volumes:
  data:
```

The channel's `volumes` maps a volume name to how it is backed. `type` is `scratch` (the default) or `persist`, and each type takes its own options:

```json
"upstream_access_config": {
  "base": {
    "access_method": "container",
    "resources": "nano",
    "customer_access_requests": [
      {
        "object": "service:home",
        "permissions": ["read", "write"],
        "options": "path=app/",
        "required": true,
        "justification": "Keeps the app's data in the app folder of your home between runs."
      }
    ],
    "volumes": {
      "data": {
        "type": "persist",
        "source": "{{ home.path }}/app",
        "mode": "rw",
        "exclude": ["*-wal", "*-shm"]
      }
    }
  }
}
```

| Option | Meaning |
|---|---|
| `source` | Where the files live: `{{ storage.path }}/<folder>` (the enrollment's own folder in the customer's storage; the default is a folder named like the volume) or `{{ home.path }}/<folder>` (a folder of the customer's home). Nothing else is accepted: no other variable, no URL. A folder is relative, with segments of letters, digits, `.`, `_` and `-` (not starting with `.`, no `..`, no empty segment). |
| `mode` | `rw` (the default): restored before the service starts and copied back. `ro`: restored only; changes are discarded when the instance stops. |
| `exclude` | At most 32 globs, relative to the directory, left out both ways. They follow Go's `path.Match` syntax (`*`, `?`, `[...]`), plus `**` across folders; a malformed class such as `[]` or `[a` is an error. |
| `uid`, `gid` | The owner of the restored files, for an image that runs as a non-root user. Both or neither, from 0 to 2^63-1. |

**What the platform does.** Files are restored before the service starts, copied while it runs (about every 30 seconds) and once more when it stops. A stop waits for that last copy, and the customer sees the instance as `draining`; a copy that fails fails the stop and leaves the instance running. Copying only adds and replaces: nothing is ever deleted from storage, so a file the service removes can come back at the next start. Empty files, symbolic links and files over 1 GiB are not stored, and a crash can lose the last 30 seconds of writes.

**The customer must approve the storage access.** Both stores belong to the customer, so the channel asks for them in `customer_access_requests`, as a `required` request: `service:storage` for the enrollment's folder (no options), or `service:home` with a `path` option that covers the folder. Every persisted volume needs `read` (the restore reads), and `rw` needs `write` as well. A persisted volume with no such request is a `persist_not_requested` error. The platform's own connectivity test approves a channel's required requests, as a customer does when enrolling, so the test can start the instance.

**Choosing `storage` or `home`.**

- `{{ storage.path }}` is the enrollment's folder. It is gone from the customer's view with the enrollment: unenrolling and enrolling again creates a new instance at a new address with **no data**.
- `{{ home.path }}/<folder>` belongs to the customer, so a later enrollment of the service finds it. The folder is then shared by every enrollment of that customer, and two running instances would overwrite each other's copy. Allow one active enrollment per customer in the listing:

  ```json
  "service_options": {"enrollment": {"limit_per_customer": 1}}
  ```

**Rules `specs validate` checks** (the codes are in the report):

- Each key of `volumes` must be a top-level volume of the Compose file (`overlay_volume`), and a persisted one must be mounted by a service (`persist_unmounted`). Only named volumes can be persisted, not anonymous ones or bind mounts.
- A volume is mounted at one path of one service, a path is not both scratch and persisted, and two persisted folders of one store cannot be the same or nested (`shared` and `shared/db` would map files of two volumes to the same objects).
- `x-unitysvc-persist` on a volume of the file is an error (`persist_in_file`): persistence is declared in the channel.
- `type` must be `scratch` or `persist`, and an option the type does not have is an error.

**Writing a recipe that persists**

- **SQLite in WAL mode:** exclude `*-wal` and `*-shm`. Copying never deletes, so an earlier copy of a write-ahead file would be restored beside a newer database, and SQLite's documentation warns that mixing a database with a write-ahead file from another point in time can corrupt it. A clean stop copies the database after the app has exited and checkpointed.
- **First-run settings:** with persisted data, an app's first-run setup (an initial administrator password, for example) only happens the first time. A later enrollment, or a changed parameter, does not change what the data already holds, so say so in the service's guide.
- **Say what is kept:** state in the guide which folders persist, which mode they use, what a crash can lose, and that the platform never deletes the stored files.

**Testing.** `specs validate` checks the rules above, including the access requests. The local Docker `run-tests` runs a persisted volume as a plain scratch volume, because there is no customer storage on your machine; the persistence itself is exercised by the platform test (`services run-tests`) and by a real enrollment.

### No per-channel `spec`

A channel has no `spec` field: there is nothing to name, because every channel runs the offering's one instance spec. Writing `spec` on a channel is an error.

Container channels are enrollable and request `resource:container` creation. Public `entries` select a Compose service and its container port. These are distinct from standard Compose `ports`; the public HTTPS endpoint still uses port 443.

The existing upload and service-diagnostic APIs carry container services through the normal provider/offering/listing and Document flow. Validation and normalization come from unitysvc-core; no compute intent/status API is exposed in the seller SDK.

## Pricing

A container channel's price is its instance time, and the platform's cost for the instance is the **base cost** of the size the channel names (`resources`). Two shapes:

**You take payment.** Price each tier above base cost and set `payout_price` to a revenue share, which is paid on the part of the price above base cost. Either a time price you choose, or a margin composed around the platform's cost so it follows the size table:

```json
"list_price": {"type": "channel", "default": "base",
  "channels": {"base": {"type": "multiply", "factor": "1.2", "base": {"type": "base_cost"}}}}
```

```json
"payout_price": {"type": "revenue_share", "percentage": "80", "description": "80% of the price after the platform's compute cost"}
```

**You take no payment.** If you do not or cannot take payment, for example you are the author of an open-source project and want visitors to preview or run it, list the service at cost: the bare leaf.

```json
"list_price": {"type": "base_cost"}
```

`{"type": "base_cost"}` is the platform's cost of the channel's size for the metered runtime, like `constant` is a fixed amount: the platform derives the figure from the size table, so you never copy a number that goes stale, and fills `price` with the resolved monthly figure, which the catalog shows and sorts by, while each run is priced from the table as it is when the run starts. At cost you earn nothing whatever your `payout_price`; a margin composed around the leaf (`multiply` by a factor, or `add` a `one_month` price) is yours under your revenue share. `specs validate` rejects `base_cost` wherever it does not price a container channel of the offering, and as a `payout_price`. See [`base_cost` in the pricing reference](../pricing.md#the-platforms-cost-as-a-price-base_cost). It needs `unitysvc-core>=0.3.19`.

## Local connectivity test

```sh
usvc seller specs validate
usvc seller specs format
usvc seller specs run-tests <provider>/<name> --force
```

The local command explicitly runs Docker: it pulls the images (a tag is allowed), starts the core compiler's normalized services on an isolated bridge network, waits for the declared health checks (or default TCP readiness), fetches every entry, runs optional declarative JSON `connectivity_test` probes, and removes the containers/network even on failure. Bindings and Compose restrictions are validated before starting containers. Each run applies the Document's `meta.environment` overlay and uses a fresh random `${UNITYSVC_INSTANCE_API_KEY}` value; it never imports a real key or other environment variable from the host, mounts host data, or forwards UnitySVC credentials. Readiness is capped at 120 seconds. Local Docker does not assert Kubernetes/gVisor behavior or ephemeral-storage quotas.

A JSON probes document has the shared core shape:

```json
{"probes":[{"entry":"api","path":"/status","expect_status":200,"expect_body_contains":"\"ok\":true"}]}
```

For an `auth: app` entry the test sends the generated instance key as a bearer token. Authentication at the platform's edge is outside this local test. The initial backend requires a declarative JSON probes document for its recorded cluster test, a container-only offering and one public entry per channel; arbitrary parameter/secret bindings and forwarding through the API gateway are still deferred.

`specs validate` prints core's warnings, including dropped Compose options and loud storage/start-order warnings. A successful local test records upstream status in the usual service sidecar; upload remains a separate action.

## Upload and platform test

```sh
usvc seller specs upload <provider>/<name>
usvc seller services run-tests <provider>/<name> --force
```

The platform test provisions only the ops enrollment's temporary instance on the configured compute cluster, waits for readiness, fetches its entries/probes over HTTPS, deletes it and records the result. It starts the instance for each container channel, waits for the agent to report every service ready, fetches every entry and then every check of your `connectivity_test` document (or preset), and **always removes the instance afterwards**, whether the tests passed or not. One row is recorded per (document, channel); `run-tests` prints it with the channel, and for a container run the readiness and per-entry lines under it:

```text
  ✓ 1a2b3c4d… probes.json (channel base): success
      every service passed readiness on the compute cluster
      web/: HTTP 200
      web/status: HTTP 200
```

A run fails, with the reason, when the instance does not become ready (for example `progress_deadline_exceeded`, or an image the cluster does not allow), when an entry or check answers with the wrong status or lacks the expected text, or when a route is still unreachable after a few retries; no check runs against an instance that did not start. A service with no connectivity test cannot be tested: `run-tests` exits non-zero and prints the platform's reason. A container channel cannot yet share a service with another channel. The service stays private and the diagnostic restores its original status. Each enrollment's address is its enrollment code under the deployment's apps domain; no extra admin hostname is created.

The reserved instance key is an application credential, separate from a UnitySVC API key. Keep actual keys out of Compose, documents and source control. Containers use temporary storage unless the channel persists a volume (see [Persistent storage](#persistent-storage)).
