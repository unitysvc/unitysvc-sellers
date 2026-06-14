# Operate Live Services

Once a service exists on the platform you manage it with `usvc_seller services …`
(or `client.services` from the SDK). Services are targeted by **`service_name`**
(= `listing.name`) as a literal or fnmatch pattern, e.g. `acme/llama-8b` or
`'acme/*'`; omit the name to act on everything you own. For *what happens after a
service goes live* (review, billing, payouts) see
[After You Publish](../seller-lifecycle.md).

## Inspect

```bash
usvc_seller services list                 # everything you own, with status & visibility
usvc_seller services show acme/llama-8b   # documents, access interfaces, full detail
```

## Move through review

The status lifecycle (see [Services](../services.md#service-status-and-updates)):

```bash
usvc_seller services submit    acme/llama-8b   # draft|rejected → pending
usvc_seller services withdraw  acme/llama-8b   # pending|rejected → draft
usvc_seller services deprecate acme/llama-8b   # mark a live service deprecated
```

Each accepts a pattern (`'acme/*'`) plus `--all`, `--provider`, and `--yes` for
bulk, non-interactive operation in CI.

## Control visibility

Visibility is independent of status — set it any time; it takes effect once the
service is active.

```bash
usvc_seller services set-visibility public   acme/llama-8b   # listed in the marketplace
usvc_seller services set-visibility unlisted acme/llama-8b   # reachable by link, not listed
usvc_seller services set-visibility private  acme/llama-8b   # hidden entirely
```

## Update a live service

There are two ways to change a service that already exists:

**Patch it directly** — for quick, targeted changes to a live service without
re-uploading files:

```bash
usvc_seller services update acme/llama-8b --visibility public
usvc_seller services update acme/llama-8b --set-routing-var model=llama-3.3-70b
usvc_seller services update acme/llama-8b --set-price '{"type":"one_million_tokens","input":"0.9","output":"0.9"}'
```

`services update` can change **visibility**, **routing vars**
(`--set-routing-var` / `--remove-routing-var` / `--load-routing-vars`), and the
**list price** (`--set-price` / `--remove-price-field`).

**Re-upload its specs** — for content changes (documentation, upstream config,
pricing shape). Edit the files and run [`specs upload`](author-specs.md); the SDK
matches the service by the `service_id` in `service.json`.

### Live services update through revisions

When you re-upload (or otherwise change) a service that is already `active`, the
change lands as a **draft revision** rather than editing the live service in
place — customers keep hitting a stable service until the revision is reviewed
and activated. The `service_id` never changes, so subscriptions and enrollments
are undisturbed. Subsequent uploads keep updating the same revision until it's
activated.

## Test live services

Beyond the local `specs run-tests`, you can exercise a deployed service
end-to-end through the gateway with a server-side diagnostic:

```bash
usvc_seller services run-tests  acme/llama-8b   # run its testable documents server-side
usvc_seller services list-tests acme/llama-8b   # which documents are testable
usvc_seller services show-test  acme/llama-8b   # latest result for a document
usvc_seller services skip-test  acme/llama-8b   # exclude a doc from testing…
usvc_seller services unskip-test acme/llama-8b  # …and put it back
```

See [Test Services](../code-examples.md) for authoring the testable documents.
