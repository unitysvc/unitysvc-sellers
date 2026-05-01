"""Tests for ``--from-data`` / ``--data-dir`` in ``usvc_seller services``.

Covers:
- ``_read_ids_from_data_dir``: collects service_id from listing_v1 files,
  including via merged override files; skips listings without a service_id.
- ``_resolve_or_fetch_ids``: mutual exclusivity enforcement; --from-data path;
  --provider filter in --from-data mode; explicit-IDs path.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import typer

from unitysvc_sellers.commands.services import _read_ids_from_data_dir, _resolve_or_fetch_ids

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_listing(path: Path, extra: dict | None = None) -> Path:
    """Write a minimal listing_v1 JSON file, with optional extra fields."""
    data: dict = {"schema": "listing_v1", "status": "ready"}
    if extra:
        data.update(extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return path


def _write_override(listing_path: Path, override: dict) -> Path:
    """Write a <stem>.override.<ext> alongside the listing file."""
    stem = listing_path.stem
    suffix = listing_path.suffix
    override_path = listing_path.with_name(f"{stem}.override{suffix}")
    override_path.write_text(json.dumps(override))
    return override_path


# ---------------------------------------------------------------------------
# _read_ids_from_data_dir
# ---------------------------------------------------------------------------

class TestReadIdsFromDataDir:
    def test_single_listing_with_inline_service_id(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "aaa-111"},
        )
        assert _read_ids_from_data_dir(tmp_path) == ["aaa-111"]

    def test_service_id_from_override_file(self, tmp_path: Path) -> None:
        listing = _write_listing(tmp_path / "acme" / "services" / "svc1" / "listing.json")
        _write_override(listing, {"service_id": "bbb-222"})
        assert _read_ids_from_data_dir(tmp_path) == ["bbb-222"]

    def test_listing_without_service_id_skipped(self, tmp_path: Path) -> None:
        _write_listing(tmp_path / "acme" / "services" / "svc1" / "listing.json")
        assert _read_ids_from_data_dir(tmp_path) == []

    def test_multiple_listings_all_ids_collected(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "id-1"},
        )
        listing2 = _write_listing(tmp_path / "acme" / "services" / "svc2" / "listing.json")
        _write_override(listing2, {"service_id": "id-2"})
        _write_listing(tmp_path / "acme" / "services" / "svc3" / "listing.json")

        ids = _read_ids_from_data_dir(tmp_path)
        assert sorted(ids) == ["id-1", "id-2"]

    def test_empty_directory_returns_empty(self, tmp_path: Path) -> None:
        assert _read_ids_from_data_dir(tmp_path) == []


# ---------------------------------------------------------------------------
# _resolve_or_fetch_ids — mutual exclusivity
# ---------------------------------------------------------------------------

class TestMutualExclusivity:
    def _call(self, **kwargs) -> list[str]:
        defaults = dict(
            api_key=None,
            base_url="https://api.example.test",
            service_ids=None,
            use_all=False,
            statuses_when_all=["draft"],
            provider=None,
            flag_name="all",
            use_from_data=False,
            data_dir=Path("."),
        )
        defaults.update(kwargs)
        return _resolve_or_fetch_ids(**defaults)

    def test_ids_and_all_together_is_error(self, tmp_path: Path) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call(service_ids=["abc-123"], use_all=True)
        assert exc.value.exit_code == 1

    def test_ids_and_from_data_together_is_error(self, tmp_path: Path) -> None:
        _write_listing(tmp_path / "p" / "services" / "s" / "listing.json", {"service_id": "x"})
        with pytest.raises(typer.Exit) as exc:
            self._call(service_ids=["abc-123"], use_from_data=True, data_dir=tmp_path)
        assert exc.value.exit_code == 1

    def test_all_and_from_data_together_is_error(self, tmp_path: Path) -> None:
        _write_listing(tmp_path / "p" / "services" / "s" / "listing.json", {"service_id": "x"})
        with pytest.raises(typer.Exit) as exc:
            self._call(use_all=True, use_from_data=True, data_dir=tmp_path)
        assert exc.value.exit_code == 1

    def test_no_mode_and_no_ids_is_error(self) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call()
        assert exc.value.exit_code == 1

    def test_provider_without_all_or_from_data_is_error(self) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call(service_ids=["abc-123"], provider="acme")
        assert exc.value.exit_code == 1

    def test_explicit_ids_returned_directly(self) -> None:
        result = self._call(service_ids=["id-a", "id-b"])
        assert result == ["id-a", "id-b"]


# ---------------------------------------------------------------------------
# _resolve_or_fetch_ids — --from-data path
# ---------------------------------------------------------------------------

class TestResolveFromData:
    def _call(self, data_dir: Path, provider: str | None = None) -> list[str]:
        return _resolve_or_fetch_ids(
            api_key=None,
            base_url="https://api.example.test",
            service_ids=None,
            use_all=False,
            statuses_when_all=["draft"],
            provider=provider,
            flag_name="all",
            use_from_data=True,
            data_dir=data_dir,
        )

    def test_ids_collected_from_listing_files(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "svc-001"},
        )
        assert self._call(tmp_path) == ["svc-001"]

    def test_empty_dir_exits_with_zero(self, tmp_path: Path) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call(tmp_path)
        assert exc.value.exit_code == 0

    def test_provider_filter_keeps_matching(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "acme-001", "provider_name": "Acme Corp"},
        )
        _write_listing(
            tmp_path / "other" / "services" / "svc2" / "listing.json",
            {"service_id": "other-002", "provider_name": "Other Inc"},
        )
        result = self._call(tmp_path, provider="acme")
        assert result == ["acme-001"]

    def test_provider_filter_case_insensitive(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "acme-001", "provider_name": "ACME"},
        )
        result = self._call(tmp_path, provider="acme")
        assert result == ["acme-001"]

    def test_provider_filter_no_match_exits_zero(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "acme-001", "provider_name": "Acme Corp"},
        )
        with pytest.raises(typer.Exit) as exc:
            self._call(tmp_path, provider="nobody")
        assert exc.value.exit_code == 0

    def test_service_id_from_override_is_included(self, tmp_path: Path) -> None:
        listing = _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"provider_name": "Acme Corp"},
        )
        _write_override(listing, {"service_id": "from-override"})
        result = self._call(tmp_path)
        assert result == ["from-override"]
