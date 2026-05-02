"""Tests for ``--local-ids`` / ``--data-dir`` in ``usvc_seller services``.

Covers:
- ``_read_ids_from_data_dir``: collects service_id from listing_v1 files,
  including via merged override files; skips listings without a service_id.
- ``_resolve_or_fetch_ids``: mutual exclusivity enforcement; --local-ids path;
  --provider filter in --local-ids mode; explicit-IDs path.
"""

from __future__ import annotations

import json
import json as _json
from pathlib import Path

import httpx as _httpx
import pytest
import respx as _respx
import typer
from typer.testing import CliRunner

from unitysvc_sellers.cli import app as _cli_app
from unitysvc_sellers.commands.services import _read_ids_from_data_dir, _resolve_or_fetch_ids

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Fixed UUIDs used by the list-mode mocks (``_filter_ids_by_state`` casts the
# ``ids`` list through ``UUID(sid)`` before passing them to the SDK, so test
# fixtures must look like real UUIDs).
_UUID_A = "11111111-1111-1111-1111-111111111111"
_UUID_B = "22222222-2222-2222-2222-222222222222"


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


def _list_page(items: list[dict], *, has_more: bool = False, next_cursor: str | None = None) -> dict:
    """Build a CursorPageServicePublic-shaped list response payload."""
    return {"data": items, "has_more": has_more, "next_cursor": next_cursor}


def _public_payload(service_id: str, **overrides) -> dict:
    """Build a ServicePublic-shaped payload for list endpoint mocks."""
    return {
        "id": service_id,
        "name": overrides.pop("name", "svc"),
        "status": overrides.pop("status", "active"),
        "visibility": overrides.pop("visibility", "public"),
        "provider_name": overrides.pop("provider_name", "acme"),
        "service_type": overrides.pop("service_type", "llm"),
        "display_name": None,
        "created_at": "2024-01-01T00:00:00Z",
        "seller_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "offering_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "listing_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        **overrides,
    }


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
            use_local_ids=False,
            data_dir=Path("."),
        )
        defaults.update(kwargs)
        return _resolve_or_fetch_ids(**defaults)

    def test_ids_and_all_together_is_error(self, tmp_path: Path) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call(service_ids=["abc-123"], use_all=True)
        assert exc.value.exit_code == 1

    def test_ids_and_local_ids_together_is_error(self, tmp_path: Path) -> None:
        _write_listing(tmp_path / "p" / "services" / "s" / "listing.json", {"service_id": "x"})
        with pytest.raises(typer.Exit) as exc:
            self._call(service_ids=["abc-123"], use_local_ids=True, data_dir=tmp_path)
        assert exc.value.exit_code == 1

    def test_all_and_local_ids_together_is_error(self, tmp_path: Path) -> None:
        _write_listing(tmp_path / "p" / "services" / "s" / "listing.json", {"service_id": "x"})
        with pytest.raises(typer.Exit) as exc:
            self._call(use_all=True, use_local_ids=True, data_dir=tmp_path)
        assert exc.value.exit_code == 1

    def test_no_mode_and_no_ids_is_error(self) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call()
        assert exc.value.exit_code == 1

    def test_provider_without_all_or_local_ids_is_error(self) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call(service_ids=["abc-123"], provider="acme")
        assert exc.value.exit_code == 1

    def test_explicit_ids_returned_directly(self) -> None:
        result = self._call(service_ids=["id-a", "id-b"])
        assert result == ["id-a", "id-b"]


# ---------------------------------------------------------------------------
# _resolve_or_fetch_ids — --local-ids path
# ---------------------------------------------------------------------------
#
# ``_filter_ids_by_state`` now resolves eligible ids via a single
# ``services.list(ids=...)`` call (the backend expands the filter to also
# include any service whose ``revision_of`` matches a requested id — see
# backend PR #915).  Status / visibility filtering is then applied
# client-side.  Tests mock the ``GET /services`` list endpoint accordingly.

_BASE = "https://api.example.test"


