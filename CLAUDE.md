# CLAUDE.md — unitysvc-sellers

Seller-facing Python SDK + CLI for the UnitySVC platform. Lets sellers
manage services, promotions, groups, secrets, and documents via
`unitysvc_sellers.Client` (sync) / `AsyncClient` (async) or the
`usvc_seller` CLI.

## Key directories

| Path | Purpose |
|------|---------|
| `src/unitysvc_sellers/` | Package root — client, resources, CLI, utilities |
| `src/unitysvc_sellers/_generated/` | Auto-generated HTTP client from OpenAPI spec. **Do not edit by hand.** |
| `src/unitysvc_sellers/resources/` | Hand-written resource facades (services, tasks, secrets, etc.) |
| `scripts/` | Code-generation and doc-generation scripts |
| `docs/` | mkdocs site — tutorials (guides) and references |
| `openapi.json` | Committed snapshot of the seller OpenAPI spec (input for code gen + CI fingerprint check) |

## Commands

```bash
# Tests
uv run --extra test pytest tests/

# Linting
uv run --extra test ruff check src/ tests/

# Type checking
uv run --extra test mypy src/

# Build docs site
uv run --extra docs mkdocs build

# Serve docs locally
uv run --extra docs mkdocs serve
```

## Regeneration workflows

When the backend API changes, three things need updating:

### 1. Regenerate the HTTP client (from OpenAPI spec)

```bash
./scripts/generate_client.sh [path/to/seller_api.json]
```

- Copies the spec to `openapi.json`
- Runs `openapi-python-client generate` → `src/unitysvc_sellers/_generated/`
- Updates `src/unitysvc_sellers/_spec_version.py` (SHA256, version, timestamp)
- Default spec path: `../unitysvc/backend/generated/seller_api.json`

### 2. Regenerate the CLI reference

```bash
./scripts/generate_cli_reference.sh
```

- Uses `typer utils docs` to produce `docs/cli-reference.md`
- Must be re-run whenever CLI commands or options change

### 3. Update the SDK reference

`docs/sdk-reference.md` uses mkdocstrings directives — it auto-generates
from Python docstrings at `mkdocs build` time. When you add a new resource
class, add a `:::` block for it in `docs/sdk-reference.md`.

### After any API change, the full sequence is:

```bash
./scripts/generate_client.sh          # 1. regen HTTP client
# edit resources/ if the facade needs changes
./scripts/generate_cli_reference.sh   # 2. regen CLI reference
# add mkdocstrings entry in docs/sdk-reference.md if new resource
uv run --extra docs mkdocs build      # 3. verify docs build
uv run --extra test pytest tests/     # 4. verify tests pass
```

## Conventions

- `ruff` excludes `src/unitysvc_sellers/_generated/` (byte-stable codegen output)
- Docstring style: Google
- Python >= 3.11
- Package manager: uv
- CI verifies the SHA256 of `openapi.json` matches `_spec_version.py`

## Docs structure

- **`*-reference.md`** files are auto-generated or mkdocstrings-powered. They must match the implementation exactly.
- **`*-guide.md`** files are hand-written tutorials. They don't need updating with every API change.
