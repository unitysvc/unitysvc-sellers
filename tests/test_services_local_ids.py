"""Tests for ``--local-ids`` / ``--data-dir`` in ``usvc_seller services``.

Covers:
- ``_read_ids_from_data_dir``: collects service_id from each service folder's
  service.json; skips folders without one.
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
from unitysvc_sellers.utils import read_local_service_ids

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Fixed UUIDs used by the list-mode mocks (``_filter_ids_by_state`` casts the
# ``ids`` list through ``UUID(sid)`` before passing them to the SDK, so test
# fixtures must look like real UUIDs).
_UUID_A = "11111111-1111-1111-1111-111111111111"
_UUID_B = "22222222-2222-2222-2222-222222222222"


def _write_listing(path: Path, extra: dict | None = None) -> Path:
    """Write a minimal listing.json. A ``service_id`` in *extra* is recorded in
    the folder's service.json (flat specs/ layout), not in the listing."""
    extra = dict(extra or {})
    sid = extra.pop("service_id", None)
    prov = extra.pop("provider_name", None)
    data: dict = {"status": "ready", **extra}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    if sid is not None:
        (path.parent / "service.json").write_text(json.dumps({"service_id": sid}))
    if prov is not None:
        # Provider is a sibling in the flat layout; the filter reads its name.
        (path.parent / "provider.json").write_text(json.dumps({"name": prov}))
    return path