class TestResolveLocalIds:
    """``--local-ids`` reads ids from the data dir, then resolves them via
    the seller list endpoint (one round-trip, follows cursors)."""

    def _mock_list(self, *items: dict) -> None:
        _respx.get(f"{_BASE}/services").mock(
            return_value=_httpx.Response(200, json=_list_page(list(items))),
        )

    def _call(
        self,
        data_dir: Path,
        provider: str | None = None,
        *,
        statuses_when_all: list[str] | None = None,
    ) -> list[str]:
        return _resolve_or_fetch_ids(
            api_key="svcpass_test",
            base_url=_BASE,
            service_ids=None,
            use_all=False,
            statuses_when_all=statuses_when_all or ["draft"],
            provider=provider,
            flag_name="all",
            use_local_ids=True,
            data_dir=data_dir,
        )

    @_respx.mock
    def test_ids_collected_from_listing_files(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": _UUID_A},
        )
        self._mock_list(_public_payload(_UUID_A, status="draft"))
        assert self._call(tmp_path) == [_UUID_A]

    def test_empty_dir_exits_with_zero(self, tmp_path: Path) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call(tmp_path)
        assert exc.value.exit_code == 0

    @_respx.mock
    def test_provider_filter_keeps_matching(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": _UUID_A, "provider_name": "Acme Corp"},
        )
        _write_listing(
            tmp_path / "other" / "services" / "svc2" / "listing.json",
            {"service_id": _UUID_B, "provider_name": "Other Inc"},
        )
        # Only the acme id reaches the list call (provider filter trims locally).
        self._mock_list(_public_payload(_UUID_A, status="draft"))
        result = self._call(tmp_path, provider="acme")
        assert result == [_UUID_A]

    @_respx.mock
    def test_provider_filter_case_insensitive(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": _UUID_A, "provider_name": "ACME"},
        )
        self._mock_list(_public_payload(_UUID_A, status="draft"))
        result = self._call(tmp_path, provider="acme")
        assert result == [_UUID_A]

    def test_provider_filter_no_match_exits_zero(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": _UUID_A, "provider_name": "Acme Corp"},
        )
        with pytest.raises(typer.Exit) as exc:
            self._call(tmp_path, provider="nobody")
        assert exc.value.exit_code == 0

    @_respx.mock
    def test_service_id_from_override_is_included(self, tmp_path: Path) -> None:
        listing = _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"provider_name": "Acme Corp"},
        )
        _write_override(listing, {"service_id": _UUID_A})
        self._mock_list(_public_payload(_UUID_A, status="draft"))
        result = self._call(tmp_path)
        assert result == [_UUID_A]

    @_respx.mock
    def test_status_filter_drops_ineligible_services(self, tmp_path: Path) -> None:
        """``submit --local-ids`` allows draft → pending only.  When the
        list call returns both an ``active`` and a ``draft`` service, only
        the draft is eligible; the active one is silently filtered out."""
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": _UUID_A},
        )
        _write_listing(
            tmp_path / "acme" / "services" / "svc2" / "listing.json",
            {"service_id": _UUID_B},
        )
        self._mock_list(
            _public_payload(_UUID_A, status="draft"),
            _public_payload(_UUID_B, status="active"),
        )
        result = self._call(tmp_path, statuses_when_all=["draft", "rejected"])
        assert result == [_UUID_A]

    @_respx.mock
    def test_all_ids_filtered_out_exits_zero(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": _UUID_A},
        )
        self._mock_list(_public_payload(_UUID_A, status="active"))
        with pytest.raises(typer.Exit) as exc:
            self._call(tmp_path, statuses_when_all=["draft", "rejected"])
        assert exc.value.exit_code == 0


# ---------------------------------------------------------------------------
# CLI: ``services list --local-ids``
# ---------------------------------------------------------------------------

_BASE_URL = "https://seller.test.unitysvc"


@pytest.fixture
def _runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "svcpass_test")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", _BASE_URL)


