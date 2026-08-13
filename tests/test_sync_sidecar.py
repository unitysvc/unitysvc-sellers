"""Tests for ``_sync_sidecar`` — writing the canonical service_id back to
``service.json`` after a completed ingest (idempotent-upload self-heal)."""

import json
from pathlib import Path

from unitysvc_sellers.upload import _sync_sidecar


def _read(service_dir: Path) -> dict:
    return json.loads((service_dir / "service.json").read_text())


def test_revision_pins_canonical_id_not_the_revision_id(tmp_path: Path) -> None:
    # A revision result: service_id is the revision's own id; revision_of is the
    # canonical (original active) id. The sidecar must carry the canonical id so
    # the next upload targets the same service.
    _sync_sidecar(
        tmp_path,
        {"service_id": "rev-id", "revision_of": "orig-id", "status": "revision_created"},
    )
    assert _read(tmp_path)["service_id"] == "orig-id"


def test_non_revision_writes_the_returned_service_id(tmp_path: Path) -> None:
    _sync_sidecar(tmp_path, {"service_id": "svc-id", "revision_of": None, "status": "created"})
    assert _read(tmp_path)["service_id"] == "svc-id"


def test_empty_record_is_a_noop(tmp_path: Path) -> None:
    _sync_sidecar(tmp_path, {})
    assert not (tmp_path / "service.json").exists()


def test_diverged_sidecar_self_heals_to_canonical_id(tmp_path: Path) -> None:
    # A sidecar that had drifted to a stale/wrong id (parallel branch) is
    # corrected to the canonical id the backend resolved by (seller, name).
    (tmp_path / "service.json").write_text(json.dumps({"service_id": "stale-wrong-id"}) + "\n")
    _sync_sidecar(tmp_path, {"service_id": "rev-id", "revision_of": "orig-active-id"})
    assert _read(tmp_path)["service_id"] == "orig-active-id"
