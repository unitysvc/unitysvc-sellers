# Container services

Use `unitysvc-core>=0.3.10` and the `container` access method. Keep a concrete service under `services/specs/<provider>/<name>/` with `provider.json`, `offering.json`, `listing.json`, and an offering Document of category `instance_spec` pointing to a Compose file (`meta.format: compose`). A channel references that Document by title through `spec` and declares its Kubernetes-style `resources` there. Multiple Compose services require a complete per-service allocation within that tier.

Container channels are enrollable and request `resource:container` creation. Public `entries` select a Compose service and its container port. These are distinct from standard Compose `ports`; the public HTTPS endpoint still uses port 443.

The existing upload and service-diagnostic APIs carry container services through the normal provider/offering/listing and Document flow. Validation and normalization come from unitysvc-core; no compute intent/status API is exposed in the seller SDK.

## Local connectivity test

```sh
usvc seller specs validate
usvc seller specs format
usvc seller specs run-tests <provider>/<name> --force
```

The local command explicitly runs Docker: it pulls digest-pinned images, starts the core compiler's normalized services on an isolated bridge network, waits for the declared health checks (or default TCP readiness), fetches every entry, runs optional declarative JSON `connectivity_test` probes, and removes the containers/network even on failure. Bindings and Compose restrictions are validated before starting containers. Each run uses a fresh random `${UNITYSVC_INSTANCE_API_KEY}` value; it never imports a real key or other environment variable from the host, mounts host data, or forwards UnitySVC credentials. Readiness is capped at 120 seconds. Local Docker does not assert Kubernetes/gVisor behavior or ephemeral-storage quotas.

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
