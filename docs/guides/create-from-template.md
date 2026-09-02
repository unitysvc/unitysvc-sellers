# Create from a System Template

The fastest way to publish a common service type is to use a **system
template**: a template the platform publishes, such as an OpenAI-compatible LLM
endpoint or a PlatformService member template. You supply a small param file
under `specs/`; `usvc seller specs upload` sends it to the backend, where the
template is rendered into a normal private seller service.

For the bigger picture, including PlatformService membership, see
[Service Templates](../service-templates.md).

## 1. Browse the Catalog

```bash
usvc seller templates list
usvc seller templates show openai-compatible-llm
```

`templates show` lists each parameter's name, type, and whether it is required.
Secret-typed parameters take the **name** of a seller secret, never the secret
value itself.

## 2. Author a Param File

A system-template param file has the same shape as a local-template param file:
`{ "template", "parameters" }`. Its path under `specs/` becomes the service
name.

```
specs/
└── acme/
    ├── gpt.json
    └── gpt.service.json    # written after upload; commit this sidecar
```

```jsonc
// specs/acme/gpt.json
{
  "template": "openai-compatible-llm",
  "parameters": {
    "api_base_url": "https://api.acme.ai/v1",
    "api_key_secret_name": "UPSTREAM_API_KEY",
    "input_price": 1.00
  }
}
```

If `template` names a directory under your local `templates/`, the SDK renders
it locally for validate/test/upload. If it does not resolve locally, `specs
upload` treats it as a system template and calls backend instantiation.

## 3. Upload

```bash
usvc seller specs upload           # all service definitions under specs/
usvc seller specs upload acme/gpt  # one service, by fnmatch selector
usvc seller specs upload --submit  # render and submit for review in one task
```

On success, the backend-assigned `service_id` is written to
`specs/<name>.service.json`. Commit that sidecar. Re-running `specs upload`
passes the `service_id` back to the backend so the service is updated or revised
in place rather than duplicated.

If the system template is linked to a PlatformService, no extra seller command is
needed. The generated private service becomes a PlatformService member after it
passes review and reaches the active state.

For repos that manage these memberships as files, keep them under
`platform_services/<platform-service>/<provider>/<member>.json` and set
`parameters.service_name` to that same path. See
[Platform Service Members](platform-service-members.md) for the full layout.

## From the SDK

`client.templates` browses the catalog; `client.instances.create` starts the
same backend render directly:

```python
from unitysvc_sellers import Client

with Client() as client:
    result = client.instances.create(
        "openai-compatible-llm",
        parameters={
            "api_base_url": "https://api.acme.ai/v1",
            "api_key_secret_name": "UPSTREAM_API_KEY",
            "input_price": 1.00,
        },
        auto_submit=True,
    )
    print(result.task_id)
```

The CLI file workflow is preferred for CI because it keeps the service name,
template parameters, and sidecar identity in version control.
