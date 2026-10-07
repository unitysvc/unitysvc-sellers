"""Tests for scripts/check_spec_sync.py (the backend spec drift check)."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_spec_sync", ROOT / "scripts" / "check_spec_sync.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check = _load()


def _spec() -> dict[str, Any]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "UnitySVC Seller API", "version": "1.0.0"},
        "paths": {
            "/services": {
                "get": {
                    "summary": "List Services",
                    "description": "List them.",
                    "operationId": "seller-services-list",
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
        "components": {
            "schemas": {
                "ServicePublic": {
                    "title": "ServicePublic",
                    "description": "A service.",
                    "type": "object",
                    "properties": {"description": {"type": "string", "title": "Description"}},
                }
            }
        },
    }


def _drift(committed: dict[str, Any], reference: dict[str, Any]) -> list[str]:
    return check.describe_drift(check.normalize(committed), check.normalize(reference))


def test_prose_and_version_changes_are_not_drift() -> None:
    reference = _spec()
    reference["info"]["version"] = "2.0.0"
    reference["paths"]["/services"]["get"]["description"] = "Reworded."
    reference["components"]["schemas"]["ServicePublic"]["description"] = "Reworded."

    assert _drift(_spec(), reference) == []


def test_property_named_description_is_not_stripped() -> None:
    reference = _spec()
    del reference["components"]["schemas"]["ServicePublic"]["properties"]["description"]

    assert _drift(_spec(), reference) == ["changed schema: ServicePublic"]


def test_missing_backend_path_is_drift() -> None:
    reference = _spec()
    reference["paths"]["/usage/cycle"] = {"get": {"operationId": "seller-get_cycle_usage", "responses": {}}}

    assert _drift(_spec(), reference) == ["missing operation: GET /usage/cycle"]


def test_title_change_is_drift() -> None:
    # Titles name the generated model classes, so they are part of the surface.
    reference = copy.deepcopy(_spec())
    reference["components"]["schemas"]["ServicePublic"]["properties"]["description"]["title"] = "Summary"

    assert _drift(_spec(), reference) == ["changed schema: ServicePublic"]


def test_main_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    committed = tmp_path / "openapi.json"
    reference = tmp_path / "seller_api.json"
    committed.write_text(json.dumps(_spec()))
    reference.write_text(json.dumps(_spec()))
    assert check.main([str(reference), "--spec", str(committed)]) == 0

    drifted = _spec()
    drifted["components"]["schemas"]["CycleUsageResponse"] = {"type": "object"}
    reference.write_text(json.dumps(drifted))
    assert check.main([str(reference), "--spec", str(committed)]) == 1
    assert "missing schema: CycleUsageResponse" in capsys.readouterr().out
