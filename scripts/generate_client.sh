#!/usr/bin/env bash
# Regenerate the low-level seller API client from the backend OpenAPI spec.
#
# Usage:
#     ./scripts/generate_client.sh [path/to/unitysvc]
#
# Defaults to ../unitysvc (sibling checkout). Dumps /v1/openapi.json from the
# backend, filters it to `tags: ["seller"]` operations, sanitizes schema
# names with characters that aren't valid Python identifiers, and
# regenerates src/unitysvc_sellers/_generated via openapi-python-client.
#
# Requirements:
#   - A checkout of unitysvc/unitysvc with backend/.venv provisioned
#     (cd backend && uv sync).
#   - openapi-python-client installed. If not on PATH, this script will
#     bootstrap it in .tool-venv/.
set -euo pipefail

UNITYSVC_DIR="${1:-../unitysvc}"
UNITYSVC_DIR="$(cd "$UNITYSVC_DIR" && pwd)"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# ---------------------------------------------------------------------------
# Tool bootstrap
# ---------------------------------------------------------------------------
if ! command -v openapi-python-client >/dev/null 2>&1; then
    if [ ! -x "$REPO_ROOT/.tool-venv/bin/openapi-python-client" ]; then
        echo "==> Bootstrapping openapi-python-client into .tool-venv"
        python3 -m venv "$REPO_ROOT/.tool-venv"
        "$REPO_ROOT/.tool-venv/bin/pip" install --quiet openapi-python-client
    fi
    OAPI_CLIENT="$REPO_ROOT/.tool-venv/bin/openapi-python-client"
else
    OAPI_CLIENT="$(command -v openapi-python-client)"
fi

# ---------------------------------------------------------------------------
# Dump + filter + sanitize the spec
# ---------------------------------------------------------------------------
echo "==> Dumping OpenAPI spec from $UNITYSVC_DIR"
cd "$UNITYSVC_DIR/backend"
.venv/bin/python "$REPO_ROOT/scripts/dump_spec.py" "$REPO_ROOT/openapi.json"

# ---------------------------------------------------------------------------
# Regenerate client
# ---------------------------------------------------------------------------
echo "==> Regenerating _generated/"
cd "$REPO_ROOT"
rm -rf src/unitysvc_sellers/_generated
"$OAPI_CLIENT" generate \
    --path openapi.json \
    --config scripts/openapi-python-client.yml \
    --meta none \
    --output-path src/unitysvc_sellers/_generated \
    --overwrite

echo "==> Done. Review the diff, run tests, and commit."
