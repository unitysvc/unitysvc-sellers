"""Product-link check in ``specs run-tests`` (unitysvc/unitysvc#2873)."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

import httpx
import pytest
import typer
from typer.testing import CliRunner

from unitysvc_sellers import links as links_mod
from unitysvc_sellers.example import run_local
from unitysvc_sellers.links import check_link, offering_links


def _addr(ip: str) -> list[Any]:
    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", (ip, 443))]


@pytest.fixture
def public_dns(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Resolve every host to a public address unless the test maps it."""
    table: dict[str, str] = {}
    monkeypatch.setattr(links_mod.socket, "getaddrinfo", lambda host, *a, **k: _addr(table.get(host, "93.184.216.34")))
    return table


def _client(handler: Any) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False)


class TestCheckLink:
    def test_a_page_that_answers_is_reachable(self, public_dns: dict[str, str]) -> None:
        assert check_link("https://app.example", client=_client(lambda r: httpx.Response(200))) is None

    def test_an_error_status_is_unreachable(self, public_dns: dict[str, str]) -> None:
        assert check_link("https://app.example", client=_client(lambda r: httpx.Response(404))) == "HTTP 404"

    def test_redirects_are_followed_and_rechecked(self, public_dns: dict[str, str]) -> None:
        public_dns["internal.example"] = "10.0.0.5"

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.host == "app.example":
                return httpx.Response(302, headers={"location": "https://www.app.example/"})
            if request.url.host == "www.app.example":
                return httpx.Response(301, headers={"location": "https://internal.example/"})
            return httpx.Response(200)

        error = check_link("https://app.example", client=_client(handler))
        assert error is not None and "non-public address" in error

    def test_a_redirect_to_http_is_refused(self, public_dns: dict[str, str]) -> None:
        client = _client(lambda r: httpx.Response(302, headers={"location": "http://app.example/"}))
        assert check_link("https://app.example", client=client) == "not an https:// URL: http://app.example/"

    def test_redirect_loops_stop(self, public_dns: dict[str, str]) -> None:
        client = _client(lambda r: httpx.Response(302, headers={"location": "https://app.example/"}))
        assert check_link("https://app.example", client=client) == "more than 5 redirects"

    def test_a_timeout_is_unreachable(self, public_dns: dict[str, str]) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("slow", request=request)

        error = check_link("https://app.example", client=_client(handler))
        assert error is not None and error.startswith("no answer within")


def _service(root: Path, name: str, offering: dict[str, Any]) -> None:
    folder = root / "specs" / "acme" / name
    folder.mkdir(parents=True)
    (folder / "provider.json").write_text(json.dumps({"name": "acme"}))
    (folder / "offering.json").write_text(json.dumps({"name": name, **offering}))
    (folder / "listing.json").write_text(json.dumps({"name": f"acme/{name}"}))


class TestRunTests:
    @pytest.fixture
    def app(self) -> typer.Typer:
        app = typer.Typer()
        app.command()(run_local)
        return app

    def test_offering_links_reads_details_links(self, tmp_path: Path) -> None:
        _service(tmp_path, "site", {"details": {"links": {"homepage": "https://app.example"}}})
        assert offering_links(tmp_path / "specs" / "acme" / "site" / "listing.json") == {
            "homepage": "https://app.example"
        }

    def test_an_external_app_is_tested_by_its_links(
        self, app: typer.Typer, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _service(
            tmp_path, "site", {"details": {"links": {"homepage": "https://app.example", "docs": "https://d.example"}}}
        )
        checked: list[str] = []

        def fake_check(links: dict[str, str]) -> list[dict[str, Any]]:
            checked.extend(links.values())
            return [
                {"name": k, "url": v, "ok": k == "homepage", "error": None if k == "homepage" else "HTTP 404"}
                for k, v in links.items()
            ]

        monkeypatch.setattr("unitysvc_sellers.example.check_links", fake_check)
        monkeypatch.chdir(tmp_path)

        result = CliRunner().invoke(app, [])

        assert checked == ["https://app.example", "https://d.example"]
        assert "Product Links" in result.output and "HTTP 404" in result.output
        assert result.exit_code == 1
        assert not list(tmp_path.rglob("service.json")), "link results are never saved"

    def test_reachable_links_pass(self, app: typer.Typer, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _service(tmp_path, "site", {"details": {"links": {"homepage": "https://app.example"}}})
        monkeypatch.setattr(
            "unitysvc_sellers.example.check_links",
            lambda links: [{"name": k, "url": v, "ok": True, "error": None} for k, v in links.items()],
        )
        monkeypatch.chdir(tmp_path)

        result = CliRunner().invoke(app, [])

        assert result.exit_code == 0, result.output

    def test_skip_links(self, app: typer.Typer, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _service(tmp_path, "site", {"details": {"links": {"homepage": "https://app.example"}}})
        monkeypatch.setattr("unitysvc_sellers.example.check_links", lambda links: pytest.fail("checked"))
        monkeypatch.chdir(tmp_path)

        result = CliRunner().invoke(app, ["--skip-links"])

        assert result.exit_code == 0, result.output
