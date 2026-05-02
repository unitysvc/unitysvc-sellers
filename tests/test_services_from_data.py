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

import httpx as _httpx
import pytest
import respx as _respx
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
    """``--from-data`` reads ids from the data dir, then fetches each
    service and filters by ``statuses_when_all`` so the action runs only
    on services in the right starting state — same contract as ``--all``,
    just sourced from local data instead of a server-side list query.
    """

    _BASE = "https://api.example.test"

    def _setup_state(self, **id_to_status: str) -> None:
        """Mock ``GET /services/{id}`` responses with the given statuses."""
        for sid, status in id_to_status.items():
            _respx.get(f"{self._BASE}/services/{sid}").mock(
                return_value=_httpx.Response(
                    200,
                    json={
                        "service_id": sid,
                        "service_name": "svc",
                        "status": status,
                        "visibility": "public",
                        "documents": [],
                        "interfaces": [],
                    },
                )
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
            base_url=self._BASE,
            service_ids=None,
            use_all=False,
            statuses_when_all=statuses_when_all or ["draft"],
            provider=provider,
            flag_name="all",
            use_from_data=True,
            data_dir=data_dir,
        )

    @_respx.mock
    def test_ids_collected_from_listing_files(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "svc-001"},
        )
        self._setup_state(**{"svc-001": "draft"})
        assert self._call(tmp_path) == ["svc-001"]

    def test_empty_dir_exits_with_zero(self, tmp_path: Path) -> None:
        with pytest.raises(typer.Exit) as exc:
            self._call(tmp_path)
        assert exc.value.exit_code == 0

    @_respx.mock
    def test_provider_filter_keeps_matching(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "acme-001", "provider_name": "Acme Corp"},
        )
        _write_listing(
            tmp_path / "other" / "services" / "svc2" / "listing.json",
            {"service_id": "other-002", "provider_name": "Other Inc"},
        )
        self._setup_state(**{"acme-001": "draft", "other-002": "draft"})
        result = self._call(tmp_path, provider="acme")
        assert result == ["acme-001"]

    @_respx.mock
    def test_provider_filter_case_insensitive(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "acme-001", "provider_name": "ACME"},
        )
        self._setup_state(**{"acme-001": "draft"})
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

    @_respx.mock
    def test_service_id_from_override_is_included(self, tmp_path: Path) -> None:
        listing = _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"provider_name": "Acme Corp"},
        )
        _write_override(listing, {"service_id": "from-override"})
        self._setup_state(**{"from-override": "draft"})
        result = self._call(tmp_path)
        assert result == ["from-override"]

    @_respx.mock
    def test_status_filter_drops_ineligible_services(self, tmp_path: Path) -> None:
        """The whole point of mirroring ``--all``'s server-side filter
        on the client when ``--from-data`` is set: services in the
        wrong state get skipped instead of producing 400s downstream
        (e.g. ``submit --from-data`` against a repo that mixes
        ``draft`` and ``active`` services).
        """
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "drft-001"},
        )
        _write_listing(
            tmp_path / "acme" / "services" / "svc2" / "listing.json",
            {"service_id": "actv-002"},
        )
        self._setup_state(**{"drft-001": "draft", "actv-002": "active"})
        # ``submit`` allows draft → pending only.
        result = self._call(tmp_path, statuses_when_all=["draft", "rejected"])
        assert result == ["drft-001"]

    @_respx.mock
    def test_all_ids_filtered_out_exits_zero(self, tmp_path: Path) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "actv-001"},
        )
        self._setup_state(**{"actv-001": "active"})
        with pytest.raises(typer.Exit) as exc:
            self._call(tmp_path, statuses_when_all=["draft", "rejected"])
        assert exc.value.exit_code == 0


# ---------------------------------------------------------------------------
# CLI: ``services list --from-data``
# ---------------------------------------------------------------------------
import json as _json  # noqa: E402

from typer.testing import CliRunner  # noqa: E402

from unitysvc_sellers.cli import app as _cli_app  # noqa: E402

_BASE_URL = "https://seller.test.unitysvc"


def _detail_payload(service_id: str, **overrides) -> dict:
    """Build a ServiceDetailResponse-shaped payload for ``services.get`` mocks."""
    payload = {
        "service_id": service_id,
        "service_name": overrides.pop("name", "svc"),
        "status": overrides.pop("status", "active"),
        "visibility": overrides.pop("visibility", "public"),
        "provider_name": overrides.pop("provider_name", "acme"),
        "documents": [],
        "interfaces": [],
    }
    payload.update(overrides)
    return payload


@pytest.fixture
def _runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNITYSVC_SELLER_API_KEY", "svcpass_test")
    monkeypatch.setenv("UNITYSVC_SELLER_API_URL", _BASE_URL)


