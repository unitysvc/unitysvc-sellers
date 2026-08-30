"""Tests for recording the local connectivity-test outcome.

``specs run-tests`` records the connectivity-test outcome in a service's
``service.json`` (round-tripped to the ``<name>.service.json`` sidecar for
param-file services). The value is advisory local feedback — it does NOT gate
``specs upload``; the platform's own ``check_service_tests_passed`` is the
authoritative gate, and it runs on gateway-side results.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from unitysvc_sellers.example import record_upstream_test_status

CONNECTIVITY = "connectivity_test"


def _result(service: str, listing: Path, category: str, success: bool, skipped: bool = False):
    return {
        "service_name": service,
        "category": category,
        "listing_file": str(listing),
        "result": {"success": success, "exit_code": 0 if success else 1, "skipped": skipped},
    }


def _listing(tmp_path: Path, name: str = "svc") -> Path:
    folder = tmp_path / name
    folder.mkdir(parents=True, exist_ok=True)
    listing = folder / "listing.json"
    listing.write_text("{}")
    return listing


class TestRecordUpstreamTestStatus:
    def test_records_pass_when_connectivity_succeeds(self, tmp_path: Path) -> None:
        listing = _listing(tmp_path)
        recorded = record_upstream_test_status([_result("p/svc", listing, CONNECTIVITY, True)])
        assert recorded == [("p/svc", "pass")]
        data = json.loads((listing.parent / "service.json").read_text())
        assert data["upstream_test_status"] == "pass"

    def test_records_fail_when_connectivity_fails(self, tmp_path: Path) -> None:
        listing = _listing(tmp_path)
        recorded = record_upstream_test_status([_result("p/svc", listing, CONNECTIVITY, False)])
        assert recorded == [("p/svc", "fail")]
        data = json.loads((listing.parent / "service.json").read_text())
        assert data["upstream_test_status"] == "fail"

    def test_preserves_existing_service_id(self, tmp_path: Path) -> None:
        listing = _listing(tmp_path)
        (listing.parent / "service.json").write_text(json.dumps({"service_id": "abc-123"}))
        record_upstream_test_status([_result("p/svc", listing, CONNECTIVITY, False)])
        data = json.loads((listing.parent / "service.json").read_text())
        assert data["service_id"] == "abc-123"
        assert data["upstream_test_status"] == "fail"

    def test_code_example_failure_does_not_block(self, tmp_path: Path) -> None:
        """A failing code example (missing SDK, per-doc rate limit) says nothing
        about whether the upstream can serve the model, so it must not be recorded."""
        listing = _listing(tmp_path)
        recorded = record_upstream_test_status(
            [
                _result("p/svc", listing, CONNECTIVITY, True),
                _result("p/svc", listing, "code_example", False),
            ]
        )
        assert recorded == [("p/svc", "pass")]
        assert json.loads((listing.parent / "service.json").read_text())["upstream_test_status"] == "pass"

    def test_skipped_connectivity_leaves_status_untouched(self, tmp_path: Path) -> None:
        listing = _listing(tmp_path)
        (listing.parent / "service.json").write_text(json.dumps({"upstream_test_status": "pass"}))
        recorded = record_upstream_test_status([_result("p/svc", listing, CONNECTIVITY, True, skipped=True)])
        assert recorded == []
        assert json.loads((listing.parent / "service.json").read_text())["upstream_test_status"] == "pass"

    def test_service_without_connectivity_result_is_untouched(self, tmp_path: Path) -> None:
        listing = _listing(tmp_path)
        assert record_upstream_test_status([_result("p/svc", listing, "code_example", False)]) == []
        assert not (listing.parent / "service.json").exists()


class TestCategoryResolution:
    """`--category` accepts a full name or an unambiguous prefix."""

    def test_exact_and_prefix(self) -> None:
        from unitysvc_sellers.example import _resolve_categories

        assert _resolve_categories(["connectivity_test"]) == {"connectivity_test"}
        assert _resolve_categories(["connectivity"]) == {"connectivity_test"}
        assert _resolve_categories(["CONNECTIVITY"]) == {"connectivity_test"}

    def test_repeatable(self) -> None:
        from unitysvc_sellers.example import _resolve_categories

        assert _resolve_categories(["connectivity", "request_template"]) == {
            "connectivity_test",
            "request_template",
        }

    def test_none_means_no_filter(self) -> None:
        from unitysvc_sellers.example import _resolve_categories

        assert _resolve_categories(None) is None
        assert _resolve_categories([]) is None

    def test_ambiguous_prefix_is_an_error(self) -> None:
        import typer

        from unitysvc_sellers.example import _resolve_categories

        # code_example and code_example_output both start with "code_example"
        with pytest.raises(typer.BadParameter, match="Ambiguous"):
            _resolve_categories(["code_exam"])

    def test_unknown_category_is_an_error(self) -> None:
        import typer

        from unitysvc_sellers.example import _resolve_categories

        with pytest.raises(typer.BadParameter, match="Unknown document category"):
            _resolve_categories(["nope"])


class TestLocalIdsUnaffected:
    """`-l` / `--local-ids` must cope with the sidecar shapes this feature adds.

    Recording `upstream_test_status` means a sidecar can now exist *without* a
    `service_id` (tested locally but never uploaded) — a shape that previously
    never occurred, since sidecars were only created by upload.
    """

    def test_status_only_sidecar_is_skipped_and_extra_key_ignored(self, tmp_path: Path) -> None:
        from unitysvc_sellers.utils import read_local_service_ids

        root = tmp_path / "specs" / "prov"
        root.mkdir(parents=True)
        # never uploaded, only tested — must not yield an id (and must not raise)
        (root / "never-uploaded.service.json").write_text(json.dumps({"upstream_test_status": "fail"}))
        # uploaded then tested — id still collected despite the extra key
        (root / "uploaded.service.json").write_text(
            json.dumps({"service_id": "abc-123", "upstream_test_status": "pass"})
        )
        # legacy id-only sidecar
        (root / "legacy.service.json").write_text(json.dumps({"service_id": "def-456"}))

        assert sorted(read_local_service_ids(tmp_path)) == ["abc-123", "def-456"]
