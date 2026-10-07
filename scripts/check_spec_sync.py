#!/usr/bin/env python3
"""Fail when the committed ``openapi.json`` drifts from the backend's projection.

Usage::

    python scripts/check_spec_sync.py REFERENCE [--spec openapi.json]

``REFERENCE`` is the backend's per-role spec, i.e. ``backend/generated/
<role>_api.json`` from the unitysvc repo (CI fetches it from main; locally
point it at a sibling checkout). Both documents are compared after dropping
prose (``description``, ``summary``, ``example(s)``, ``externalDocs``) and the
``info`` block, so a reworded docstring or a version bump on the backend is not
drift. Titles are kept: openapi-python-client names model classes after them.

The fix for any reported drift is ``./scripts/generate_client.sh REFERENCE``.
Stdlib only, so CI can run it without installing the package (unitysvc#2536).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_PROSE_KEYS = frozenset({"description", "summary", "example", "examples", "externalDocs"})
# Keys whose value maps user-chosen names (property names, paths, status codes,
# media types) to nodes. Their keys are never treated as prose keywords.
_NAME_MAP_KEYS = frozenset(
    {
        "properties",
        "patternProperties",
        "schemas",
        "paths",
        "responses",
        "content",
        "headers",
        "securitySchemes",
        "encoding",
        "$defs",
        "definitions",
    }
)
_LITERAL_KEYS = frozenset({"default", "enum", "const"})
_HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


def _strip(node: Any, *, name_map: bool = False) -> Any:
    if isinstance(node, list):
        return [_strip(item) for item in node]
    if not isinstance(node, dict):
        return node
    out: dict[str, Any] = {}
    for key, value in node.items():
        if name_map:
            out[key] = _strip(value)
        elif key in _PROSE_KEYS:
            continue
        elif key in _LITERAL_KEYS:
            out[key] = value
        else:
            out[key] = _strip(value, name_map=key in _NAME_MAP_KEYS)
    return out


def normalize(spec: dict[str, Any]) -> dict[str, Any]:
    """Drop prose and ``info`` so only the generated-client surface remains."""
    return {
        "openapi": spec.get("openapi"),
        "paths": _strip(spec.get("paths", {}), name_map=True),
        "components": _strip(spec.get("components", {})),
    }


def _operations(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        f"{method.upper()} {path}": operation
        for path, item in spec.get("paths", {}).items()
        for method, operation in item.items()
        if method in _HTTP_METHODS
    }


def describe_drift(committed: dict[str, Any], reference: dict[str, Any]) -> list[str]:
    """List how ``committed`` differs from ``reference`` (both normalized)."""
    lines: list[str] = []

    def compare(kind: str, ours: dict[str, Any], theirs: dict[str, Any]) -> None:
        for name in sorted(set(theirs) - set(ours)):
            lines.append(f"missing {kind}: {name}")
        for name in sorted(set(ours) - set(theirs)):
            lines.append(f"extra {kind} (gone from the backend): {name}")
        for name in sorted(set(ours) & set(theirs)):
            if ours[name] != theirs[name]:
                lines.append(f"changed {kind}: {name}")

    compare("operation", _operations(committed), _operations(reference))
    compare(
        "schema",
        committed.get("components", {}).get("schemas", {}),
        reference.get("components", {}).get("schemas", {}),
    )
    if not lines and committed != reference:
        lines.append("other differences (path parameters, security schemes, ...)")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("reference", type=Path, help="backend generated/<role>_api.json")
    parser.add_argument("--spec", type=Path, default=Path("openapi.json"))
    args = parser.parse_args(argv)

    committed = normalize(json.loads(args.spec.read_text()))
    reference = normalize(json.loads(args.reference.read_text()))
    drift = describe_drift(committed, reference)
    if not drift:
        print(f"{args.spec} matches the backend projection.")
        return 0

    print(f"{args.spec} has drifted from the backend projection ({args.reference}):")
    for line in drift:
        print(f"  - {line}")
    print(f"\nRegenerate: ./scripts/generate_client.sh {args.reference}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
