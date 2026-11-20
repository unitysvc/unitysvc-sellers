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

A named or anonymous volume mount (`data:/app/data`) becomes scratch space: the path exists and is writable, its data survives a container restart but not a replacement of the instance, and it counts against the service's `ephemeral-storage`. Host paths and bind mounts are still refused. The local Docker test gives each scratch path a disposable disk-backed volume (removed afterwards), so it counts against disk, not memory.

### No per-channel `spec`

A channel has no `spec` field: there is nothing to name, because every channel runs the offering's one instance spec. Writing `spec` on a channel is an error.

Container channels are enrollable and request `resource:container` creation. Public `entries` select a Compose service and its container port. These are distinct from standard Compose `ports`; the public HTTPS endpoint still uses port 443.

The existing upload and service-diagnostic APIs carry container services through the normal provider/offering/listing and Document flow. Validation and normalization come from unitysvc-core; no compute intent/status API is exposed in the seller SDK.

## Pricing

A container channel's price is its instance time, and the platform's cost for the instance is the **base cost** of the size the channel names (`resources`). Two shapes:

**You take payment.** Price each tier with a time price above base cost in a channel-keyed `list_price`, and set `payout_price` to a revenue share, which is paid on the part of the price above base cost:

```json
"list_price": {"type": "channel", "default": "base",
  "channels": {"base": {"type": "one_month", "price": "9", "description": "$9 / month"}}}
```

```json
"payout_price": {"type": "revenue_share", "percentage": "80", "description": "80% of the price after the platform's compute cost"}
```

**You take no payment.** If you do not or cannot take payment, for example you are the author of an open-source project and want visitors to preview or run it, declare the listing at cost and decline the payout:

```json
"list_price": {"type": "base_cost"}
```

```json
"payout_price": {"type": "revenue_share", "percentage": "0"}
```

The customer pays what the platform pays for the instance, and the platform derives the figure from the size, so it follows the platform's size table and you never copy a number that goes stale. Anything you write in `price` beside `base_cost` is ignored. To offer a fixed markup on top of cost, add `"markup": "1.00"` (an amount per month of continuous runtime, billed by the instance minute); the markup stays with the platform. `specs validate` rejects `base_cost` on a service that is not container-only, as a `payout_price`, and next to a non-zero payout. See [`base_cost` in the pricing reference](../pricing.md#container-services-at-cost-base_cost). It needs `unitysvc-core>=0.3.17`.

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

The platform test provisions only the ops enrollment's temporary instance on the configured compute cluster, waits for readiness, fetches its entries/probes over HTTPS, deletes it and records the result. The service stays private and the diagnostic restores its original status. Each enrollment's address is its enrollment code under the deployment's apps domain; no extra admin hostname is created.

The reserved instance key is an application credential, separate from a UnitySVC API key. Keep actual keys out of Compose, documents and source control. Containers use temporary storage unless a future contract explicitly provides persistence.
