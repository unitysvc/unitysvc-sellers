# Workflows

This guide explains the different workflows for managing service data with the UnitySVC Seller SDK.

**Note:** All examples use the `usvc_seller` CLI (installed as a console entry point by the `unitysvc-sellers` package). For programmatic access to the same operations, see the [SDK Guide](sdk-guide.md).

## Overview

UnitySVC provides two ways to create and manage service data:

1. **Web Interface** ([unitysvc.com](https://unitysvc.com)) - Create and edit data visually
2. **SDK** (this tool) - Manage data locally with version control and automation

The SDK supports these workflows:

1. **Web-to-SDK Workflow** - Start with web interface, export to SDK for version control
2. **Manual Workflow** - Create/edit files locally for small catalogs
3. **Automated Workflow** - Script-based generation for large or dynamic catalogs

```mermaid
flowchart TB
    subgraph WebStart["Getting Started"]
        W1[Web Interface] --> W2[Export Data]
        W2 --> W3[Local Files]
    end

    subgraph Manual["Manual/Ongoing"]
        W3 --> A2[Edit Files]
        A2 --> A3[usvc_seller data validate]
        A3 --> A4[usvc_seller data format]
        A4 --> A5[usvc_seller data upload]
    end

    subgraph Automated["Automated Workflow"]
        B1[Configure populate script] --> B2[usvc_seller data populate]
        B2 --> B3[usvc_seller data validate]
        B3 --> B4[usvc_seller data format]
        B4 --> B5[usvc_seller data upload]
    end

    subgraph Platform["UnitySVC Platform"]
        A5 --> C[Backend API]
        B5 --> C
        C --> D[Service Available]
    end
```

## Web-to-SDK Workflow

**Recommended for getting started.** Use the web interface for initial setup, then transition to SDK for version control.

### Step-by-Step Process

#### 1. Create Data via Web Interface

1. Go to [unitysvc.com](https://unitysvc.com) and sign in
2. Create your Provider, Offerings, and Listings using the visual editor
3. Export your data as JSON/TOML files

#### 2. Set Up Local Directory

Place exported files in the expected structure:

```
data/
└── my-provider/
    ├── provider.json
    └── services/
        └── my-service/
            ├── offering.json
            └── listing.json
```

#### 3. Validate and Upload

```bash
usvc_seller data validate
usvc_seller data format
usvc_seller data upload
```

#### 4. Ongoing Management

After initial setup, manage changes locally:

- Edit files directly
- Use `usvc_seller data validate` to check changes
- Commit to git for version control
- Use CI/CD for automated uploads

## Manual Workflow

Best for:

- Small number of services (< 20)
- Teams comfortable editing JSON/TOML directly
- Situations where web interface isn't preferred

### Step-by-Step Process

#### 1. Create Files Manually

Create files following the [File Schemas](file-schemas.md) documentation:

```
data/
└── my-provider/
    ├── provider.json          # See provider_v1 schema
    └── services/
        └── my-service/
            ├── offering.json  # See offering_v1 schema
            └── listing.json   # See listing_v1 schema
```

#### 2. Edit Your Files

Fill in your service details:

- Provider information (name, contact, metadata)
- Service offering details (API endpoints, pricing, capabilities)
- Service listing details (user-facing info, documentation)

#### 3. Validate Data

```bash
usvc_seller data validate
```

Fix any validation errors. Common issues:

- Directory names not matching field values
- Missing required fields
- Invalid file paths

#### 4. Format Files (Optional)

```bash
usvc_seller data format
```

This ensures:

- JSON files have 2-space indentation
- Files end with single newline
- No trailing whitespace

#### 5. Edit Local Files as Needed

Edit JSON/TOML files directly to update service status or other fields. The file-based approach gives you full control and integrates naturally with version control.

#### 6. Upload to Platform

```bash
# Set credentials
export UNITYSVC_API_URL="https://api.unitysvc.com/v1"
export UNITYSVC_SELLER_API_KEY="your-api-key"

# Upload all services
cd data
usvc_seller data upload

# Or from parent directory
usvc_seller data upload --data-path ./data
```

#### 7. Verify on Platform

```bash
# List your services
usvc_seller services list

# Or list with custom fields for focused output
usvc_seller services list --fields id,name,status

# Filter by status
usvc_seller services list --status active
```

#### 8. Publish to Marketplace

After your service is activated (approved by admin), it starts as **unlisted**. Set visibility to `public` when you're ready for it to appear in the catalog:

```bash
# Publish a specific service
usvc_seller services update <service-id> --visibility public

# Or publish all active services at once
usvc_seller services set-visibility --all --visibility public --yes
```

See [Seller Lifecycle](seller-lifecycle.md#visibility) for details on visibility settings.

### Version Control Integration

```bash
# After creating/updating files
git add data/
git commit -m "Add new service: my-service"
git push

# Upload from CI/CD
usvc_seller data validate
usvc_seller data upload --data-path ./data
```

## Automated Workflow (Template-Based)

Best for providers with:

- Large service catalogs (> 20 services)
- Frequently changing services
- Dynamic pricing or availability
- Services added/deprecated automatically

### How It Works

The template-based approach separates **structure** (Jinja2 templates) from **data** (a populator script):

```mermaid
flowchart LR
    subgraph "One-Time Setup"
        A[Create service on unitysvc.com] --> B[Export offering.json & listing.json]
        B --> C[Save as .j2 templates]
        C --> D[Replace variables with {{ placeholders }}]
    end

    subgraph "Ongoing Population"
        E[Populator script reads upstream API] --> F[Renders templates per service]
        D --> F
        F --> G[services/model-name/offering.json]
        F --> H[services/model-name/listing.json]
    end
```

The script is invoked by `usvc_seller data populate`, which reads a
`[services_populator]` section in `provider.toml` to decide what to
run. The script itself can be written in any language — Python,
Node, shell — and just needs to write the generated files into
`services/{name}/` under the provider directory.

### Step-by-Step Process

#### 1. Create a Working Service on unitysvc.com

Start by creating a single service through the web interface:

1. Go to [unitysvc.com](https://unitysvc.com) and sign in
2. Create your Provider and one Service manually
3. Configure all fields, test that it works end-to-end
4. Export the working `offering.json` and `listing.json` files

#### 2. Convert Exported Files to Templates

Create `data/my-provider/templates/` directory and save the exported files as `.j2` templates:

```
data/my-provider/
├── provider.toml
├── templates/
│   ├── offering.json.j2    # Template for offering
│   └── listing.json.j2     # Template for listing
├── scripts/
│   └── update_services.py  # Yields model dictionaries
└── services/               # Generated output
```

#### 3. Replace Variable Parts with Template Variables

Edit the `.j2` files to replace model-specific values with Jinja2 placeholders:

**`templates/offering.json.j2`**:
```jinja2
{
  "schema": "offering_v1",
  "name": "{{ name }}",
{%- if display_name %}
  "display_name": "{{ display_name }}",
{%- endif %}
  "description": "{{ description | default('', true) }}",
  "service_type": "{{ service_type }}",
  "status": "{{ status | default('ready') }}",
  "currency": "USD",
  "details": {
    "model_name": "{{ model_name }}"
{%- for key, value in details.items() %},
    "{{ key }}": {{ value | tojson }}
{%- endfor %}
  },
  "payout_price": {
    "type": "revenue_share",
    "percentage": "100.00"
  },
  "upstream_access_config": {
    "{{ provider_display_name }} API": {
      "access_method": "http",
      "api_key": "${ secrets.{{ api_key_secret }} }",
      "base_url": "{{ api_base_url }}"
    }
  }
}
```

**`templates/listing.json.j2`**:
```jinja2
{
  "schema": "listing_v1",
  "display_name": "{{ display_name | default(name) }}",
  "status": "{{ listing_status | default('ready') }}",
  "currency": "USD",
{%- if pricing %}
  "list_price": {
    "type": "{{ pricing.type }}"
{%- if pricing.input is defined %},
    "input": "{{ pricing.input }}",
    "output": "{{ pricing.output }}"
{%- elif pricing.price is defined %},
    "price": "{{ pricing.price }}"
{%- endif %}
  },
{%- endif %}
  "user_access_interfaces": {
    "provider_api": {
      "access_method": "http",
      "base_url": "${API_GATEWAY_BASE_URL}/p/{{ gateway_path }}"
    }
  },
  "documents": {
{%- if service_type == 'image_generation' %}
    "Python code example": {
      "category": "code_example",
      "file_path": "../../docs/code_example_image.py.j2",
      "mime_type": "python",
      "is_public": true
    }
{%- else %}
    "Python code example": {
      "category": "code_example",
      "file_path": "../../docs/code_example.py.j2",
      "mime_type": "python",
      "is_public": true
    }
{%- endif %}
  }
}
```

#### 4. Write Script to Generate Service Files

Create `scripts/update_services.py` that fetches from your API,
renders the templates, and writes one pair of files per service
into `services/{name}/`:

```python
#!/usr/bin/env python3
"""Generate services from upstream API + Jinja2 templates.

This script is invoked by `usvc_seller data populate`. It reads the
provider's upstream API, renders the local .j2 templates for every
service, and writes the results into services/{name}/ under the
provider directory.
"""

import json
import os
from pathlib import Path

import jinja2
import requests

PROVIDER_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROVIDER_DIR / "templates"
SERVICES_DIR = PROVIDER_DIR / "services"


def fetch_models() -> list[dict]:
    """Fetch models from the provider's upstream API."""
    api_key = os.environ["MY_PROVIDER_API_KEY"]
    resp = requests.get(
        "https://api.myprovider.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    resp.raise_for_status()
    return resp.json()["models"]


def determine_service_type(model: dict) -> str:
    if "embedding" in model["id"].lower():
        return "embedding"
    if "image" in model["id"].lower():
        return "image_generation"
    return "llm"


def extract_pricing(model: dict) -> dict | None:
    if "pricing" not in model:
        return None
    p = model["pricing"]
    return {
        "type": "one_million_tokens",
        "input": str(p.get("input_per_million", 0)),
        "output": str(p.get("output_per_million", 0)),
    }


def build_context(model: dict) -> dict:
    """Flatten an upstream model record into template variables."""
    return {
        # Required — becomes the service directory name.
        "name": model["id"],
        # Offering fields.
        "display_name": model.get("display_name"),
        "description": model.get("description", ""),
        "service_type": determine_service_type(model),
        "status": "ready" if model.get("active") else "draft",
        "model_name": model["full_name"],
        "details": {
            "contextLength": model.get("context_length"),
            "supportsTools": model.get("supports_tools", False),
        },
        # Listing fields.
        "listing_status": "ready",
        "pricing": extract_pricing(model),
        # Provider-specific constants.
        "provider_display_name": "My Provider",
        "api_key_secret": "MY_PROVIDER_API_KEY",
        "api_base_url": "https://api.myprovider.com/v1",
        "gateway_path": "myprovider",
    }


def render_and_write(env: jinja2.Environment, name: str, context: dict) -> None:
    service_dir = SERVICES_DIR / name
    service_dir.mkdir(parents=True, exist_ok=True)
    for template_name, output_name in (
        ("offering.json.j2", "offering.json"),
        ("listing.json.j2", "listing.json"),
    ):
        template = env.get_template(template_name)
        rendered = template.render(**context)
        # Validate JSON before writing so a broken template fails
        # loudly instead of producing a half-written file.
        json.loads(rendered)
        (service_dir / output_name).write_text(rendered)


def main() -> None:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
    )

    existing = {p.name for p in SERVICES_DIR.iterdir() if p.is_dir()} if SERVICES_DIR.exists() else set()
    generated: set[str] = set()

    for model in fetch_models():
        if not model.get("is_available"):
            continue
        context = build_context(model)
        render_and_write(env, context["name"], context)
        generated.add(context["name"])

    # Auto-deprecate services that disappeared upstream. The next
    # `usvc_seller data upload` will propagate status=deprecated to
    # the backend.
    for stale_name in existing - generated:
        listing = SERVICES_DIR / stale_name / "listing.json"
        if listing.exists():
            data = json.loads(listing.read_text())
            if data.get("status") != "deprecated":
                data["status"] = "deprecated"
                listing.write_text(json.dumps(data, indent=2) + "\n")

    print(f"Generated {len(generated)} services, deprecated {len(existing - generated)}")


if __name__ == "__main__":
    main()
```

#### 5. Configure Provider to Run the Script

Create `data/my-provider/provider.toml`:

```toml
schema = "provider_v1"
name = "my-provider"
display_name = "My Service Provider"

[services_populator]
command = "scripts/update_services.py"
requirements = ["requests"]

[services_populator.envs]
MY_PROVIDER_API_KEY = ""  # Set via environment variable
```

#### 6. Run Populate Command

```bash
# Generate all services
usvc_seller data populate

# Generate for specific provider only
usvc_seller data populate --provider my-provider

# Dry run to see what would execute
usvc_seller data populate --dry-run
```

Output shows progress:
```
[1/50] llama-3-70b
  OK: llm
[2/50] gpt-4-turbo
  OK: llm
...
  Deprecated: old-model-v1
  Deprecated: legacy-service

Done! Total: 50, Written: 45, Skipped: 3, Filtered: 2, Errors: 0, Deprecated: 2
```

**Note:** Services that exist locally but are no longer returned by the upstream API are automatically marked as deprecated (their `offering.json` status is set to `"deprecated"`). To sync this to the backend, run `usvc_seller data upload` - deprecated services with a `service_id` will update the server-side status to deprecated.

#### 7. Validate, Format, and Upload

```bash
usvc_seller data validate
usvc_seller data format

# Review changes
git diff
git add data/
git commit -m "Update service catalog from API"

# Upload
usvc_seller data upload
```

### Template Tips

**Conditional Fields:**
```jinja2
{%- if display_name %}
  "display_name": "{{ display_name }}",
{%- endif %}
```

**Iterating Over Details:**
```jinja2
"details": {
{%- for key, value in details.items() %}
    "{{ key }}": {{ value | tojson }}{{ "," if not loop.last else "" }}
{%- endfor %}
}
```

**Service Type Variations:**
```jinja2
{%- if service_type == 'image_generation' %}
    "file_path": "../../docs/image_example.py.j2"
{%- else %}
    "file_path": "../../docs/chat_example.py.j2"
{%- endif %}
```

**Default Values:**
```jinja2
"status": "{{ status | default('ready') }}"
"description": "{{ description | default('', true) }}"
```

### Filtering Models

Filter in the script itself — just skip models before calling
`render_and_write`:

```python
for model in fetch_models():
    if model.get("status") != "ready":
        continue
    if determine_service_type(model) != "llm":
        continue
    render_and_write(env, context["name"], build_context(model))
```

### Automation with CI/CD

Create `.github/workflows/update-services.yml`:

```yaml
name: Update Services

on:
    schedule:
        - cron: "0 0 * * *" # Daily at midnight
    workflow_dispatch:

jobs:
    update:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v3

            - name: Set up Python
              uses: actions/setup-python@v4
              with:
                  python-version: "3.11"

            - name: Install dependencies
              run: pip install unitysvc-sellers requests jinja2

            - name: Generate services from templates
              env:
                  MY_PROVIDER_API_KEY: ${{ secrets.MY_PROVIDER_API_KEY }}
              run: usvc_seller data populate

            - name: Validate
              run: usvc_seller data validate

            - name: Format
              run: usvc_seller data format

            - name: Commit changes
              run: |
                  git config user.name "GitHub Actions"
                  git config user.email "actions@github.com"
                  git add data/
                  git diff --staged --quiet || git commit -m "Update services from API"
                  git push

            - name: Upload to UnitySVC
              env:
                  UNITYSVC_API_URL: ${{ secrets.UNITYSVC_API_URL }}
                  UNITYSVC_SELLER_API_KEY: ${{ secrets.UNITYSVC_SELLER_API_KEY }}
              run: |
                  usvc_seller data upload --data-path ./data
```

### Summary: Template-Based Workflow

| Step | Action | Output |
|------|--------|--------|
| 1 | Create working service on unitysvc.com | Verified offering.json, listing.json |
| 2 | Export and save as .j2 templates | templates/offering.json.j2, listing.json.j2 |
| 3 | Replace variables with `{{ placeholders }}` | Parameterized templates |
| 4 | Write script that yields model dicts | scripts/update_services.py |
| 5 | Run `usvc_seller data populate` (which invokes the script) | services/{name}/offering.json, listing.json |

## Hybrid Workflow

Combine web interface and automated approaches:

1. Use automated populate for most services
2. Use web interface or manual files for special/custom services
3. Edit files directly to adjust individual services

```bash
# Generate bulk of services from provider API
usvc_seller data populate

# Create premium service via web interface and export, or create files manually
# Place in: data/my-provider/services/premium-service/

# Edit files directly to update status or other fields
# Then validate and upload
usvc_seller data validate
usvc_seller data upload
```

## Service Upload Lifecycle

Understanding how services are created and updated is essential for managing your catalog:

### First Upload: New Service Creation

When you upload a listing file for the **first time** (from a new repository or data directory):

1. **A new Service is always created** - even if the content is identical to an existing service
2. The Service ID is generated by the backend
3. **The SDK saves the `service_id`** to an override file (e.g., `listing.override.json`)

```bash
# First upload - creates a new service
$ usvc_seller data upload
  + Created service: my-service (provider: my-provider)
    Service ID: 550e8400-e29b-41d4-a716-446655440000
    → Saved to listing.override.json
```

### Override File Persistence

After the first successful publish, the override file contains the stable service identity and the backend-resolved service name:

```json
// listing.override.json (auto-generated)
{
    "service_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "gpt-4-enterprise"
}
```

The `name` field is the backend-resolved service name (`listing.name` if set, otherwise `offering.name`). It is saved as a valid `listing.name` field, so it feeds back into subsequent uploads. This provides an unambiguous reference when targeting services in promotion files.

**Best practices for override files:**

- **Commit to version control** - preserves service identity across team members
- **Don't manually edit** - the SDK manages this file
- **Keep per-environment** if deploying to staging/production separately

### Subsequent Uploads: Service Updates

On subsequent uploads, the SDK automatically loads the `service_id` from the override file:

```bash
# Subsequent upload - updates existing service
$ usvc_seller data upload
  ~ Updated service: my-service (provider: my-provider)
    Service ID: 550e8400-e29b-41d4-a716-446655440000
```

The Service ID remains stable, ensuring:

- Subscriptions continue to work
- Usage history is preserved
- Customers experience no disruption

### Uploading as New Service

To create a completely new service (ignoring existing `service_id`):

```bash
# Delete the override file
rm listing.override.json

# Upload creates a new service with a new ID
usvc_seller data upload
```

## Upload Order

**Recommended:** Use `usvc_seller data upload` to upload all types automatically in the correct order:

```mermaid
flowchart LR
    subgraph Step1["Step 1"]
        A[Sellers]
        B[Providers]
    end

    subgraph Step2["Step 2"]
        C[Service Offerings]
    end

    subgraph Step3["Step 3"]
        D[Service Listings]
    end

    A --> D
    B --> C
    C --> D

    style A fill:#e1f5fe
    style B fill:#e1f5fe
    style C fill:#fff3e0
    style D fill:#e8f5e9
```

1. **Sellers** - Must exist before listings
2. **Providers** - Must exist before offerings
3. **Service Offerings** - Links providers to services
4. **Service Listings** - Links sellers to offerings

The CLI handles this order automatically. Incorrect order will result in foreign key errors.

## Bulk Operations with --from-data

After running `usvc_seller data upload`, each listing file gets a `listing.override.json`
(or `.override.toml`) written alongside it containing the backend-assigned `service_id`.
The `--from-data` flag on all bulk service commands reads those IDs automatically, so you
don't have to copy-paste UUIDs from the upload output.

```bash
# Submit all services whose override files live under the current directory
usvc_seller services submit --from-data --yes

# Withdraw services for a specific provider only
usvc_seller services withdraw --from-data --provider acme --yes

# Submit services whose listing files are in a data/ subdirectory
usvc_seller services submit --from-data --data-dir data --yes

# Publish all active services in a data subdirectory
usvc_seller services publish --from-data --data-dir ./data --yes
```

### How it works

1. `--from-data` tells the command to scan for `listing_v1` files under `--data-dir`
   (default: current directory).
2. For each listing file found, the corresponding `*.override.*` file is merged in
   automatically. The `service_id` field from the merged result is collected.
3. Listings that have no `service_id` yet (i.e. not yet uploaded) are silently skipped.
4. `--provider NAME` filters the collected IDs to those whose listing contains a
   `provider_name` matching `NAME` (case-insensitive substring match).

### Typical CI/CD upload-and-submit pattern

```yaml
- name: Upload data
  env:
    UNITYSVC_SELLER_API_KEY: ${{ secrets.UNITYSVC_SELLER_API_KEY }}
    UNITYSVC_SELLER_API_URL: ${{ secrets.UNITYSVC_SELLER_API_URL }}
  run: usvc_seller data upload

- name: Commit back override files
  run: |
    git config user.name "GitHub Actions"
    git config user.email "actions@github.com"
    git add -A '*.override.*'
    git diff --staged --quiet || git commit -m "chore: update service override files [skip ci]"
    git push

- name: Submit for review
  env:
    UNITYSVC_SELLER_API_KEY: ${{ secrets.UNITYSVC_SELLER_API_KEY }}
    UNITYSVC_SELLER_API_URL: ${{ secrets.UNITYSVC_SELLER_API_URL }}
  run: usvc_seller services submit --from-data --data-dir data --yes
```

### Mutual exclusivity

`--from-data`, `--all`, and explicit service ID arguments are mutually exclusive.
Only one source may be active per invocation.

| Source | When to use |
|--------|-------------|
| Explicit IDs | You know the exact UUIDs |
| `--all` | Operate on all services in the seller account matching a status/visibility |
| `--from-data` | Operate on services whose listings live in the local data directory |

## Deleting Services

Use `usvc_seller services delete` to remove services from the backend:

```bash
# Preview what would be deleted
usvc_seller services delete <service-id> --dryrun

# Delete a service
usvc_seller services delete <service-id>

# Delete multiple services
usvc_seller services delete <service-id-1> <service-id-2>

# Force delete with active subscriptions (use with caution!)
usvc_seller services delete <service-id> --force --yes
```

### Integration with Version Control

After deleting services, update your local repository:

```bash
# Delete local files after removing from backend
rm -rf data/my-provider/deprecated-service/

# Commit the change
git add data/
git commit -m "Remove deprecated service from catalog"
git push
```

### Best Practices for Deleting Services

**Safety:**

- **Always dryrun first** - Preview impact before deleting
- **Check subscriptions** - Avoid force-deleting services with active users
- **Use version control** - Keep deleted files in git history

**Communication:**

- **Notify users** - Warn customers before removing services
- **Deprecation period** - Use `usvc_seller services deprecate` before deleting
- **Document reasons** - Log why services were removed

## Best Practices

### Version Control

- Commit generated files to git
- Review changes before uploading
- Use meaningful commit messages
- Tag releases

### Validation

- Always run `usvc_seller data validate` before `usvc_seller data upload`
- Fix all validation errors
- Use `usvc_seller data format --check` in CI to enforce formatting

### Environment Management

- Use different API keys for dev/staging/prod
- Store secrets in environment variables, not files

### Error Handling

- Check exit codes in scripts
- Log populate script output
- Retry failed publishes with exponential backoff

### Documentation

- Document custom populate scripts
- Keep README.md updated with service catalog
- Explain any special services or pricing

## Troubleshooting

### Populate Script Fails

- Check API credentials in `services_populator.envs`
- Verify script has execute permissions
- Test script manually: `python3 populate_services.py`

### Validation Errors After Populate

- Check generated file formats
- Verify all required fields are populated
- Ensure file paths are relative

### Upload Failures

- Verify credentials are set
- Check network connectivity
- Use `usvc_seller data upload` to handle upload order automatically
- Look for foreign key constraint errors
- Verify you're in the correct directory or using `--data-path`

## Next Steps

- [CLI Reference](cli-reference.md) - Detailed command documentation
- [Data Structure](data-structure.md) - File organization rules
- [File Schemas](file-schemas.md) - Schema specifications