class TestListLocalIds:
    """``services list --local-ids`` reads ids from the local data dir and
    calls ``GET /services?ids=...`` rather than paging the full catalog."""

    @_respx.mock
    def test_fetches_services_listed_in_data_dir(
        self, tmp_path: Path, _runner: CliRunner, _env: None
    ) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": _UUID_A},
        )
        _write_listing(
            tmp_path / "acme" / "services" / "svc2" / "listing.json",
            {"service_id": _UUID_B},
        )

        _respx.get(f"{_BASE_URL}/services").mock(
            return_value=_httpx.Response(
                200,
                json=_list_page([
                    _public_payload(_UUID_A, name="alpha"),
                    _public_payload(_UUID_B, name="beta"),
                ]),
            )
        )

        # ``--format json`` so assertions compare structured data instead
        # of Rich's table output, which gets auto-truncated to the
        # CliRunner's narrow default terminal width.
        result = _runner.invoke(
            _cli_app,
            [
                "services", "list",
                "--local-ids", "--data-dir", str(tmp_path),
                "--format", "json",
            ],
        )

        assert result.exit_code == 0, result.stdout
        rendered = _json.loads(result.stdout)
        assert {svc["name"] for svc in rendered} == {"alpha", "beta"}
        # The request must scope by ids (not a wildcard list call).
        assert any("ids=" in str(call.request.url) for call in _respx.calls)

    @_respx.mock
    def test_empty_data_dir_prints_warning_and_exits_zero(
        self, tmp_path: Path, _runner: CliRunner, _env: None
    ) -> None:
        result = _runner.invoke(
            _cli_app,
            ["services", "list", "--local-ids", "--data-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "No service IDs" in result.stdout

    @_respx.mock
    def test_status_filter_sent_to_backend(
        self, tmp_path: Path, _runner: CliRunner, _env: None
    ) -> None:
        """``--status`` is forwarded to the backend as a query param; the list
        endpoint returns only the matching services."""
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": _UUID_A},
        )
        _write_listing(
            tmp_path / "acme" / "services" / "svc2" / "listing.json",
            {"service_id": _UUID_B},
        )

        # Backend returns only the active service (as it would for ?status=active).
        _respx.get(f"{_BASE_URL}/services").mock(
            return_value=_httpx.Response(
                200,
                json=_list_page([
                    _public_payload(_UUID_A, name="alpha", status="active"),
                ]),
            )
        )

        result = _runner.invoke(
            _cli_app,
            [
                "services", "list",
                "--local-ids", "--data-dir", str(tmp_path),
                "--status", "active",
                "--format", "json",
            ],
        )

        assert result.exit_code == 0, result.stdout
        rendered = _json.loads(result.stdout)
        assert {svc["name"] for svc in rendered} == {"alpha"}
        assert any("status=active" in str(call.request.url) for call in _respx.calls)

    @_respx.mock
    def test_nonexistent_service_is_omitted_silently(
        self, tmp_path: Path, _runner: CliRunner, _env: None
    ) -> None:
        """A service id in the data dir that no longer exists on the backend
        is simply absent from the list response — no error or warning needed
        because the backend silently omits IDs it doesn't know about."""
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": _UUID_A},
        )
        _write_listing(
            tmp_path / "acme" / "services" / "svc2" / "listing.json",
            {"service_id": _UUID_B},
        )

        # Backend silently omits the second id (deleted / not found).
        _respx.get(f"{_BASE_URL}/services").mock(
            return_value=_httpx.Response(
                200,
                json=_list_page([
                    _public_payload(_UUID_A, name="alpha"),
                ]),
            )
        )

        result = _runner.invoke(
            _cli_app,
            [
                "services", "list",
                "--local-ids", "--data-dir", str(tmp_path),
                "--format", "json",
            ],
        )

        assert result.exit_code == 0, result.stdout
        rendered = _json.loads(result.stdout)
        assert {svc["name"] for svc in rendered} == {"alpha"}
