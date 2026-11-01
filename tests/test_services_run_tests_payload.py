"""Tests for ``_parse_run_tests_payload`` — the task-payload → typed-result coercion.

Pins the per-channel breakdown (#1281/#1297): the diagnostic probes each
upstream access channel, so a failing row carries ``upstream_channels`` keyed
by channel name alongside the back-compat singleton ``upstream``.
"""

from __future__ import annotations

from unitysvc_sellers.services import _parse_run_tests_payload


def test_parses_upstream_channels_per_row() -> None:
    payload = {
        "status": "success",
        "result": {
            "service_id": "svc-1",
            "status": "failure",
            "success_count": 0,
            "fail_count": 1,
            "skipped_count": 0,
            "results": [
                {
                    "document_id": "doc-1",
                    "interface_name": "default",
                    "status": "script_failed",
                    "outcome": "upstream_fault",
                    "upstream": {"status": "script_failed"},
                    "upstream_channels": {
                        "http_relay": {"status": "success"},
                        "plus": {"status": "script_failed"},
                    },
                }
            ],
        },
    }

    result = _parse_run_tests_payload("task-1", payload)

    assert len(result.results) == 1
    row = result.results[0]
    assert row.upstream == {"status": "script_failed"}
    assert row.upstream_channels == {
        "http_relay": {"status": "success"},
        "plus": {"status": "script_failed"},
    }


def test_upstream_channels_absent_is_none() -> None:
    payload = {
        "status": "success",
        "result": {
            "service_id": "svc-1",
            "status": "success",
            "results": [{"document_id": "doc-1", "status": "success"}],
        },
    }

    row = _parse_run_tests_payload("task-1", payload).results[0]
    assert row.upstream_channels is None


def _links_payload(links: list[dict[str, object]]) -> dict[str, object]:
    return {
        "status": "success",
        "result": {
            "service_id": "svc-1",
            "status": "success",
            "outcome": "no_executable_documents",
            "results": [],
            "links": links,
        },
    }


def test_parses_product_link_checks() -> None:
    result = _parse_run_tests_payload(
        "task-1",
        _links_payload(
            [
                {"name": "homepage", "url": "https://app.example", "ok": True, "error": None},
                {"name": "docs", "url": "https://app.example/docs", "ok": False, "error": "HTTP 404"},
            ]
        ),
    )

    assert [(link.name, link.ok, link.error) for link in result.links] == [
        ("homepage", True, None),
        ("docs", False, "HTTP 404"),
    ]
    assert not result.passed, "an unreachable link fails the run"


def test_reachable_links_pass_and_links_are_optional() -> None:
    ok = _parse_run_tests_payload(
        "task-1", _links_payload([{"name": "homepage", "url": "https://app.example", "ok": True}])
    )
    assert ok.passed

    payload = _links_payload([])
    del payload["result"]["links"]  # type: ignore[index]
    assert _parse_run_tests_payload("task-1", payload).links == []


def test_cli_renders_links_and_fails_on_a_dead_one(capsys: object) -> None:
    from unitysvc_sellers.commands.tests import _render_run_tests_result

    result = _parse_run_tests_payload(
        "task-1",
        _links_payload([{"name": "homepage", "url": "https://app.example", "ok": False, "error": "HTTP 503"}]),
    )

    assert _render_run_tests_result(result) == 1