class TestListFromData:
    """``services list --from-data`` reads ids from the local data dir
    and fetches each via ``services.get`` rather than paging the seller's
    full catalog."""

    @_respx.mock
    def test_fetches_services_listed_in_data_dir(
        self, tmp_path: Path, _runner: CliRunner, _env: None
    ) -> None:
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "11111111-1111-1111-1111-111111111111"},
        )
        _write_listing(
            tmp_path / "acme" / "services" / "svc2" / "listing.json",
            {"service_id": "22222222-2222-2222-2222-222222222222"},
        )

        _respx.get(
            f"{_BASE_URL}/services/11111111-1111-1111-1111-111111111111"
        ).mock(
            return_value=_httpx.Response(
                200,
                json=_detail_payload(
                    "11111111-1111-1111-1111-111111111111", name="alpha"
                ),
            )
        )
        _respx.get(
            f"{_BASE_URL}/services/22222222-2222-2222-2222-222222222222"
        ).mock(
            return_value=_httpx.Response(
                200,
                json=_detail_payload(
                    "22222222-2222-2222-2222-222222222222", name="beta"
                ),
            )
        )

        # ``--format json`` so assertions compare structured data instead
        # of Rich's table output, which gets auto-truncated to the
        # CliRunner's narrow default terminal width.
        result = _runner.invoke(
            _cli_app,
            [
                "services", "list",
                "--from-data", "--data-dir", str(tmp_path),
                "--format", "json",
            ],
        )

        assert result.exit_code == 0, result.stdout
        rendered = _json.loads(result.stdout)
        assert {svc["service_name"] for svc in rendered} == {"alpha", "beta"}
        # The default seller catalog endpoint must NOT be hit — we're
        # explicitly scoping by the data dir, so a wildcard list call
        # would defeat the whole point of the flag.
        assert all(
            "/services?" not in str(call.request.url) and not str(call.request.url).endswith("/services")
            for call in _respx.calls
        )

    @_respx.mock
    def test_empty_data_dir_prints_warning_and_exits_zero(
        self, tmp_path: Path, _runner: CliRunner, _env: None
    ) -> None:
        result = _runner.invoke(
            _cli_app,
            ["services", "list", "--from-data", "--data-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "No service IDs" in result.stdout

    @_respx.mock
    def test_status_filter_applied_client_side(
        self, tmp_path: Path, _runner: CliRunner, _env: None
    ) -> None:
        """``--status`` post-filters fetched records when used with ``--from-data``.

        The backend ``services_list`` filter doesn't run in this mode (we
        fetch by id), so the CLI must apply it locally — otherwise
        ``--status active --from-data`` would silently ignore the filter.
        """
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "11111111-1111-1111-1111-111111111111"},
        )
        _write_listing(
            tmp_path / "acme" / "services" / "svc2" / "listing.json",
            {"service_id": "22222222-2222-2222-2222-222222222222"},
        )

        _respx.get(
            f"{_BASE_URL}/services/11111111-1111-1111-1111-111111111111"
        ).mock(
            return_value=_httpx.Response(
                200,
                json=_detail_payload(
                    "11111111-1111-1111-1111-111111111111",
                    name="alpha",
                    status="active",
                ),
            )
        )
        _respx.get(
            f"{_BASE_URL}/services/22222222-2222-2222-2222-222222222222"
        ).mock(
            return_value=_httpx.Response(
                200,
                json=_detail_payload(
                    "22222222-2222-2222-2222-222222222222",
                    name="beta",
                    status="draft",
                ),
            )
        )

        result = _runner.invoke(
            _cli_app,
            [
                "services", "list",
                "--from-data", "--data-dir", str(tmp_path),
                "--status", "active",
                "--format", "json",
            ],
        )

        assert result.exit_code == 0, result.stdout
        rendered = _json.loads(result.stdout)
        assert {svc["service_name"] for svc in rendered} == {"alpha"}

    @_respx.mock
    def test_missing_service_is_skipped_with_warning(
        self, tmp_path: Path, _runner: CliRunner, _env: None
    ) -> None:
        """A service id in the override file that no longer exists on the
        backend must not abort the whole listing — print a warning and
        carry on with the rest. This matters because override files
        outlive the services they reference (e.g. when a draft is
        deleted server-side but the local repo isn't pruned)."""
        _write_listing(
            tmp_path / "acme" / "services" / "svc1" / "listing.json",
            {"service_id": "11111111-1111-1111-1111-111111111111"},
        )
        _write_listing(
            tmp_path / "acme" / "services" / "svc2" / "listing.json",
            {"service_id": "22222222-2222-2222-2222-222222222222"},
        )

        _respx.get(
            f"{_BASE_URL}/services/11111111-1111-1111-1111-111111111111"
        ).mock(
            return_value=_httpx.Response(
                200,
                json=_detail_payload(
                    "11111111-1111-1111-1111-111111111111", name="alpha"
                ),
            )
        )
        _respx.get(
            f"{_BASE_URL}/services/22222222-2222-2222-2222-222222222222"
        ).mock(return_value=_httpx.Response(404, json={"detail": "Not found"}))

        result = _runner.invoke(
            _cli_app,
            [
                "services", "list",
                "--from-data", "--data-dir", str(tmp_path),
                "--format", "json",
            ],
        )

        assert result.exit_code == 0, result.stdout
        # The skip-warning is emitted on the Rich console (stdout under
        # the CliRunner) before the JSON payload — assert both:
        # the warning appears and the surviving service makes it into
        # the parsed JSON output.
        assert "could not fetch service" in result.stdout
        # JSON output is whatever follows the warning line.
        json_start = result.stdout.find("[")
        rendered = _json.loads(result.stdout[json_start:])
        assert {svc["service_name"] for svc in rendered} == {"alpha"}