def _write_override(listing_path: Path, override: dict) -> Path:
    """Record a service_id (formerly stored in a listing override) into the
    folder's service.json beside the listing."""
    service_file = listing_path.parent / "service.json"
    data = json.loads(service_file.read_text()) if service_file.exists() else {}
    if override.get("service_id") is not None:
        data["service_id"] = override["service_id"]
    service_file.write_text(json.dumps(data))
    return service_file


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
    """The four selector modes (positional NAME, --id, --all, --local-ids)
    are mutually exclusive — exactly one must be active per invocation.
    """

    def _call(self, **kwargs) -> list[str]:
        defaults = dict(
            api_key=None,
            base_url="https://api.example.test",
            name=None,
            service_id=None,
            use_all=False,
            statuses_when_all=["draft"],
            provider=None,
            use_local_ids=False,
            data_dir=Path("."),
        )
        defaults.update(kwargs)
        return _resolve_or_fetch_ids(**defaults)

    def test_name_and_id_together_is_error(self, tmp_path: Path) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call(name="cohere/*", service_id="abc12345")
        assert exc.value.exit_code == 1

    def test_name_and_all_together_is_error(self, tmp_path: Path) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call(name="cohere/*", use_all=True)
        assert exc.value.exit_code == 1

    def test_id_and_local_ids_together_is_error(self, tmp_path: Path) -> None:
        _write_listing(tmp_path / "p" / "services" / "s" / "listing.json", {"service_id": "x"})
        with pytest.raises(typer.Exit) as exc:
            self._call(service_id="abc12345", use_local_ids=True, data_dir=tmp_path)
        assert exc.value.exit_code == 1

    def test_all_and_local_ids_together_is_error(self, tmp_path: Path) -> None:
        _write_listing(tmp_path / "p" / "services" / "s" / "listing.json", {"service_id": "x"})
        with pytest.raises(typer.Exit) as exc:
            self._call(use_all=True, use_local_ids=True, data_dir=tmp_path)
        assert exc.value.exit_code == 1

    def test_no_mode_is_error(self) -> None:
        """No selector at all is also an error — exactly one required."""
        with pytest.raises(typer.Exit) as exc:
            self._call()
        assert exc.value.exit_code == 1


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
            name=None,
            service_id=None,
            use_all=False,
            statuses_when_all=statuses_when_all or ["draft"],
            provider=provider,
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
    def test_fetches_services_listed_in_data_dir(self, tmp_path: Path, _runner: CliRunner, _env: None) -> None:
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
                json=_list_page(
                    [
                        _public_payload(_UUID_A, name="alpha"),
                        _public_payload(_UUID_B, name="beta"),
                    ]
                ),
            )
        )

        # ``--format json`` so assertions compare structured data instead
        # of Rich's table output, which gets auto-truncated to the
        # CliRunner's narrow default terminal width.
        result = _runner.invoke(
            _cli_app,
            [
                "services",
                "list",
                "--local-ids",
                "--data-dir",
                str(tmp_path),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0, result.stdout
        rendered = _json.loads(result.stdout)
        assert {svc["name"] for svc in rendered} == {"alpha", "beta"}
        # The request must scope by ids (not a wildcard list call).
        assert any("ids=" in str(call.request.url) for call in _respx.calls)

    @_respx.mock
    def test_empty_data_dir_prints_warning_and_exits_zero(self, tmp_path: Path, _runner: CliRunner, _env: None) -> None:
        result = _runner.invoke(
            _cli_app,
            ["services", "list", "--local-ids", "--data-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "No service IDs" in result.stdout

    @_respx.mock
    def test_status_filter_sent_to_backend(self, tmp_path: Path, _runner: CliRunner, _env: None) -> None:
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
                json=_list_page(
                    [
                        _public_payload(_UUID_A, name="alpha", status="active"),
                    ]
                ),
            )
        )

        result = _runner.invoke(
            _cli_app,
            [
                "services",
                "list",
                "--local-ids",
                "--data-dir",
                str(tmp_path),
                "--status",
                "active",
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0, result.stdout
        rendered = _json.loads(result.stdout)
        assert {svc["name"] for svc in rendered} == {"alpha"}
        assert any("status=active" in str(call.request.url) for call in _respx.calls)

    @_respx.mock
    def test_nonexistent_service_is_omitted_silently(self, tmp_path: Path, _runner: CliRunner, _env: None) -> None:
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
                json=_list_page(
                    [
                        _public_payload(_UUID_A, name="alpha"),
                    ]
                ),
            )
        )

        result = _runner.invoke(
            _cli_app,
            [
                "services",
                "list",
                "--local-ids",
                "--data-dir",
                str(tmp_path),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0, result.stdout
        rendered = _json.loads(result.stdout)
        assert {svc["name"] for svc in rendered} == {"alpha"}


# ---------------------------------------------------------------------------
# read_local_service_ids — the shared -l / --local-ids resolution utility
# ---------------------------------------------------------------------------


def test_read_local_service_ids_collects_from_service_json(tmp_path: Path) -> None:
    _write_listing(tmp_path / "a" / "listing.json", {"service_id": _UUID_A})
    _write_listing(tmp_path / "b" / "listing.json", {"service_id": _UUID_B})
    _write_listing(tmp_path / "c" / "listing.json")  # no service.json → skipped

    ids = read_local_service_ids(tmp_path)
    assert sorted(ids) == sorted([_UUID_A, _UUID_B])


def test_read_local_service_ids_filters_by_provider(tmp_path: Path) -> None:
    _write_listing(tmp_path / "a" / "listing.json", {"service_id": _UUID_A, "provider_name": "acme"})
    _write_listing(tmp_path / "b" / "listing.json", {"service_id": _UUID_B, "provider_name": "globex"})

    assert read_local_service_ids(tmp_path, provider="acme") == [_UUID_A]
    assert read_local_service_ids(tmp_path, provider="globex") == [_UUID_B]
    # Substring, case-insensitive — mirrors the existing services-command filter.
    assert sorted(read_local_service_ids(tmp_path, provider="")) == sorted([_UUID_A, _UUID_B])


def test_read_ids_from_data_dir_delegates_to_utility(tmp_path: Path) -> None:
    """The private services-module reader stays as a thin wrapper."""
    _write_listing(tmp_path / "a" / "listing.json", {"service_id": _UUID_A})
    assert _read_ids_from_data_dir(tmp_path) == [_UUID_A]


# ---------------------------------------------------------------------------
# read_local_service_ids — flat param layout (`<name>.service.json` sidecars)
# ---------------------------------------------------------------------------


def _write_flat_param(repo: Path, provider: str, name: str, service_id: str | None) -> None:
    """Flat param layout: a ``specs/<provider>/<name>.json`` param file plus the
    ``<name>.service.json`` sidecar that ``specs upload`` writes — no
    ``listing.json`` in the directory."""
    pdir = repo / "specs" / provider
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / f"{name}.json").write_text(json.dumps({"template": "t", "parameters": {}}))
    if service_id is not None:
        (pdir / f"{name}.service.json").write_text(json.dumps({"service_id": service_id}))


def test_read_local_service_ids_collects_flat_sidecars(tmp_path: Path) -> None:
    _write_flat_param(tmp_path, "labs", "discord-relay", _UUID_A)
    _write_flat_param(tmp_path, "labs", "msg-to-discord", _UUID_B)
    _write_flat_param(tmp_path, "labs", "not-uploaded", None)  # no sidecar → skipped
    assert sorted(read_local_service_ids(tmp_path)) == sorted([_UUID_A, _UUID_B])


def test_read_local_service_ids_flat_provider_from_path(tmp_path: Path) -> None:
    # No sibling provider.json in the param layout — provider comes from the
    # ``specs/<provider>/`` path segment.
    _write_flat_param(tmp_path, "labs", "discord-relay", _UUID_A)
    _write_flat_param(tmp_path, "acme", "thing", _UUID_B)
    assert read_local_service_ids(tmp_path, provider="labs") == [_UUID_A]
    assert read_local_service_ids(tmp_path, provider="acme") == [_UUID_B]


def test_read_local_service_ids_mixed_layouts(tmp_path: Path) -> None:
    # A folder-layout service and a flat-param service coexist; both surface once.
    _write_listing(tmp_path / "old" / "services" / "svc" / "listing.json", {"service_id": _UUID_A})
    _write_flat_param(tmp_path, "labs", "discord-relay", _UUID_B)
    assert sorted(read_local_service_ids(tmp_path)) == sorted([_UUID_A, _UUID_B])


def test_read_local_service_ids_deeply_nested_hierarchical_name(tmp_path: Path) -> None:
    # Hierarchical service name (parasail/Qwen/Qwen2.5-…) → a deeply-nested
    # `<name>.service.json` sidecar. The recursive walk finds it at any depth.
    sidecar = tmp_path / "specs" / "parasail" / "Qwen" / "Qwen2.5-Coder-7B-Instruct.service.json"
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(json.dumps({"service_id": _UUID_A}))
    assert read_local_service_ids(tmp_path) == [_UUID_A]
    # Provider is the segment right after `specs/`, not a nested name segment.
    assert read_local_service_ids(tmp_path, provider="parasail") == [_UUID_A]
    assert read_local_service_ids(tmp_path, provider="qwen") == []


def test_read_local_service_ids_bare_service_json_at_depth(tmp_path: Path) -> None:
    # A bare `service.json` with no sibling listing.json is still found by the
    # walk — the earlier listing_v1-anchored discovery missed exactly this.
    sidecar = tmp_path / "specs" / "acme" / "deep" / "svc" / "service.json"
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(json.dumps({"service_id": _UUID_B}))
    assert read_local_service_ids(tmp_path) == [_UUID_B]


def test_read_local_service_ids_mixed_sidecar_shapes_one_repo(tmp_path: Path) -> None:
    # Real repos (e.g. anthropic) carry both shapes side by side under one
    # provider dir: a bare `service.json` plus per-model `<name>.service.json`.
    pdir = tmp_path / "specs" / "anthropic"
    pdir.mkdir(parents=True)
    (pdir / "service.json").write_text(json.dumps({"service_id": _UUID_A}))
    (pdir / "claude-opus.service.json").write_text(json.dumps({"service_id": _UUID_B}))
    assert sorted(read_local_service_ids(tmp_path)) == sorted([_UUID_A, _UUID_B])
    assert sorted(read_local_service_ids(tmp_path, provider="anthropic")) == sorted([_UUID_A, _UUID_B])
