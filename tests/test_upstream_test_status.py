"""Tests for the upstream connectivity-test gate on ``specs upload``.

``specs run-tests`` records the connectivity-test outcome in a service's
``service.json`` (round-tripped to the ``<name>.service.json`` sidecar for
param-file services), and ``specs upload`` refuses to publish a service whose
recorded outcome is ``fail`` unless ``--ignore-test-status`` is passed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from unitysvc_sellers.example import record_upstream_test_status
from unitysvc_sellers.upload import _upstream_test_blocked

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
        recorded = record_upstream_test_status(
            [_result("p/svc", listing, CONNECTIVITY, True, skipped=True)]
        )
        assert recorded == []
        assert json.loads((listing.parent / "service.json").read_text())["upstream_test_status"] == "pass"

    def test_service_without_connectivity_result_is_untouched(self, tmp_path: Path) -> None:
        listing = _listing(tmp_path)
        assert record_upstream_test_status([_result("p/svc", listing, "code_example", False)]) == []
        assert not (listing.parent / "service.json").exists()


class TestUploadGate:
    def test_blocks_on_recorded_failure(self, tmp_path: Path) -> None:
        listing = _listing(tmp_path)
        (listing.parent / "service.json").write_text(json.dumps({"upstream_test_status": "fail"}))
        reason = _upstream_test_blocked(listing)
        assert reason and "connectivity" in reason

    def test_allows_on_pass(self, tmp_path: Path) -> None:
        listing = _listing(tmp_path)
        (listing.parent / "service.json").write_text(json.dumps({"upstream_test_status": "pass"}))
        assert _upstream_test_blocked(listing) is None

    def test_never_tested_is_not_a_failure(self, tmp_path: Path) -> None:
        """A service that has never been tested locally must still upload."""
        listing = _listing(tmp_path)
        assert _upstream_test_blocked(listing) is None
        (listing.parent / "service.json").write_text(json.dumps({"service_id": "abc"}))
        assert _upstream_test_blocked(listing) is None

    def test_malformed_service_json_does_not_block(self, tmp_path: Path) -> None:
        listing = _listing(tmp_path)
        (listing.parent / "service.json").write_text("{not json")
        assert _upstream_test_blocked(listing) is None


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


class TestConnectivityFirst:
    """Connectivity probes must run before a service's other documents.

    Listing templates declare connectivity in arbitrary positions (8th of 9 in
    some), and the early-exit only helps once the probe has run.
    """

    @staticmethod
    def _doc(title: str, category: str):
        return ({"title": title, "category": category}, "prov", {})

    def test_connectivity_moves_to_front(self) -> None:
        from unitysvc_sellers.example import connectivity_first

        items = [
            self._doc("How to use", "getting_started"),
            self._doc("Python code example", "code_example"),
            self._doc("Connectivity test", "connectivity_test"),
            self._doc("cURL code example", "code_example"),
        ]
        assert [d[0]["title"] for d in connectivity_first(items)] == [
            "Connectivity test",
            "How to use",
            "Python code example",
            "cURL code example",
        ]

    def test_is_stable_for_everything_else(self) -> None:
        """Non-connectivity documents keep their declared order."""
        from unitysvc_sellers.example import connectivity_first

        items = [self._doc(f"doc{i}", "code_example") for i in range(5)]
        assert [d[0]["title"] for d in connectivity_first(items)] == [f"doc{i}" for i in range(5)]

    def test_no_connectivity_document_is_a_no_op(self) -> None:
        from unitysvc_sellers.example import connectivity_first

        items = [self._doc("a", "code_example"), self._doc("b", "getting_started")]
        assert [d[0]["title"] for d in connectivity_first(items)] == ["a", "b"]
